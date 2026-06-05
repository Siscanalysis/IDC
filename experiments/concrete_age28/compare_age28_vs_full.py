"""
compare_age28_vs_full.py — side-by-side aggregator for the age28
companion experiment vs the parent (age-mixed) §7.5 result.

Reads from this folder's results/ subdir (age28 chain outputs) and
the canonical IDC_benchmark/results/branch_a/ holdout outputs for
the parent comparison. Reports:

  - per-surrogate IDC strength_max and pymoo strength_max
  - HV per surrogate (vs union-ref of all algos)
  - Number of points whose NN-predicted strength exceeds the
    age=28 data ceiling (81.75 MPa) — the hallucination indicator
"""
from __future__ import annotations
from pathlib import Path
import sys

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
RESULTS_AGE28 = HERE / "results"
RESULTS_PARENT = Path(r"C:\Users\Artelnics\Desktop\experiments\IDC_benchmark\results\branch_a")

# Add the shared experiments dir for compute_concrete_mo_hv_feasible_only.py's HV func
sys.path.insert(0, str(Path(r"C:\Users\Artelnics\Desktop\experiments\Papers\first_IDC_paper\afte_first_review\experiments")))
try:
    from compute_concrete_mo_hv_feasible_only import non_dominated_max_min
    from pymoo.indicators.hv import HV as PyMooHV
    HAVE_HV = True
except ImportError:
    HAVE_HV = False

DATA_CEILING_AGE28 = 81.75   # max(strength) in the 425-row age=28 subset


def load_idc(f: Path) -> pd.DataFrame:
    df = pd.read_csv(f)
    df["strength"] = df["F_0"].astype(float)
    df["cement"]   = df["F_1"].astype(float)
    return df


def load_pymoo(f: Path) -> pd.DataFrame:
    df = pd.read_csv(f)
    df["strength"] = -df["F_0"].astype(float)
    df["cement"]   =  df["F_1"].astype(float)
    return df


def hv_for(F: np.ndarray, nadir: np.ndarray) -> float:
    if F.shape[0] == 0 or not HAVE_HV:
        return float("nan")
    # convert to all-min and apply pymoo HV (larger is better)
    G = np.column_stack([-F[:, 0], F[:, 1]])
    return float(PyMooHV(ref_point=nadir)(G))


def summarise_seed(idc_fronts: Path, pym_fronts: Path) -> dict:
    idc = load_idc(idc_fronts)
    pym = load_pymoo(pym_fronts)

    # union nadir = max(-strength), max(cement) over union, both with margin
    union = pd.concat([idc[["strength","cement"]], pym[["strength","cement"]]], ignore_index=True)
    nadir = np.array([-union.strength.min() * 1.1, union.cement.max() * 1.1])

    out = {}
    out["idc_smax"] = float(idc.strength.max())
    out["idc_smin"] = float(idc.strength.min())
    out["idc_npts"] = len(idc)
    out["idc_above_ceiling"] = int((idc.strength > DATA_CEILING_AGE28).sum())
    out["idc_hv"] = hv_for(idc[["strength","cement"]].to_numpy(), nadir)
    for algo, g in pym.groupby("algorithm"):
        out[f"pym_{algo}_smax"] = float(g.strength.max())
        out[f"pym_{algo}_npts"] = len(g)
        out[f"pym_{algo}_hv"]   = hv_for(g[["strength","cement"]].to_numpy(), nadir)
    return out


def main() -> None:
    print("=" * 90)
    print("AGE=28 surrogate — full-data + 5 holdout seeds")
    print("=" * 90)
    print("Data ceiling at age=28: 81.75 MPa  (the hallucination threshold)")
    print()
    print(f"{'label':<22} {'IDC smax':>10} {'IDC npts':>9} {'>ceil':>6} {'IDC HV':>10}  "
          f"{'NSGA2 smax':>11} {'NSGA3 smax':>11}")
    print("-" * 100)

    for tag in ["full"] + [f"holdout_seed{s}" for s in range(5)]:
        idc_f = RESULTS_AGE28 / f"age28_concrete_uci_mo_idc_fronts_{tag}.csv"
        pym_f = RESULTS_AGE28 / f"age28_concrete_uci_mo_pymoo_fronts_{tag}.csv"
        if not idc_f.exists() or not pym_f.exists():
            print(f"  {tag}: NOT YET — {idc_f.name if not idc_f.exists() else pym_f.name} missing")
            continue
        s = summarise_seed(idc_f, pym_f)
        print(f"  {tag:<20} {s['idc_smax']:>10.2f} {s['idc_npts']:>9d} {s['idc_above_ceiling']:>6d} "
              f"{s.get('idc_hv', float('nan')):>10.3g}  "
              f"{s.get('pym_nsga2_smax', float('nan')):>11.2f} "
              f"{s.get('pym_nsga3_smax', float('nan')):>11.2f}")

    # Parent (age-mixed) comparison
    print()
    print("=" * 90)
    print("PARENT (age-mixed §7.5 baseline) — holdout 5 seeds")
    print("=" * 90)
    print(f"{'label':<22} {'IDC smax':>10} {'IDC npts':>9} {'>ceil':>6} {'IDC HV':>10}  "
          f"{'NSGA2 smax':>11} {'NSGA3 smax':>11}")
    print("-" * 100)
    for s in range(5):
        idc_f = RESULTS_PARENT / f"concrete_uci_mo_idc_fronts_holdout_seed{s}.csv"
        pym_f = RESULTS_PARENT / f"concrete_uci_mo_pymoo_fronts_holdout_seed{s}.csv"
        if not idc_f.exists() or not pym_f.exists():
            print(f"  seed_{s}: NOT FOUND"); continue
        si = summarise_seed(idc_f, pym_f)
        print(f"  parent_holdout_seed{s}  {si['idc_smax']:>10.2f} {si['idc_npts']:>9d} {si['idc_above_ceiling']:>6d} "
              f"{si.get('idc_hv', float('nan')):>10.3g}  "
              f"{si.get('pym_nsga2_smax', float('nan')):>11.2f} "
              f"{si.get('pym_nsga3_smax', float('nan')):>11.2f}")


if __name__ == "__main__":
    main()
