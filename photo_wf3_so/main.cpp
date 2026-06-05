// Worked example — IDC on the Olympus photo_wf3 OPV task (SCI 2026 paper, Sec. 3).
//
// Single-objective Iterative Domain Contraction over a trained OpenNN surrogate
// (4 mass fractions -> measured photo-degradation). The blend is constrained by
//   (1) the 3-simplex   mat_1 + mat_2 + mat_3 + mat_4 == 1, and
//   (2) a functional donor:acceptor window  0.4 <= mat_1 + mat_2 <= 0.6
// (donor total = WF3 + P3HT), which keeps the optimum a realistic, percolating
// bulk-heterojunction rather than the degenerate donor-free blend. Both are
// affine input constraints, repaired in one pass by IDC's affine-repair
// operator (feasibility by construction). Writes result.csv with the
// recommended blend and its predicted degradation.
//
// Paths resolve relative to the example directory (EXAMPLE_DIR, set by CMake),
// so the binary runs from any build tree.

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

#include "yaml_constraints.h"   // sci2026/common/

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
        const fs::path dir = EXAMPLE_DIR;
        // CLI: --seed N (default 0); --nn / --out override the surrogate and the
        // output path. Defaults reproduce the paper's full-data deployment run.
        int seed = 0;
        fs::path nn_json    = dir / "nn" / "photo_wf3.json";
        fs::path result_csv = dir / "result.csv";
        const fs::path yaml_path = dir / "problem.yaml";
        for(int a = 1; a < argc; ++a)
        {
            const std::string s = argv[a];
            if(s == "--seed" && a + 1 < argc)      seed = std::stoi(argv[++a]);
            else if(s == "--nn" && a + 1 < argc)   nn_json = argv[++a];
            else if(s == "--out" && a + 1 < argc)  result_csv = argv[++a];
        }

        // Surrogate architecture: 4 inputs -> 8 hidden -> 1 output (degradation).
        // R^2 = 0.78 full / 0.80 test on the 1040-mixture Olympus campaign.
        ApproximationNetwork network({Index(4)}, Shape{Index(8)}, {Index(1)});
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

        opennn::set_seed(seed);
        ResponseOptimization opt(&network);

        // mat_1=WF3, mat_2=P3HT (donors); mat_3=PCBM, mat_4=oIDTBR (acceptors).
        static const char* NAMES[4] = {"mat_1", "mat_2", "mat_3", "mat_4"};
        for(Index i = 0; i < 4; ++i)
            opt.set_condition(NAMES[i], ResponseOptimization::ConditionType::Between, 0.0f, 1.0f);
        opt.set_condition("degradation", ResponseOptimization::ConditionType::Minimize);

        // Simplex equality + donor band (0.4 <= mat_1+mat_2 <= 0.6) from the YAML.
        opennn_idc::apply_yaml_constraints(opt, yaml_path);

        // Paper IDC configuration: 40k surrogate evaluations (2000 x 20).
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
        // 17 significant digits = exact IEEE-double round-trip, so the written
        // point re-checks against the simplex/donor-band constraints to machine
        // precision.
        f << std::setprecision(17) << "mat_1,mat_2,mat_3,mat_4,degradation\n";
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
