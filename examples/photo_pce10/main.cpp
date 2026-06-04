// Worked example — IDC on the Olympus photo_pce10 OPV task (paper Section 8.4).
//
// Loads the trained OpenNN surrogate (4 mass fractions -> photo-degradation),
// declares the simplex + donor-band constraints from problem.yaml, runs
// single-objective Iterative Domain Contraction, and writes result.csv with the
// recommended blend and its predicted degradation.
//
// Adapted from the authors' working driver; paths are resolved relative to the
// example directory (EXAMPLE_DIR, set by CMake) so it runs from any build tree.

#include <chrono>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>

#include "standard_networks.h"
#include "bounding_layer.h"
#include "response_optimization.h"
#include "random_utilities.h"

#include "yaml_constraints.h"   // examples/common/

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
        const fs::path nn_json    = dir / "nn" / "photo_pce10.json";
        const fs::path yaml_path  = dir / "problem.yaml";
        const fs::path result_csv = dir / "result.csv";

        // Surrogate architecture: 4 inputs -> 15 hidden -> 1 output (degradation).
        ApproximationNetwork network({Index(4)}, Shape{Index(15)}, {Index(1)});
        if(auto* b = dynamic_cast<Bounding*>(network.get_first("Bounding")))
            b->set_bounding_method("NoBounding");
        if(!fs::exists(nn_json))
            throw std::runtime_error("NN JSON missing: " + nn_json.string());
        network.load(nn_json.string());

        // The OpenNN JSON schema persists variable names but not roles;
        // ResponseOptimization filters by role, so set them explicitly.
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

        // mat_1=PCE10, mat_2=P3HT (donors); mat_3=PCBM, mat_4=oIDTBR (acceptors).
        static const char* NAMES[4] = {"mat_1", "mat_2", "mat_3", "mat_4"};
        for(Index i = 0; i < 4; ++i)
            opt.set_condition(NAMES[i], ResponseOptimization::ConditionType::Between, 0.0f, 1.0f);
        opt.set_condition("degradation", ResponseOptimization::ConditionType::Minimize);

        // Simplex equality + donor band (1/6 <= mat_1+mat_2 <= 5/6) from the YAML.
        opennn_idc::apply_yaml_constraints(opt, yaml_path);

        // Paper-default IDC configuration (Section 8.1).
        opt.set_evaluations_number(2000);   // N candidates per iteration
        opt.set_iterations(20);             // I_max
        opt.set_zoom_factor(0.85f);         // gamma
        opt.set_relative_tolerance(1e-6f);  // tau

        const auto t0 = std::chrono::high_resolution_clock::now();
        MatrixR results = opt.perform_response_optimization();
        const double walltime =
            std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - t0).count();

        if(results.rows() == 0)
            throw std::runtime_error("IDC returned no feasible point.");

        // Columns: [mat_1, mat_2, mat_3, mat_4, degradation].
        std::ofstream f(result_csv);
        f << std::setprecision(9) << "mat_1,mat_2,mat_3,mat_4,degradation\n";
        for(Index i = 0; i < 4; ++i) f << results(0, i) << ",";
        f << results(0, 4) << "\n";

        std::cout << "[OK] best photo-degradation = " << results(0, 4)
                  << "  (" << walltime << " s)  ->  " << result_csv << std::endl;
        return 0;
    }
    catch(const std::exception& e)
    {
        std::cerr << "[ERROR] " << e.what() << std::endl;
        return 1;
    }
}
