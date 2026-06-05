#!/usr/bin/env bash
# reproduce_paper.sh — one-shot reproduction of the §7 worked examples.
#
#   1. configure + build (fetches the pinned OpenNN, see cmake/FindOrFetchOpenNN.cmake)
#   2. run the three C++ case studies (write each example's result.csv)
#   3. run the §7.2 BBOB analytical validation + §6.3 stress test
#   4. run the §7.4 Olympus real-data SO sweep
#   5. run the §7.4 photo_pce10 21-seed sweep + aggregate
#   6. run the pymoo/pycma baselines for the three §7 example problems
#   7. render the surrogate-quality audit table (§7.5)
#   8. regenerate the §7 MO figures from the committed result CSVs
#
# Re-running is safe: the build is incremental and each example overwrites its
# own result.csv. The §7 example baselines run here (step 6); only the broader
# ~30-problem benchmark catalog (the additional problems §7.1 points to) and its
# baseline sweep are run from the authors' workspace.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> [1/8] Configure + build (Release)"
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release -j

# Provenance: record the commit hashes this reproduction was generated from,
# so every result CSV / figure produced below is traceable to an exact build.
{
  echo "# Provenance for the result CSVs and figures produced by this run"
  echo "companion_repo_commit: $(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo 'unknown (not a git checkout)')"
  echo "opennn_tag: ${OPENNN_TAG:-v1.2-IDC-paper}"
  if [ -d "$ROOT/build/_deps/opennn-src/.git" ]; then
    echo "opennn_commit: $(git -C "$ROOT/build/_deps/opennn-src" rev-parse HEAD 2>/dev/null || echo unknown)"
  fi
} > "$ROOT/RESULTS_PROVENANCE.txt"
echo "    provenance -> RESULTS_PROVENANCE.txt"

echo "==> [2/8] Run the three C++ case studies (MO examples: equality + band)"
"$ROOT/build/bin/moeed13"               # §7.3 simulator MO — equality (headline)
"$ROOT/build/bin/moeed13" band          # §7.3 simulator MO — tolerance band
"$ROOT/build/bin/photo_pce10"           # §7.4 real SO
"$ROOT/build/bin/concrete_uci_mo"       # §7.5 real MO — equality (headline)
"$ROOT/build/bin/concrete_uci_mo" band  # §7.5 real MO — tolerance band

echo "==> [3/8] BBOB analytical validation (§7.2) + f15-f24 stress test (§6.3)"
python benchmarks/bbob/run_bbob_suites.py || echo "    (cocoex not installed; see benchmarks/bbob/README.md)"
python benchmarks/bbob/run_bbob_stress.py --algorithms IDC

echo "==> [4/8] Olympus real-data SO sweep (§7.4 photo_pce10)"
python benchmarks/run_olympus.py || echo "    (olympus not installed; see benchmarks/README.md)"

echo "==> [5/8] photo_pce10 21-seed sweep + aggregate (§7.4)"
python benchmarks/run_idc_21seeds.py
python benchmarks/aggregate_21seeds.py

echo "==> [6/8] pymoo/pycma baselines for the §7 example problems"
# §7.4 SO sweep at the 40k SO budget; §7.3/§7.5 MO at the matched 400k budget,
# both constraint formulations (equality top-level + band subdir).
python benchmarks/baselines/run_baselines.py --example photo_pce10     --seeds 21 || echo "    (pymoo/cma not installed; see benchmarks/requirements.txt)"
python benchmarks/baselines/run_baselines.py --example concrete_uci_mo --seed 42 --budget 400000 || true
python benchmarks/baselines/run_baselines.py --example concrete_uci_mo --seed 42 --budget 400000 --subdir band || true
python benchmarks/baselines/run_baselines.py --example moeed13         --seed 42 --budget 400000 || true
python benchmarks/baselines/run_baselines.py --example moeed13         --seed 42 --budget 400000 --subdir band || true

echo "==> [7/8] Surrogate-quality audit (§7.5)"
python benchmarks/audit_surrogates.py

echo "==> [8/8] Regenerate §7 MO figures + matched-budget tables from committed CSVs"
# Matched-budget normalized-HV figures (equality + band) and the machine-readable
# results summary (Tables tab:case_moeed13 / tab:case_concrete_mo + residual tables).
python benchmarks/mo_matched_budget.py
python benchmarks/compute_mo_geometric.py    # geometric front-quality diagnostics
python benchmarks/make_figures.py            # IDC Pareto-front scatter views
python benchmarks/make_convergence_figure.py || echo "    (convergence trace optional)"

echo "==> Done. Example outputs in examples/<name>/result.csv; figures in benchmarks/figures/"
