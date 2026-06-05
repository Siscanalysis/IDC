#!/usr/bin/env python3
"""
mo_matched_budget.py — authoritative regeneration of the §7.3 (MOEED13) and
§7.5 (UCI Concrete) matched-budget multi-objective results, for BOTH constraint
formulations (equality + tolerance band), from the committed example artifacts.

For each example and formulation it reads the bundled IDC front and the bundled
NSGA-II/NSGA-III fronts (all produced under the same 400000 total
surrogate-evaluation budget — IDC via OpenNN's set_max_total_evaluations(400000)
cap, the baselines via pymoo's MaximumFunctionCallTermination(400000)), and
reports, per algorithm:

  |PF|      number of returned Pareto points (IDC: archive; NSGA: final front)
  normHV    normalized hypervolume (1 = best corner) against a fixed
            per-problem reference box (the single-seed full-data equality run;
            the same box for every formulation), same staircase convention as
            the paper's normalized-HV figures
  feas%     feasibility at the engineering tolerance (|Sum - target| <= 0.5),
            NOT the strict 1e-6 float tolerance (which spuriously fails IDC's
            float32 equality-projected points; see problem_pymoo.feasible)
  res_mean  mean equality residual  mean |Sum(vars) - target|
  res_max   max  equality residual
  dom       % of the other algorithm's front dominated by IDC

Targets:
  MOEED13   Sum(P_i)        == 1800        MW   (physical demand equality)
  Concrete  Sum(ingredients) == 2325.012558 kg/m^3  (mean age-28 density;
            a fixed-to-mean modeling choice, not a physical equality)

Outputs:
  - prints a table per (example, formulation)
  - writes extra_results/mo_matched_budget_summary.csv  (machine-readable)
  - writes figures/fig_normhv_<example>_<form>.{pdf,png}

    python mo_matched_budget.py

Reproduces the numbers in Tables tab:case_moeed13 / tab:case_concrete_mo and the
band-formulation residual tables.
"""
from __future__ import annotations
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
ROOT = HERE.parent
EXAMPLES = ROOT / "examples"
OUTFIG = HERE / "figures"
OUTCSV = HERE / "extra_results" / "mo_matched_budget_summary.csv"
ENG_TOL = 0.5   # engineering feasibility tolerance on the equality residual

# Per-example wiring. `idc_obj` maps an IDC result.csv row to (f0, f1) in the
# same orientation pymoo uses (both minimized internally for the HV staircase).
CASES = {
    "moeed13": dict(
        dir="moeed13", prefix="moeed13", target=1800.0, nvars=13,
        idc_cols=("total_cost", "total_emission"),
        idc_sum=lambda r: sum(float(r[f"P_{i}"]) for i in range(13)),
        # both objectives minimized; smaller is better on both axes
        sense=("min", "min"),
        axis_labels=(r"total cost [\$/h]", r"NO$_x$ [lb/h]"),
        title="MOEED13 (economic-emission dispatch)",
    ),
    "concrete_uci_mo": dict(
        dir="concrete_uci_mo", prefix="", target=2325.012558, nvars=7,
        idc_cols=("strength", "cement"),
        idc_sum=lambda r: sum(float(r["x_" + c]) for c in
                              ("cement", "slag", "fly_ash", "water", "sp",
                               "coarse_agg", "fine_agg")),
        # strength maximized, cement minimized
        sense=("max", "min"),
        axis_labels=("strength [MPa]", r"cement [kg/m$^3$]"),
        title="UCI Concrete (max strength / min cement)",
    ),
}


