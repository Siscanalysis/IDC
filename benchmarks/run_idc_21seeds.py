#!/usr/bin/env python3
"""
run_idc_21seeds.py — sweep the shipped single-objective worked example over the
21 independent optimizer seeds of the paper's §7.4 protocol.

Runs the built `bin/<example>` with `--seed s` for s in 0..N-1, parses the
machine-readable `SWEEP seed=.. best_f=.. walltime=..` line each binary prints,
and writes a per-seed CSV to `benchmarks/results/branch_a/<example>_idc.csv`.
Aggregate the result with `aggregate_21seeds.py`.

Only the single-objective real-application example (photo_pce10) ships as a C++
driver here; the broader SO catalog that §7.1 points to is run from the authors'
workspace, and other Olympus tasks are reachable via `run_olympus.py --task`.

    python run_idc_21seeds.py            # photo_pce10, 21 seeds
    python run_idc_21seeds.py --seeds 5  # quick check
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
BIN_DIRS = [ROOT / "build" / "bin" / "Release", ROOT / "build" / "bin"]
OUT = HERE / "results" / "branch_a"

# Shipped single-objective example binaries (CMake target -> problem key).
SO_EXAMPLES = {"photo_pce10": "photo_pce10"}

SWEEP_RE = re.compile(
    r"SWEEP\s+seed=(\d+)\s+best_f=([-\d.eE+]+)\s+walltime=([-\d.eE+]+)")


def find_bin(name: str) -> Path | None:
    for d in BIN_DIRS:
        for ext in (".exe", ""):
            p = d / f"{name}{ext}"
            if p.exists():
                return p
    return None


def run_problem(target: str, key: str, seeds: int) -> None:
    exe = find_bin(target)
    if exe is None:
        print(f"[skip] {target}: binary not built (run cmake --build first)")
        return
    rows = []
    for s in range(seeds):
        t0 = time.time()
        r = subprocess.run([str(exe), "--seed", str(s)],
                           capture_output=True, text=True, timeout=3600)
        if r.returncode != 0:
            print(f"[FAIL] {target} seed {s}: {r.stderr[-300:]}")
            continue
        m = SWEEP_RE.search(r.stdout)
        if not m:
            print(f"[WARN] {target} seed {s}: no SWEEP line in output")
            continue
        rows.append({"seed": int(m.group(1)), "algorithm": "idc_default",
                     "problem": key, "best_f": float(m.group(2)),
                     "feasible": True, "walltime_s": float(m.group(3))})
        print(f"[ok] {target} seed {s}: best_f={m.group(2)} ({time.time() - t0:.2f}s)")
    if rows:
        OUT.mkdir(parents=True, exist_ok=True)
        out = OUT / f"{key}_idc.csv"
        with open(out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"[write] {out} ({len(rows)} seeds)")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seeds", type=int, default=21)
    ap.add_argument("--problems", nargs="+", default=list(SO_EXAMPLES))
    args = ap.parse_args(argv)
    for target in args.problems:
        run_problem(target, SO_EXAMPLES.get(target, target), args.seeds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
