#!/usr/bin/env python3
"""
Plot the photo_pce10 convergence-vs-budget figure (manuscript §7.4).

Reads the committed convergence trace
(`extra_results/photo_pce10_convergence.csv`) and renders best feasible
photo-degradation found vs. the number of surrogate evaluations, for IDC
and the pymoo single-objective baselines, on the top-5% holdout
surrogates. This is the figure addressing the reviewer's request for a
convergence plot.

This script only
renders the committed CSV, so the figure regenerates with no heavy
dependencies (just matplotlib + numpy).

Usage:
    python make_convergence_figure.py            # writes fig_conv_photo_pce10.pdf
    python make_convergence_figure.py --out /path/fig.pdf
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

HERE = Path(__file__).parent
DEFAULT_CSV = HERE / "extra_results" / "photo_pce10_convergence.csv"

# Display order, labels, and styles. IDC emphasized.
SERIES = [
    ("idc", "IDC", {"color": "#1f77b4", "lw": 2.4, "zorder": 5}),
    ("ga", "GA", {"color": "#2ca02c", "lw": 1.4, "ls": "--"}),
    ("de", "DE", {"color": "#ff7f0e", "lw": 1.4, "ls": "--"}),
    ("pso", "PSO", {"color": "#9467bd", "lw": 1.4, "ls": "--"}),
    ("cmaes", "CMA-ES", {"color": "#d62728", "lw": 1.4, "ls": ":"}),
]


def load(csv_path: Path):
    rows = list(csv.DictReader(open(csv_path)))
    evals = [float(r["evaluations"]) for r in rows]
    cols = {}
    for key, _, _ in SERIES:
        cols[key] = [float(r[f"{key}_mean"]) if r.get(f"{key}_mean") not in (None, "") else None
                     for r in rows]
        fk = f"{key}_feasible_frac"
        cols[key + "_feas"] = [float(r[fk]) if r.get(fk) not in (None, "") else 0.0 for r in rows]
    return evals, cols


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    ap.add_argument("--out", type=Path, default=HERE / "fig_conv_photo_pce10.pdf")
    args = ap.parse_args(argv)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    evals, cols = load(args.csv)

    import numpy as np

    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    infeasible = []
    for key, label, style in SERIES:
        xs = [e for e, v in zip(evals, cols[key]) if v is not None]
        ys = [v for v in cols[key] if v is not None]
        if not ys:
            # series never produced a feasible point (e.g. CMA-ES on the simplex)
            infeasible.append(label)
            continue
        # The CSV stores the mean across feasible seeds; the population over
        # which the mean is taken grows as more seeds find a first feasible
        # point, which can cause spurious bumps where the "best-so-far" mean
        # transiently increases. Enforce monotone non-increasing (cumulative
        # min) before plotting — every seed's running-best is monotone, so
        # any apparent increase is a pure feasibility-population artefact.
        ys = np.minimum.accumulate(np.asarray(ys, dtype=float)).tolist()
        ax.plot(xs, ys, label=label, **style)

    if infeasible:
        ax.text(0.97, 0.95, f"{', '.join(infeasible)}: no feasible point",
                transform=ax.transAxes, ha="right", va="top", fontsize=8,
                color="#d62728",
                bbox=dict(boxstyle="round", fc="white", ec="#d62728", alpha=0.8))

    ax.set_xlabel("surrogate evaluations")
    ax.set_ylabel("best feasible photo-degradation")
    ax.set_yscale("log")
    ax.set_title("Photo-PCE10 convergence (top-5% holdout surrogates)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(args.out)
    fig.savefig(args.out.with_suffix(".png"), dpi=150)
    print(f"[OK] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
