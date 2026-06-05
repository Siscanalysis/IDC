#!/usr/bin/env python3
"""
run_idc_sensitivity.py — N x gamma hyperparameter-sensitivity sweep for IDC on the
single-objective Photo-PCE10 case study (§7.4), added in response to Reviewer Z
(Major Issue 0: "no quantification of how the zoom factor and the sample size N
affect solution quality") and Reviewer X ("sensitivity analyses of key
hyperparameters").

It calls the built photo_pce10 example binary with the --evals (N), --zoom (gamma),
and --seed overrides, sweeping a compact grid of N x gamma at fixed I_max and tau,
several seeds per cell, and records the best feasible photo-degradation (lower is
better) reached in each (N, gamma, seed) run. The full offline grid (also over
I_max and tau, across 23 problems) is documented in docs/hyperparameter_tuning.md;
this script reproduces the in-paper N x gamma table on one representative problem.

Output: benchmarks/results/photo_pce10_sensitivity.csv  (one row per N,gamma,seed)
plus a printed mean-best_f table.

Usage:
    python run_idc_sensitivity.py --seeds 5
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent          # benchmarks/
ROOT = HERE.parent                              # repo root
EXE_CANDIDATES = [
    ROOT / "build" / "bin" / "Release" / "photo_pce10.exe",
    ROOT / "build" / "bin" / "photo_pce10",
    ROOT / "build" / "bin" / "Release" / "photo_pce10",
]

N_GRID = [500, 1000, 2000, 4000, 8000]
GAMMA_GRID = [0.45, 0.60, 0.75, 0.85, 0.95]
SWEEP_RE = re.compile(r"best_f=([0-9.eE+\-]+)\s+walltime=([0-9.eE+\-]+)")


def find_exe() -> Path:
    for p in EXE_CANDIDATES:
        if p.exists():
            return p
    raise FileNotFoundError(
        "photo_pce10 binary not found; build it first "
        "(cmake --build build --target photo_pce10 --config Release).")


def run_one(exe: Path, n: int, gamma: float, seed: int, out_csv: Path) -> tuple[float, float]:
    cmd = [str(exe), "--evals", str(n), "--zoom", f"{gamma}",
           "--seed", str(seed), "--out", str(out_csv)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    m = SWEEP_RE.search(r.stdout)
    if not m:
        raise RuntimeError(f"no SWEEP line for N={n} gamma={gamma} seed={seed}:\n"
                           f"{r.stdout}\n{r.stderr}")
    return float(m.group(1)), float(m.group(2))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seeds", type=int, default=5, help="seeds 0..S-1 per cell")
    ap.add_argument("--out", type=Path, default=HERE / "results" / "photo_pce10_sensitivity.csv")
    args = ap.parse_args()

    exe = find_exe()
    print(f"[exe] {exe}")
    rows = []
    tmp = Path(tempfile.gettempdir()) / "_idc_sens_tmp.csv"
    t0 = time.perf_counter()
    for n in N_GRID:
        for g in GAMMA_GRID:
            bests = []
            for s in range(args.seeds):
                bf, wt = run_one(exe, n, g, s, tmp)
                bests.append(bf)
                rows.append({"N": n, "gamma": g, "seed": s,
                             "best_f": bf, "walltime_s": wt})
            arr = np.array(bests)
            print(f"  N={n:5d} gamma={g:.2f}  best_f mean={arr.mean():.6g} "
                  f"std={arr.std():.2g} min={arr.min():.6g}")
    dur = time.perf_counter() - t0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["N", "gamma", "seed", "best_f", "walltime_s"])
        w.writeheader()
        w.writerows(rows)
    print(f"[OK] wrote {len(rows)} rows -> {args.out}  ({dur:.1f}s)")

    # mean-best_f table (rows = N, cols = gamma)
    print("\nmean best feasible degradation (lower = better):")
    hdr = "   N \\ g | " + " ".join(f"{g:>8.2f}" for g in GAMMA_GRID)
    print(hdr)
    for n in N_GRID:
        cells = []
        for g in GAMMA_GRID:
            vals = [r["best_f"] for r in rows if r["N"] == n and r["gamma"] == g]
            cells.append(f"{np.mean(vals):8.5f}")
        print(f"   {n:5d} | " + " ".join(cells))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
