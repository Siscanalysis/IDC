// Worked example — IDC on the Yacht Hydrodynamics design, bi-objective
// (SCI 2026 paper, Sec. 4).
//
// At a FIXED cruising speed (Froude = 0.2875, the dataset mean), trade off
//   * minimize residuary resistance  (NN output)  -> less drag
//   * minimize length/beam ratio L/B (input)      -> wider hull (more beam:
//                                                    roomier and more stable)
// A wider hull (lower L/B) gains stability and interior volume but raises drag,
// so the two objectives genuinely conflict (L/B and resistance correlate
// negatively, ~ -0.61 on the surrogate) and IDC traces a dense Pareto front.
// The four remaining hull coefficients are free within the Delft envelope; the
// L/B objective is a passthrough on its input variable (no extra NN call).
// Writes result.csv with the recovered Pareto front.
//
// Paths resolve relative to the example directory (EXAMPLE_DIR, set by CMake).

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
        int seed = 0;
        fs::path nn_json    = dir / "nn" / "yacht.json";
        fs::path result_csv = dir / "result.csv";
        for(int a = 1; a < argc; ++a)
        {
            const std::string s = argv[a];
            if(s == "--seed" && a + 1 < argc)      seed = std::stoi(argv[++a]);
            else if(s == "--nn" && a + 1 < argc)   nn_json = argv[++a];
            else if(s == "--out" && a + 1 < argc)  result_csv = argv[++a];
        }

        // Variable order matches yacht.csv / the surrogate's input layer.
        static const char* NAMES[6] =
            {"long_pos_cob","prismatic_coef","length_displacement",
             "beam_draught","length_beam","froude"};
        // Delft Systematic Yacht Hull Series envelope.
        static const type LO[6] = {-5.0f, 0.53f, 4.34f, 2.81f, 2.73f, 0.125f};
        static const type HI[6] = { 0.0f, 0.60f, 5.14f, 5.35f, 3.64f, 0.45f};
        constexpr int OBJ2      = 4;       // length_beam (L/B) is the 2nd objective
        constexpr type FROUDE   = 0.2875f; // fixed cruising speed (dataset mean)

        // Surrogate architecture: 6 inputs -> 4 hidden -> 1 output (resistance).
        // R^2 = 0.995 full / 0.99 test (Growing-Neurons compact net).
        ApproximationNetwork network({Index(6)}, Shape{Index(4)}, {Index(1)});
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

        opennn::set_seed(seed);
        ResponseOptimization opt(&network);

        // Four hull coefficients free in the Delft box; Froude fixed; L/B is the
        // second objective (set below, not bounded as a free variable).
        for(int i = 0; i < 6; ++i)
        {
            if(i == OBJ2) continue;
            if(i == 5)
                opt.set_condition(NAMES[i], ResponseOptimization::ConditionType::Between, FROUDE, FROUDE);
            else
                opt.set_condition(NAMES[i], ResponseOptimization::ConditionType::Between, LO[i], HI[i]);
        }
        opt.set_condition("resistance",  ResponseOptimization::ConditionType::Minimize);
        opt.set_condition("length_beam", ResponseOptimization::ConditionType::Minimize); // = maximize beam

        // Paper IDC configuration: 40k surrogate evaluations (2000 x 20).
        opt.set_evaluations_number(2000);
        opt.set_iterations(20);
        opt.set_zoom_factor(0.85f);
        opt.set_relative_tolerance(1e-6f);

        const auto t0 = std::chrono::high_resolution_clock::now();
        MatrixR results = opt.perform_response_optimization();
        const double walltime =
            std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - t0).count();

        const Index n_pareto = results.rows();
        if(n_pareto == 0)
            throw std::runtime_error("IDC returned an empty Pareto front.");

        // Each row is a Pareto point. results columns: [x_0..x_5, resistance].
        // Objectives (non-x_ headers): resistance (output) and length_beam (= x_4).
        std::ofstream f(result_csv);
        f << std::setprecision(17)
          << "resistance,length_beam,x_long_pos_cob,x_prismatic_coef,"
             "x_length_displacement,x_beam_draught,x_length_beam,x_froude\n";
        for(Index r = 0; r < n_pareto; ++r)
        {
            f << results(r, 6) << "," << results(r, OBJ2);
            for(int i = 0; i < 6; ++i) f << "," << results(r, i);
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
