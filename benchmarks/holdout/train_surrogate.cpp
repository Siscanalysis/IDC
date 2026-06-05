// train_surrogate — companion holdout trainer.
//
// Trains one OpenNN surrogate on a held-out training split produced by
// benchmarks/gen_holdout_splits.py, and exports it as JSON (.json, loaded by
// the C++ IDC driver) AND as the numpy NeuralNetwork .py (loaded by the
// pymoo/pycma baselines in benchmarks/baselines/). This is the OpenNN
// Growing-Neurons training step behind the §7.4 held-out diagnostics
// (Table value_gap/space_gap), made reproducible from a clean clone.
//
// Mirrors the training path of the authors' baseline_trainer (Growing Neurons
// + ApproximationNetwork + TrainingStrategy), trimmed to a single split.
//
// Usage:
//   train_surrogate --data train_seed0.csv --yaml ../../examples/photo_pce10/problem.yaml \
//                   --out nn_seed0 [--hidden 15] [--seed 0]
//
// Writes <out>/surrogate.json and <out>/surrogate.py.

#include <algorithm>
#include <cctype>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "tabular_dataset.h"
#include "standard_networks.h"
#include "bounding_layer.h"
#include "neural_network.h"
#include "training_strategy.h"
#include "testing_analysis.h"
#include "growing_neurons.h"
#include "model_expression.h"
#include "variable.h"
#include "random_utilities.h"

using namespace opennn;
namespace fs = std::filesystem;

static std::string strip_ws(const std::string& s)
{
    const auto a = s.find_first_not_of(" \t\r\n");
    const auto b = s.find_last_not_of(" \t\r\n");
    return (a == std::string::npos) ? "" : s.substr(a, b - a + 1);
}
static std::string unquote(std::string s)
{
    s = strip_ws(s);
    if(s.size() >= 2 && (s.front() == '"' || s.front() == '\'') && s.back() == s.front())
        return s.substr(1, s.size() - 2);
    return s;
}

struct YamlVar { std::string name, type, goal; };
struct YamlSpec { std::vector<YamlVar> inputs, outputs; };

// Minimal flat constraints.yaml parser (inputs/outputs names + types), matching
// the baseline_trainer parser.
static YamlSpec parse_yaml(const fs::path& file)
{
    YamlSpec spec;
    std::ifstream f(file);
    std::string line, section;
    YamlVar cur; bool have = false;
    auto flush = [&]{ if(!have) return; (section=="inputs"?spec.inputs:spec.outputs).push_back(cur); have=false; };
    while(std::getline(f, line))
    {
        if(!line.empty() && line.back() == '\r') line.pop_back();
        const std::string t = strip_ws(line);
        if(t.empty() || t[0] == '#') continue;
        const bool top = !line.empty() && line[0] != ' ' && line[0] != '\t';
        if(top)
        {
            flush();
            if(t.rfind("inputs:", 0) == 0) section = "inputs";
            else if(t.rfind("outputs:", 0) == 0) section = "outputs";
            else section = "";
            continue;
        }
        if(section != "inputs" && section != "outputs") continue;
        if(t.rfind("- name:", 0) == 0) { flush(); cur = YamlVar{}; cur.name = unquote(t.substr(7)); have = true; continue; }
        if(t.rfind("- ", 0) == 0) { flush(); cur = YamlVar{}; have = true; }
        if(!have) continue;
        if(t.rfind("name:", 0) == 0 && cur.name.empty()) cur.name = unquote(t.substr(5));
        else if(t.rfind("type:", 0) == 0) cur.type = unquote(t.substr(5));
        else if(t.rfind("goal:", 0) == 0) cur.goal = unquote(t.substr(5));
    }
    flush();
    return spec;
}

static std::string arg(int c, char** v, const std::string& key, const std::string& def = "")
{
    for(int i = 1; i + 1 < c; ++i) if(key == v[i]) return v[i + 1];
    return def;
}

int main(int argc, char** argv)
{
    try
    {
        const fs::path data  = arg(argc, argv, "--data");
        const fs::path yaml  = arg(argc, argv, "--yaml");
        const fs::path out   = arg(argc, argv, "--out", "nn_out");
        const Index hidden   = static_cast<Index>(std::stoi(arg(argc, argv, "--hidden", "15")));
        const int seed       = std::stoi(arg(argc, argv, "--seed", "0"));
        if(data.empty() || yaml.empty())
            throw std::runtime_error("usage: train_surrogate --data <csv> --yaml <yaml> --out <dir> [--hidden N] [--seed S]");

        opennn::set_seed(seed);
        const YamlSpec spec = parse_yaml(yaml);
        const int n_in = static_cast<int>(spec.inputs.size());
        const int n_out = static_cast<int>(spec.outputs.size());
        if(n_in == 0 || n_out == 0) throw std::runtime_error("yaml missing inputs/outputs");

        // gen_holdout_splits.py writes a header CSV (comma-separated). It prepends
        // no row_id; columns follow the source dataset header.
        TabularDataset dataset(data, ",", true, false);

        const auto var_names = dataset.get_variable_names();
        auto find_var = [&](const std::string& nm) -> Index {
            for(Index i = 0; i < static_cast<Index>(var_names.size()); ++i)
                if(var_names[i] == nm) return i;
            return Index(-1);
        };
        for(const auto& v : spec.inputs)
        {
            const Index idx = find_var(v.name);
            if(idx < 0) throw std::runtime_error("input not in CSV header: " + v.name);
            dataset.set_variable_role(idx, "Input");
            if(v.type == "categorical")   dataset.set_variable_type(idx, VariableType::Categorical);
            else if(v.type == "binary")   dataset.set_variable_type(idx, VariableType::Binary);
            else                          dataset.set_variable_type(idx, VariableType::Numeric);
        }
        for(const auto& v : spec.outputs)
        {
            const Index idx = find_var(v.name);
            if(idx < 0) throw std::runtime_error("output not in CSV header: " + v.name);
            dataset.set_variable_role(idx, "Target");
            dataset.set_variable_type(idx, VariableType::Numeric);
        }

        dataset.impute_missing_values_statistic(TabularDataset::MissingValuesMethod::Mean);
        dataset.set_shape("Input",  { dataset.get_features_number("Input")  });
        dataset.set_shape("Target", { dataset.get_features_number("Target") });
        dataset.set_default_variable_scalers();
        dataset.split_samples_random(0.8f, 0.2f, 0.0f);

        ApproximationNetwork net(dataset.get_input_shape(),
                                 Shape{ hidden },
                                 dataset.get_target_shape());
        if(auto* b = dynamic_cast<Bounding*>(net.get_first("Bounding")))
            b->set_bounding_method("NoBounding");

        TrainingStrategy strategy(&net, &dataset);
        strategy.get_optimization_algorithm()->set_display(false);
        strategy.train();

        TestingAnalysis ta(&net, &dataset);
        const VectorR e_tr = ta.calculate_errors("Training");

        fs::create_directories(out);
        net.save(out / "surrogate.json");
        ModelExpression(&net).save(out / "surrogate.py", ModelExpression::ProgrammingLanguage::Python);

        std::cout << "[OK] trained on " << data.filename().string()
                  << " (hidden=" << hidden << ", seed=" << seed
                  << ", train MSE=" << e_tr[1] << ") -> " << out.string() << std::endl;
        return 0;
    }
    catch(const std::exception& e)
    {
        std::cerr << "[ERROR] " << e.what() << std::endl;
        return 1;
    }
}
