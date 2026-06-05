"""
compute_concrete_mo_hv_feasible_only.py — empirical-reference HV on
concrete_uci_mo, restricted to points that satisfy ALL 5 formula
constraints declared in problems/concrete_uci_mo.yaml.

This is the honest comparison: pymoo's saved fronts contain many points
that satisfy the input bounds but violate the formula constraints (C6
ACI 233R slag replacement in particular). Without filtering those out,
the HV comparison rewards pymoo for infeasible solutions.
"""
from __future__ import annotations
import os
import csv
from pathlib import Path
import numpy as np
from pymoo.indicators.hv import HV

# Author-workspace demo paths (used only when this module is run directly to
# recompute HV on the parent fronts); the importable helpers below need none of
# them. Set IDC_BENCHMARK_BRANCH_A to point at the parent fronts to re-run.
RES = Path(os.environ.get("IDC_BENCHMARK_BRANCH_A", "results"))
IDC = RES / "concrete_uci_mo_idc_fronts.csv"
PYM = RES / "concrete_uci_mo_pymoo_fronts.csv"
TOL = 1e-3


def is_feasible(x: dict, strength: float | None = None) -> bool:
    """Current 7-constraint set (post 2026-06-01 ASTM C595 revision):
      C1  water_cement_ratio_lower:  water - 0.30*cement >= 0
      C2  water_cement_ratio_upper:  water - 0.70*cement <= 0
      C3  mass_balance:              sum(ingredients) in [2200, 2600]
      C4  binder_min_en206:          cement+slag+fly_ash >= 200
      C5  slag_replacement_max:      0.30*slag - 0.70*(cement+fly_ash) <= 0
      C6  fly_ash_replacement_max:   0.60*fly_ash - 0.40*(cement+slag) <= 0
      C7  strength_cap:              strength <= 100  (only checked if strength provided)
    """
    cement = x["cement"]; slag = x["slag"]; fly_ash = x["fly_ash"]
    water = x["water"]; sp = x["sp"]
    coarse_agg = x["coarse_agg"]; fine_agg = x["fine_agg"]
    binder = cement + slag + fly_ash
    sum_ings = binder + water + sp + coarse_agg + fine_agg
    checks = [
        (water - 0.30 * cement) >= -TOL,
        (water - 0.70 * cement) <=  TOL,
        sum_ings >= 2200 - 1.0,
        sum_ings <= 2600 + 1.0,
        binder   >= 200 - TOL,
        (0.30 * slag    - 0.70 * (cement + fly_ash)) <= TOL,
        (0.60 * fly_ash - 0.40 * (cement + slag))    <= TOL,
    ]
    if strength is not None:
        checks.append(strength <= 100.0 + TOL)
    return all(checks)


def load_feasible(path: Path, neg_strength: bool) -> dict[tuple[str, int], np.ndarray]:
    names = ["cement", "slag", "fly_ash", "water", "sp",
             "coarse_agg", "fine_agg", "age"]
    out: dict[tuple[str, int], list] = {}
    n_total = n_kept = 0
    with path.open() as f:
        r = csv.reader(f); next(r)
        for row in r:
            n_total += 1
            algo = row[0]; seed = int(row[1])
            strength = float(row[2])
            if neg_strength and strength < 0:
                strength = -strength
            cement = float(row[3])
            x = {names[i]: float(row[4 + i]) for i in range(8)}
            if not is_feasible(x, strength=strength):
                continue
            n_kept += 1
            out.setdefault((algo, seed), []).append((strength, cement))
    print(f"  {path.name}: kept {n_kept}/{n_total} feasible points")
    return {k: np.array(v) for k, v in out.items()}


def non_dominated_max_min(F: np.ndarray) -> np.ndarray:
    """Return indices of non-dominated points where F[:,0] is maximized and
    F[:,1] is minimized. Converts to min-min internally then marks points that
    are DOMINATED BY some other point (i.e., another point is <= in all coords
    and strictly < in at least one)."""
    G = np.column_stack([-F[:, 0], F[:, 1]])  # min-min: lower G[0] = higher strength
    n = G.shape[0]
    keep = np.ones(n, dtype=bool)
    for i in range(n):
        if not keep[i]:
            continue
        # Points that i DOMINATES: G[i] <= G[*] elementwise AND strictly < in some.
        dominated_by_i = (G[i] <= G).all(axis=1) & (G[i] < G).any(axis=1)
        keep &= ~dominated_by_i
    return np.where(keep)[0]


def main() -> None:
    print("Loading feasibility-filtered fronts...")
    idc = load_feasible(IDC, neg_strength=False)
    pym = load_feasible(PYM, neg_strength=True)

    union = np.vstack(list(idc.values()) + list(pym.values()))
    idx_nd = non_dominated_max_min(union)
    ref = union[idx_nd]
    print(f"\nEmpirical reference front (feasible-only): {ref.shape[0]} points")
    print(f"  strength range: [{ref[:, 0].min():.2f}, {ref[:, 0].max():.2f}]")
    print(f"  cement   range: [{ref[:, 1].min():.2f}, {ref[:, 1].max():.2f}]")

    nadir = np.array([-ref[:, 0].min() * 1.1, ref[:, 1].max() * 1.1])
    hv = HV(ref_point=nadir)
    print(f"Nadir ref (min-min): {nadir}")
    print()

    print(f"{'algorithm':12s} {'n_seeds':>8s} {'HV mean':>12s} {'HV std':>10s} "
          f"{'|PF| mean':>10s} {'feas %':>8s}")
    print("-" * 78)
    for label, fronts in [("idc", idc)] + sorted([(a, {(k0, k1): v
                                                      for (k0, k1), v in pym.items()
                                                      if k0 == a})
                                                  for a in sorted(set(k[0] for k in pym))]):
        if not fronts:
            print(f"{label:12s} (no feasible points)")
            continue
        hvs, pfsizes = [], []
        for (algo, seed), F in sorted(fronts.items()):
            idx = non_dominated_max_min(F)
            F_nd = F[idx]
            F_min = np.column_stack([-F_nd[:, 0], F_nd[:, 1]])
            hvs.append(float(hv(F_min)))
            pfsizes.append(len(F_nd))
        n = len(hvs)
        hvm = sum(hvs) / n
        hvs_std = (sum((x - hvm) ** 2 for x in hvs) / n) ** 0.5
        pfm = sum(pfsizes) / n
        print(f"{label:12s} {n:>8d} {hvm:>12.2f} {hvs_std:>10.2f} {pfm:>10.1f}")


if __name__ == "__main__":
    main()
