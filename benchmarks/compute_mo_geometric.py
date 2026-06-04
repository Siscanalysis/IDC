#!/usr/bin/env python3
"""
compute_mo_geometric.py — recompute the §8 multi-objective geometric
front-quality diagnostics (Tables `mo_geom_moeed13` / `mo_geom_concrete`)
from committed fronts, so they stay consistent with the normalized-HV tables.

For each case (MOEED13, UCI Concrete) and algorithm (IDC, NSGA-II, NSGA-III)
the returned front is reduced to its non-dominated set and normalized per
objective to [0,1] against the union of all three fronts (1 = best), matching
the normalized-HV convention. It then reports:
  h   internal gap   = max_i min_{j!=i} ||o_i - o_j|| / sqrt(k)   (largest hole)
  b   boundary gap   = (1/k) sum_j |1 - max_i o_{i,j}|           (reach shortfall)
  SP  Schott spacing = std of nearest-neighbour Manhattan distances (x1e-3)
  Dl  Deb spread     = (df+dl+sum|d_i-dbar|)/(df+dl+(N-1)dbar),
                       df,dl = distance of the front extremes to the ideal
                       corners (0,1) and (1,0) of the normalized box.

Validation: on the committed Concrete fronts this reproduces the reported
Table values to rounding (h, b, Delta exact; SP exact except the 11-point
NSGA-III front, ~5%).

    python compute_mo_geometric.py
"""
from __future__ import annotations
import csv
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree

HERE = Path(__file__).parent
ROOT = HERE.parent


def _load(p):
    with open(p) as f:
        return list(csv.DictReader(f))


def _nondom_min(P):
    P = sorted(set(P), key=lambda p: (p[0], p[1]))
    r, b = [], None
    for a, c in P:
        if b is None or c < b:
            r.append((a, c)); b = c
    return r


def _norm(P, ext):
    amin, amax, bmin, bmax = ext
    return np.array([((amax - a) / (amax - amin), (bmax - c) / (bmax - bmin)) for a, c in P])


def _hv(Q):
    Q = Q[np.argsort(-Q[:, 0])]; area, ly = 0.0, 0.0
    for x, y in Q:
        if y > ly:
            area += x * (y - ly); ly = y
    return area


def _hgap(Q):
    if len(Q) < 2:
        return 1.0
    d, _ = cKDTree(Q).query(Q, k=2)
    return float(d[:, 1].max()) / np.sqrt(2)


def _bgap(Q):
    return 0.5 * sum(abs(1 - Q[:, j].max()) for j in range(2))


def _schott(Q):
    P = len(Q)
    d = cKDTree(Q).query(Q, k=2, p=1)[0][:, 1]
    db = d.mean()
    return float(np.sqrt(((db - d) ** 2).sum() / (P - 1))) * 1000 if P > 1 else 0.0


def _deb(Q):
    S = Q[np.argsort(Q[:, 0])]; P = len(S)
    if P < 2:
        return 0.0
    d = np.sqrt(((S[1:] - S[:-1]) ** 2).sum(1)); db = d.mean()
    df = np.hypot(*(S[0] - np.array([0.0, 1.0])))
    dl = np.hypot(*(S[-1] - np.array([1.0, 0.0])))
    return float((df + dl + np.abs(d - db).sum()) / (df + dl + (P - 1) * db))


def _report(case, fronts):
    allp = np.vstack([np.array(F) for F in fronts.values()])
    ext = (allp[:, 0].min(), allp[:, 0].max(), allp[:, 1].min(), allp[:, 1].max())
    print(f"# {case}")
    print(f"{'algo':9} {'h':>7} {'b':>7} {'SP(e-3)':>8} {'Delta':>6} {'HV':>7} {'|P|':>7}")
    for n, F in fronts.items():
        Q = _norm(F, ext)
        print(f"{n:9} {_hgap(Q):7.3f} {_bgap(Q):7.3f} {_schott(Q):8.1f} "
              f"{_deb(Q):6.2f} {_hv(Q):7.3f} {len(F):7d}")
    print()


def main() -> int:
    ex = ROOT / "examples" / "moeed13"
    fr = _load(ex / "moeed13_pymoo_fronts.csv"); idc = _load(ex / "result.csv")
    _report("MOEED13", {
        "IDC":   _nondom_min([(float(d["total_cost"]), float(d["total_emission"])) for d in idc]),
        "NSGA-II":  _nondom_min([(float(d["F_0"]), float(d["F_1"])) for d in fr if d["algorithm"] == "nsga2"]),
        "NSGA-III": _nondom_min([(float(d["F_0"]), float(d["F_1"])) for d in fr if d["algorithm"] == "nsga3"]),
    })

    cd = ROOT / "experiments" / "concrete_age28" / "results"
    pf = _load(cd / "age28_fulldata_pymoo_fronts.csv"); ic = _load(cd / "age28_fulldata_idc_fronts.csv")
    _report("UCI Concrete (age-28)", {
        "IDC":      _nondom_min([(-float(d["F_0"]), float(d["F_1"])) for d in ic if d["seed"] == "0"]),
        "NSGA-II":  _nondom_min([(float(d["F_0"]), float(d["F_1"])) for d in pf if d["algorithm"] == "nsga2" and d["seed"] == "42"]),
        "NSGA-III": _nondom_min([(float(d["F_0"]), float(d["F_1"])) for d in pf if d["algorithm"] == "nsga3" and d["seed"] == "42"]),
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
