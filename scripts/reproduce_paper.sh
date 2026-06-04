#!/usr/bin/env bash
# reproduce_paper.sh — one-shot reproduction of the §8 worked examples.
#
#   1. configure + build (fetches the pinned OpenNN, see cmake/FindOrFetchOpenNN.cmake)
#   2. run the three C++ case studies (write each example's result.csv)
#   3. run the §8.2 BBOB analytical validation + §7.3 stress test
#   4. run the §8.4 Olympus real-data SO sweep
#
# Re-running is safe: the build is incremental and each example overwrites its
# own result.csv. Heavy Python sweeps (run_idc_21seeds.py) are NOT invoked here;
# run them explicitly from benchmarks/ when you want the full catalog.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> [1/4] Configure + build (Release)"
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release -j

echo "==> [2/4] Run the three C++ case studies"
"$ROOT/build/bin/moeed13"          # §8.3 simulator MO
"$ROOT/build/bin/photo_pce10"      # §8.4 real SO
"$ROOT/build/bin/concrete_uci_mo"  # §8.5 real MO

echo "==> [3/4] BBOB analytical validation (§8.2) + f15-f24 stress test (§7.3)"
python benchmarks/bbob/run_bbob_suites.py || echo "    (cocoex not installed; see benchmarks/bbob/README.md)"
python benchmarks/bbob/run_bbob_stress.py --algorithms IDC

echo "==> [4/4] Olympus real-data SO sweep (§8.4 photo_pce10)"
python benchmarks/run_olympus.py || echo "    (olympus not installed; see benchmarks/README.md)"

echo "==> Done. Per-example outputs are in examples/<name>/result.csv"
