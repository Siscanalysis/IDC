#!/usr/bin/env bash
# reproduce_paper.sh — one-shot reproduction of the §8 worked examples.
#
#   1. configure + build (fetches the pinned OpenNN, see cmake/FindOrFetchOpenNN.cmake)
#   2. run the three C++ case studies (write each example's result.csv)
#   3. run the §8.2 BBOB analytical validation + §7.3 stress test
#   4. run the §8.4 Olympus real-data SO sweep
#   5. run the §8.4 photo_pce10 21-seed sweep + aggregate
#   6. render the surrogate-quality audit table (§8.5)
#   7. regenerate the §8 MO figures from the committed result CSVs
#
# Re-running is safe: the build is incremental and each example overwrites its
# own result.csv. The broader SO catalog (the ~14 problems §8.1 points to) and
# the pymoo/pycma baseline comparison are run from the authors' workspace; the
# 21-seed sweep here covers the shipped photo_pce10 SO example.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> [1/7] Configure + build (Release)"
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release -j

# Provenance: record the commit hashes this reproduction was generated from,
# so every result CSV / figure produced below is traceable to an exact build.
{
  echo "# Provenance for the result CSVs and figures produced by this run"
  echo "companion_repo_commit: $(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo 'unknown (not a git checkout)')"
  echo "opennn_tag: ${OPENNN_TAG:-v1.0-IDC-paper}"
  if [ -d "$ROOT/build/_deps/opennn-src/.git" ]; then
    echo "opennn_commit: $(git -C "$ROOT/build/_deps/opennn-src" rev-parse HEAD 2>/dev/null || echo unknown)"
  fi
} > "$ROOT/RESULTS_PROVENANCE.txt"
echo "    provenance -> RESULTS_PROVENANCE.txt"

echo "==> [2/7] Run the three C++ case studies"
"$ROOT/build/bin/moeed13"          # §8.3 simulator MO
"$ROOT/build/bin/photo_pce10"      # §8.4 real SO
"$ROOT/build/bin/concrete_uci_mo"  # §8.5 real MO

echo "==> [3/7] BBOB analytical validation (§8.2) + f15-f24 stress test (§7.3)"
python benchmarks/bbob/run_bbob_suites.py || echo "    (cocoex not installed; see benchmarks/bbob/README.md)"
python benchmarks/bbob/run_bbob_stress.py --algorithms IDC

echo "==> [4/7] Olympus real-data SO sweep (§8.4 photo_pce10)"
python benchmarks/run_olympus.py || echo "    (olympus not installed; see benchmarks/README.md)"

echo "==> [5/7] photo_pce10 21-seed sweep + aggregate (§8.4)"
python benchmarks/run_idc_21seeds.py
python benchmarks/aggregate_21seeds.py

echo "==> [6/7] Surrogate-quality audit (§8.5)"
python benchmarks/audit_surrogates.py

echo "==> [7/7] Regenerate §8 MO figures from committed CSVs"
python benchmarks/make_figures.py
python benchmarks/make_convergence_figure.py || echo "    (convergence trace optional)"

echo "==> Done. Example outputs in examples/<name>/result.csv; figures in benchmarks/figures/"