def _load(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _load_front(sub):
    """IDC front: prefer the freshly produced result.csv (gitignored), fall
    back to the committed expected_output.csv so a clean clone regenerates the
    figures/tables without first rebuilding and running the binary."""
    p = sub / "result.csv"
    if not p.exists():
        p = sub / "expected_output.csv"
    return _load(p)


def _idc_FP(case, rows):
    """Return F (n,2) in (min,min) orientation + per-row variable sum."""
    c0, c1 = case["idc_cols"]
    F = np.array([[float(r[c0]), float(r[c1])] for r in rows], float)
    S = np.array([case["idc_sum"](r) for r in rows], float)
    # flip maximized axes to minimized so the HV staircase is uniform
    for j, s in enumerate(case["sense"]):
        if s == "max":
            F[:, j] = -F[:, j]
    return F, S


def _nsga_FP(case, rows, algo, nvars):
    rr = [r for r in rows if r["algorithm"] == algo]
    if not rr:
        return np.empty((0, 2)), np.empty(0)
    # pymoo F_0/F_1 are already in min/min orientation (maximize stored negated)
    F = np.array([[float(r["F_0"]), float(r["F_1"])] for r in rr], float)
    S = np.array([sum(float(r[f"x_{i}"]) for i in range(nvars)) for r in rr], float)
    return F, S


def _nondom_min(F):
    pts = sorted(set(map(tuple, F)))
    res, best = [], None
    for a, b in pts:
        if best is None or b < best:
            res.append((a, b)); best = b
    return res


def _dom_frac(A, B):
    if len(A) == 0 or len(B) == 0:
        return float("nan")
    c = sum(1 for b in B if np.any((A[:, 0] <= b[0]) & (A[:, 1] <= b[1]) &
                                    ((A[:, 0] < b[0]) | (A[:, 1] < b[1]))))
    return 100.0 * c / len(B)


def _norm_and_hv(fronts, bounds=None):
    # Reference box. When `bounds` is supplied, every formulation is scored
    # against the SAME fixed corners (the single-seed full-data equality run
    # defines them; see main()), so an algorithm's normalized HV does not drift
    # between the equality/band/mixed comparisons and IDC's value is constant.
    # With bounds=None the legacy per-call union reference is used.
    if bounds is None:
        allp = [p for F in fronts.values() for p in F]
        amin, amax = min(p[0] for p in allp), max(p[0] for p in allp)
        bmin, bmax = min(p[1] for p in allp), max(p[1] for p in allp)
    else:
        amin, amax, bmin, bmax = bounds

    def _c(v):  # clip to the fixed reference box
        return 0.0 if v < 0.0 else (1.0 if v > 1.0 else v)

    def norm(F):
        return [(_c((amax - a) / (amax - amin)) if amax > amin else 1.0,
                 _c((bmax - b) / (bmax - bmin)) if bmax > bmin else 1.0) for a, b in F]

    def hv(Q):
        Qs = sorted(set(Q), key=lambda p: (p[0], -p[1]))
        res, best = [], None
        for x, y in reversed(Qs):
            if best is None or y > best:
                res.append((x, y)); best = y
        area, last = 0.0, 0.0
        for x, y in sorted(res, key=lambda p: -p[0]):
            if y > last:
                area += x * (y - last); last = y
        return area
    return norm, hv, (amin, amax, bmin, bmax)


def _residual(S, target):
    d = np.abs(S - target)
    feas = 100.0 * np.mean(d <= ENG_TOL) if len(d) else float("nan")
    return feas, (float(d.mean()) if len(d) else float("nan")), \
        (float(d.max()) if len(d) else float("nan"))


def process(name, case, form, fixed_bounds=None):
    # Comparison modes:
    #   "equality" — IDC + NSGA both under the equality (NSGA collapses).
    #   "band"     — IDC + NSGA both under the tolerance band.
    #   "mixed"    — IDC under the EQUALITY vs NSGA under the BAND (the population
    #                baselines cannot sample the measure-zero equality set, so the
    #                band is the most generous formulation we can give them; every
    #                residual is still scored against the equality target, which is
    #                the physically meaningful constraint — for concrete, fixing the
    #                recipe proportions independent of the total batch quantity).
    pref = (case["prefix"] + "_") if case["prefix"] else ""
    base = EXAMPLES / case["dir"]
    if form == "equality":
        idc_sub, nsga_sub = base, base
    elif form == "band":
        idc_sub, nsga_sub = base / "band", base / "band"
    else:  # mixed
        idc_sub, nsga_sub = base, base / "band"
    idc_rows = _load_front(idc_sub)
    nsga_rows = _load(nsga_sub / f"{pref}pymoo_fronts.csv")
    idcF, idcS = _idc_FP(case, idc_rows)
    n2F, n2S = _nsga_FP(case, nsga_rows, "nsga2", case["nvars"])
    n3F, n3S = _nsga_FP(case, nsga_rows, "nsga3", case["nvars"])
    fronts = {"IDC": _nondom_min(idcF), "NSGA2": _nondom_min(n2F), "NSGA3": _nondom_min(n3F)}
    norm, hv, used_bounds = _norm_and_hv(fronts, fixed_bounds)
    rows_out = []
    for algo, F, S in [("IDC", idcF, idcS), ("NSGA2", n2F, n2S), ("NSGA3", n3F, n3S)]:
        feas, rmean, rmax = _residual(S, case["target"])
        rows_out.append(dict(
            example=name, formulation=form, algorithm=algo,
            n_points=len(F), n_unique=len(set(map(tuple, F))),
            normHV=round(hv(norm(fronts[algo])), 4),
            feas_eng_pct=round(feas, 1), res_mean=rmean, res_max=rmax,
        ))
    dom_n2 = _dom_frac(idcF, n2F)
    dom_n3 = _dom_frac(idcF, n3F)
    idc_dominated = _dom_frac(np.vstack([n2F, n3F]) if len(n2F) + len(n3F) else n2F, idcF)
    for r in rows_out:
        if r["algorithm"] == "IDC":
            r["idc_dom_nsga2_pct"] = round(dom_n2, 1)
            r["idc_dom_nsga3_pct"] = round(dom_n3, 1)
            r["idc_dominated_pct"] = round(idc_dominated, 2)
    _figure(name, case, form, fronts, norm, hv)
    return rows_out, used_bounds


def _figure(name, case, form, fronts, norm, hv):
    plt.rcParams.update({
        "font.family": "serif", "font.size": 9, "axes.titlesize": 10,
        "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.25,
    })
    greys = {"IDC": "0.50", "NSGA2": "0.68", "NSGA3": "0.82"}
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4), sharey=True)
    for ax, nm in zip(axes, ["IDC", "NSGA2", "NSGA3"]):
        Q = norm(fronts[nm])
        Q = sorted(set(Q))
        xs = [0.0] + [p[0] for p in Q]
        ys = [p[1] for p in Q] + [0.0]
        ax.fill_between(xs, ys, step="post", facecolor=greys[nm],
                        edgecolor="0.30", linewidth=0.8)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.set_title(f"{nm}\nnorm. HV = {hv(norm(fronts[nm])):.3f}  (|PF|={len(fronts[nm])})")
        ax.set_xlabel(f"{case['axis_labels'][0]}  (norm., 1=best)")
    axes[0].set_ylabel(f"{case['axis_labels'][1]}  (norm., 1=best)")
    fig.suptitle(f"{case['title']} — {form} formulation — normalized HV (matched 400k budget)")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    OUTFIG.mkdir(exist_ok=True)
    # Equality is the headline formulation -> canonical figure name the
    # manuscript references; band/mixed get suffixes.
    suffix = {"equality": "", "band": "_band", "mixed": "_mixed"}[form]
    for ext in ("pdf", "png"):
        fig.savefig(OUTFIG / f"fig_normhv_{name}{suffix}.{ext}", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    OUTCSV.parent.mkdir(parents=True, exist_ok=True)
    all_rows = []
    for name, case in CASES.items():
        # Fixed reference box, computed ONCE from the equality formulation (the
        # canonical single-seed full-data run) and reused for every formulation,
        # so each algorithm is scored against the same corners and IDC's HV does
        # not drift between the equality/band/mixed comparisons.
        _, fixed_bounds = process(name, case, "equality")
        for form in ("equality", "band", "mixed"):
            rows, _ = process(name, case, form, fixed_bounds=fixed_bounds)
            all_rows.extend(rows)
            print("=" * 78)
            print(f"{name}  —  {form.upper()}  (target Sum = {case['target']})")
            print("=" * 78)
            print(f"  {'algo':6} {'|PF|':>6} {'uniq':>6} {'normHV':>7} "
                  f"{'feas%@0.5':>9} {'res_mean':>10} {'res_max':>10}")
            for r in rows:
                print(f"  {r['algorithm']:6} {r['n_points']:6d} {r['n_unique']:6d} "
                      f"{r['normHV']:7.3f} {r['feas_eng_pct']:9.1f} "
                      f"{r['res_mean']:10.2e} {r['res_max']:10.2e}")
            idc = rows[0]
            print(f"  IDC dominates NSGA2 {idc.get('idc_dom_nsga2_pct')}% / "
                  f"NSGA3 {idc.get('idc_dom_nsga3_pct')}%  | "
                  f"IDC dominated {idc.get('idc_dominated_pct')}%\n")
    fields = ["example", "formulation", "algorithm", "n_points", "n_unique",
              "normHV", "feas_eng_pct", "res_mean", "res_max",
              "idc_dom_nsga2_pct", "idc_dom_nsga3_pct", "idc_dominated_pct"]
    with open(OUTCSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in all_rows:
            w.writerow({k: r.get(k, "") for k in fields})
    print(f"[OK] summary -> {OUTCSV}")
    print(f"[OK] figures -> {OUTFIG}/fig_normhv_<example>_<formulation>.pdf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
