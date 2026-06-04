// Worked example — IDC on MOEED13 economic-emission dispatch (paper Section 8.3).
//
// Loads the trained 2-output OpenNN surrogate (13 generator setpoints -> total
// cost, total NOx emission), declares the per-unit bounds and the
// power-balance constraint from problem.yaml, and runs multi-objective IDC to
// recover the cost/emission Pareto front. Writes result.csv.
//
// Two constraint formulations are shipped (paper Section 8.3):
//   * default (no argument): the EQUALITY formulation sum(P_i) == 1800 MW,
//     read from EXAMPLE_DIR/problem.yaml, written to EXAMPLE_DIR/result.csv.
//   * argv[1] == "band": the tolerance-BAND formulation 1800 +/- 0.5 MW, read
//     from EXAMPLE_DIR/band/problem.yaml, written to EXAMPLE_DIR/band/result.csv.
// The surrogate (nn/) is shared by both. Paths resolve relative to EXAMPLE_DIR
// (set by CMake).

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

int main(int argc, char** argv)
{
    try
    {
        const fs::path dir        = EXAMPLE_DIR;
        // Formulation: "" (default) = equality at top level; "band" = band/ subdir.
        const std::string form    = (argc > 1) ? argv[1] : "";
        const fs::path form_dir   = form.empty() ? dir : dir / form;
        const fs::path nn_json    = dir / "nn" / "moeed13.json";   // shared surrogate
        const fs::path yaml_path  = form_dir / "problem.yaml";
        const fs::path result_csv = form_dir / "result.csv";

        // The true architecture (13 inputs -> hidden -> 2 outputs) is restored
        // by load(); the placeholder dimensions are overwritten.
        ApproximationNetwork network({Index(1)}, Shape{Index(1)}, {Index(2)});
        if(auto* b = dynamic_cast<Bounding*>(network.get_first("Bounding")))
            b->set_bounding_method("NoBounding");
        if(!fs::exists(nn_json))
            throw std::runtime_error("NN JSON missing: " + nn_json.string());
        network.load(nn_json.string());
        if(auto* b2 = dynamic_cast<Bounding*>(network.get_first("Bounding")))
            b2->set_bounding_method("NoBounding");

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

        // Per-unit power bounds (Walters-Sheble 1993 Table I).
        static const std::vector<std::pair<std::string, std::pair<type, type>>> BOUNDS = {
            {"P_0",  {  0.0f, 680.0f}}, {"P_1",  {  0.0f, 360.0f}}, {"P_2",  {  0.0f, 360.0f}},
            {"P_3",  { 60.0f, 180.0f}}, {"P_4",  { 60.0f, 180.0f}}, {"P_5",  { 60.0f, 180.0f}},
            {"P_6",  { 60.0f, 180.0f}}, {"P_7",  { 60.0f, 180.0f}}, {"P_8",  { 60.0f, 180.0f}},
            {"P_9",  { 40.0f, 120.0f}}, {"P_10", { 40.0f, 120.0f}},
            {"P_11", { 55.0f, 120.0f}}, {"P_12", { 55.0f, 120.0f}},
        };
        for(const auto& [name, bnd] : BOUNDS)
            opt.set_condition(name, ResponseOptimization::ConditionType::Between, bnd.first, bnd.second);
        opt.set_condition("total_cost",     ResponseOptimization::ConditionType::Minimize);
        opt.set_condition("total_emission", ResponseOptimization::ConditionType::Minimize);

        // Power-balance equality (|sum P_i - D| <= 0.5 MW) from the YAML.
        opennn_idc::apply_yaml_constraints(opt, yaml_path);

        // Matched-budget study (Section 8.3). IDC and the pymoo baselines are
        // both held to the same TOTAL surrogate-evaluation budget. Per-point
        // sampling is reduced 2000 -> 200 so IDC can refine over ~10 iterations
        // within the budget instead of a few coarse ones, and the total is
        // hard-capped so the count matches the baselines' budget exactly.
        opt.set_evaluations_number(200);
        opt.set_iterations(20);
        opt.set_max_total_evaluations(400000);
        // Initial full-domain pass draws 10x the per-point sample count for a
        // broader seed; the extra cost counts against the 400k matched cap.
        opt.set_initial_sampling_factor(10);
        opt.set_zoom_factor(0.85f);
        opt.set_relative_tolerance(1e-6f);

        const auto t0 = std::chrono::high_resolution_clock::now();
        MatrixR results = opt.perform_response_optimization();
        const double walltime =
            std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - t0).count();

        const Index n_pareto = results.rows();
        if(n_pareto == 0)
            throw std::runtime_error("IDC returned an empty Pareto front.");

        // Each row: [x_0..x_12, total_cost (col 13), total_emission (col 14)].
        std::ofstream f(result_csv);
        // 17 significant digits = exact IEEE-double round-trip, so the written
        // setpoints re-check against the power-balance constraint to machine
        // precision (used by benchmarks/baselines/run_baselines.py).
        f << std::setprecision(17) << "total_cost,total_emission";
        for(int i = 0; i < 13; ++i) f << ",P_" << i;
        f << "\n";
        for(Index r = 0; r < n_pareto; ++r)
        {
            f << results(r, 13) << "," << results(r, 14);
            for(Index i = 0; i < 13; ++i) f << "," << results(r, i);
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
