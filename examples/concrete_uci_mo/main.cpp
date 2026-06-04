// Worked example — IDC on UCI Concrete, multi-objective (paper Section 8.5).
//
// Loads the trained OpenNN strength surrogate (8 mix inputs -> 28-day
// compressive strength), declares the six EN 206 / ASTM C595 affine
// constraints from problem.yaml, and runs multi-objective IDC to trade off
// max strength vs min cement (cement is a passthrough on its input variable).
// Writes result.csv with the recovered Pareto front.
//
// The paper's Section 8.5 trains the surrogate on the age-28 slice of the Yeh
// dataset; this worked example ships the Growing-Neurons surrogate and
// demonstrates the MO pipeline. Paths resolve relative to EXAMPLE_DIR.

#include <chrono>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <utility>
#include <vector>

#include "standard_networks.h"
#include "bounding_layer.h"
#include "response_optimization.h"
#include "random_utilities.h"

#include "yaml_constraints.h"

using namespace opennn;
using type = float;
namespace fs = std::filesystem;

#ifndef EXAMPLE_DIR
#define EXAMPLE_DIR "."
#endif

int main()
{
    try
    {
        const fs::path dir        = EXAMPLE_DIR;
        const fs::path nn_json    = dir / "nn" / "concrete_uci.json";
        const fs::path yaml_path  = dir / "problem.yaml";
        const fs::path result_csv = dir / "result.csv";

        // Surrogate architecture: 8 inputs -> 52 hidden -> 1 output (strength).
        ApproximationNetwork network({Index(8)}, Shape{Index(52)}, {Index(1)});
        if(auto* b = dynamic_cast<Bounding*>(network.get_first("Bounding")))
            b->set_bounding_method("NoBounding");
        if(!fs::exists(nn_json))
            throw std::runtime_error("NN JSON missing: " + nn_json.string());
        network.load(nn_json.string());

        {
            auto vars_in = network.get_input_variables();
            for(auto& v : vars_in) v.set_role("Input");
            network.set_input_variables(vars_in);
            auto vars_out = network.get_output_variables();
            for(auto& v : vars_out) v.set_role("Target");
            network.set_output_variables(vars_out);
        }

        opennn::set_seed(0);
        ResponseOptimization opt(&network);

        // Input bounds (training-data envelope; age locked at 28 days).
        static const std::vector<std::pair<std::string, std::pair<type, type>>> BOUNDS = {
            {"cement",     { 102.0f, 540.0f}}, {"slag",       {   0.0f, 360.0f}},
            {"fly_ash",    {   0.0f, 200.0f}}, {"water",      { 122.0f, 247.0f}},
            {"sp",         {   0.0f,  32.0f}}, {"coarse_agg", { 801.0f, 1145.0f}},
            {"fine_agg",   { 594.0f, 992.0f}}, {"age",        {  28.0f,  28.0f}},
        };
        for(const auto& [name, bnd] : BOUNDS)
            opt.set_condition(name, ResponseOptimization::ConditionType::Between, bnd.first, bnd.second);
        opt.set_condition("strength", ResponseOptimization::ConditionType::Maximize);
        opt.set_condition("cement",   ResponseOptimization::ConditionType::Minimize);  // passthrough

        // Six EN 206 / ASTM C595 affine constraints from the YAML.
        opennn_idc::apply_yaml_constraints(opt, yaml_path);

        // Paper-default IDC configuration (Section 8.1).
        opt.set_evaluations_number(2000);
        opt.set_iterations(20);
        opt.set_zoom_factor(0.85f);
        opt.set_relative_tolerance(1e-6f);
        opt.set_max_pareto_number(10000);   // empirical-front cap (safety bound)

        const auto t0 = std::chrono::high_resolution_clock::now();
        MatrixR results = opt.perform_response_optimization();
        const double walltime =
            std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - t0).count();

        const Index n_pareto = results.rows();
        if(n_pareto == 0)
            throw std::runtime_error("IDC returned an empty Pareto front.");

        // Each row is a Pareto point. Columns: [x_0..x_7, strength].
        // cement objective = the cement input column (x_0).
        std::ofstream f(result_csv);
        f << std::setprecision(9)
          << "strength,cement,x_cement,x_slag,x_fly_ash,x_water,x_sp,x_coarse_agg,x_fine_agg,x_age\n";
        for(Index r = 0; r < n_pareto; ++r)
        {
            f << results(r, 8) << "," << results(r, 0);
            for(Index i = 0; i < 8; ++i) f << "," << results(r, i);
            f << "\n";
        }

        std::cout << "[OK] Pareto front of " << n_pareto << " points  ("
                  << walltime << " s)  ->  " << result_csv << std::endl;
        return 0;
    }
    catch(const std::exception& e)
    {
        std::cerr << "[ERROR] " << e.what() << std::endl;
        return 1;
    }
}
