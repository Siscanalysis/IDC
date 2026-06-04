#!/usr/bin/env python3
"""
aggregate_21seeds.py — aggregate per-seed sweep CSVs (from run_idc_21seeds.py)
into per-problem summaries.

Reads `benchmarks/results/branch_a/<problem>_idc.csv` and writes
`<problem>_summary_21seeds.csv` with mean ± std, best-of-seeds, feasible %, and
mean wall-clock per algorithm. Orientation is per-problem: photo_pce10 is a
minimization objective (lower photo-degradation is better), so best-of-seeds is
the minimum.

    python aggregate_21seeds.py

Self-contained: standard library only.
"""
from __future__ import annotations

import csv
import statistics as st
from pathlib import Path

HERE = Path(__file__).parent
RES = HERE / "results" / "branch_a"

# True = higher best_f is better. photo_pce10 minimizes photo-degradation.
MAXIMIZE = {"photo_pce10": False}


def summarize(path: Path, maximize: bool) -> list[dict]:
    rows = list(csv.DictReader(open(path, newline="")))
    by: dict[str, list[dict]] = {}
    for r in rows:
        by.setdefault(r["algorithm"], []).append(r)
    out = []
    for algo, rs in by.items():
        bf = [float(r["best_f"]) for r in rs]
        wt = [float(r["walltime_s"]) for r in rs]
        feas = 100.0 * sum(str(r["feasible"]).lower() == "true" for r in rs) / len(rs)
        out.append({
            "algorithm": algo,
            "n_seeds": len(rs),
            "best_f_mean": st.mean(bf),
            "best_f_std": st.pstdev(bf) if len(bf) > 1 else 0.0,
            "best_f_best": (max(bf) if maximize else min(bf)),
            "feasible_pct": feas,
            "walltime_mean_s": st.mean(wt),
        })
    out.sort(key=lambda d: d["best_f_mean"], reverse=maximize)
    return out


def main() -> int:
    if not RES.exists():
        print(f"[skip] {RES} missing (run run_idc_21seeds.py first)")
        return 0
    found = False
    for csvf in sorted(RES.glob("*_idc.csv")):
        found = True
        problem = csvf.stem.replace("_idc", "")
        summ = summarize(csvf, MAXIMIZE.get(problem, False))
        out = RES / f"{problem}_summary_21seeds.csv"
        with open(out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(summ[0].keys()))
            w.writeheader()
            w.writerows(summ)
        b = summ[0]
        print(f"[ok] {problem}: {b['n_seeds']} seeds, "
              f"best_f_mean={b['best_f_mean']:.5g} ± {b['best_f_std']:.2g}, "
              f"best={b['best_f_best']:.5g} -> {out.name}")
    if not found:
        print(f"[skip] no *_idc.csv in {RES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
