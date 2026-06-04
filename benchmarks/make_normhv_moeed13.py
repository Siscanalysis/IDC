#!/usr/bin/env python3
"""
make_normhv_moeed13.py — regenerate the MOEED13 normalized-hypervolume figure
(fig_normhv_moeed13) from committed artifacts, so it matches the Table-2 numbers.

Reads the bundled IDC front (examples/moeed13/result.csv) and the committed
pymoo NSGA-II/NSGA-III seed-42 fronts (examples/moeed13/moeed13_pymoo_fronts.csv,
produced by baselines/run_baselines.py --example moeed13 --seed 42). Both
objectives (total cost, NOx emission) are minimized; each is normalized per
objective to [0,1] against the union of all three fronts with 1 = best, and the
dominated staircase down to the (0,0) worst corner is filled. The panel title
reports the resulting normalized HV (dominated area).

    python make_normhv_moeed13.py            # -> figures/fig_normhv_moeed13.{pdf,png}
"""
from __future__ import annotations
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
ROOT = HERE.parent
EX = ROOT / "examples" / "moeed13"
OUT = HERE / "figures"
OUT.mkdir(exist_ok=True)


def _load(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def _nondom_min(pts):
    pts = sorted(set(pts), key=lambda p: (p[0], p[1]))
    res, best = [], None
    for a, b in pts:
        if best is None or b < best:
            res.append((a, b)); best = b
    return res


def main() -> int:
    fr = _load(EX / "moeed13_pymoo_fronts.csv")
    idc = _load(EX / "result.csv")

    def mo(algo):
        return [(float(d["F_0"]), float(d["F_1"])) for d in fr if d["algorithm"] == algo]

    fronts = {
        "IDC":   _nondom_min([(float(d["total_cost"]), float(d["total_emission"])) for d in idc]),
        "NSGA2": _nondom_min(mo("nsga2")),
        "NSGA3": _nondom_min(mo("nsga3")),
    }

    allp = [p for F in fronts.values() for p in F]
    amin, amax = min(p[0] for p in allp), max(p[0] for p in allp)
    bmin, bmax = min(p[1] for p in allp), max(p[1] for p in allp)

    def norm(F):  # both minimized -> best = 1
        return _nondom_max([((amax - a) / (amax - amin), (bmax - b) / (bmax - bmin)) for a, b in F])

    def _nondom_max(Q):  # keep maximize-both non-dominated, sorted ascending x
        Q = sorted(set(Q), key=lambda p: (p[0], -p[1]))
        res, best = [], None
        for x, y in reversed(Q):  # descending x
            if best is None or y > best:
                res.append((x, y)); best = y
        return sorted(res)        # ascending x, y descending

    def hv(Q):
        area, last = 0.0, 0.0
        for x, y in sorted(Q, key=lambda p: -p[0]):
            if y > last:
                area += x * (y - last); last = y
        return area

    plt.rcParams.update({
        "font.family": "serif", "font.size": 9, "axes.titlesize": 10,
        "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.25,
    })
    greys = {"IDC": "0.50", "NSGA2": "0.68", "NSGA3": "0.82"}
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4), sharey=True)
    for ax, name in zip(axes, ["IDC", "NSGA2", "NSGA3"]):
        Q = norm(fronts[name])
        xs = [0.0] + [p[0] for p in Q]
        ys = [p[1] for p in Q] + [0.0]
        ax.fill_between(xs, ys, step="post", facecolor=greys[name],
                        edgecolor="0.30", linewidth=0.8)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.set_title(f"{name}\nnorm. HV = {hv(Q):.3f}")
        ax.set_xlabel(r"Total cost [\$/h]  (norm., 1=best)")
    axes[0].set_ylabel(r"NO$_x$ [lb/h]  (norm., 1=best)")
    fig.suptitle("MOEED13 (full-data simulator model) — normalized HV (filled area; 1=best corner)")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"fig_normhv_moeed13.{ext}", dpi=150, bbox_inches="tight")
    print("wrote", OUT / "fig_normhv_moeed13.pdf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
