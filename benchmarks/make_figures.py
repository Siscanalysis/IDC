#!/usr/bin/env python3
"""
make_figures.py — render this companion's §7 multi-objective illustration
figures from the committed result CSVs.

Scope: views reproducible from the bundled artifacts — the concrete and MOEED13
front-vs-front overlays (IDC's dense equality front from each example's
expected_output.csv, against the band-relaxed NSGA-II/III fronts bundled in
examples/<case>/band/<prefix>pymoo_fronts.csv) plus a catalog-wide mean-HV bar
chart. The normalized-hypervolume panel figures are produced by
mo_matched_budget.py (which reads the same bundled band fronts).

Self-contained: reads only files shipped in this repository
(`examples/<case>/expected_output.csv` and `benchmarks/extra_results/*.csv`),
so it runs from a clean clone with just numpy + pandas + matplotlib — no sweep
or build step required. The §7.4 photo_pce10 convergence figure is rendered
separately by `make_convergence_figure.py`.

Outputs PDF + PNG into `benchmarks/figures/`.

    python make_figures.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent))
from paper_style import apply_style, palette  # noqa: E402

HERE = Path(__file__).parent
ROOT = HERE.parent
EXAMPLES = ROOT / "examples"
EXTRA = HERE / "extra_results"
OUT = HERE / "figures"


def _save(fig, name: str) -> None:
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=150)
    plt.close(fig)
    print(f"[fig] {name}.pdf / .png")


# Print-friendly grayscale markers for the front-vs-front overlays: IDC's dense
# equality front as small filled dots, the band-relaxed NSGA fronts as open
# markers so they stay legible on top of the IDC cloud.
_NSGA_STYLE = {
    "nsga2": dict(marker="^", s=26, facecolor="none", edgecolor="0.0",
                  linewidths=0.9, label_name="NSGA-II"),
    "nsga3": dict(marker="s", s=30, facecolor="none", edgecolor="0.30",
                  linewidths=0.9, label_name="NSGA-III"),
}


def _load_nsga_band(case_dir: str, prefix: str):
    """Return the band-formulation NSGA fronts as a DataFrame (or None)."""
    fronts = EXAMPLES / case_dir / "band" / f"{prefix}pymoo_fronts.csv"
    if not fronts.exists():
        print(f"[warn] {fronts} missing — overlay will show IDC only")
        return None
    return pd.read_csv(fronts)


def pareto_concrete() -> None:
    """UCI Concrete MO front-vs-front: IDC equality vs NSGA band."""
    csv = EXAMPLES / "concrete_uci_mo" / "expected_output.csv"
    if not csv.exists():
        print(f"[skip] {csv} (run ./bin/concrete_uci_mo first)")
        return
    df = pd.read_csv(csv)
    band = _load_nsga_band("concrete_uci_mo", "")
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    ax.scatter(df["cement"], df["strength"], s=4, color="0.55", alpha=0.55,
               label=f"IDC front (eq., {len(df)} pts)", zorder=2)
    if band is not None:
        # pymoo stores F_0 = -strength (maximize negated), F_1 = cement.
        for algo, st in _NSGA_STYLE.items():
            rr = band[band["algorithm"] == algo]
            if rr.empty:
                continue
            ax.scatter(rr["F_1"], -rr["F_0"], marker=st["marker"], s=st["s"],
                       facecolor=st["facecolor"], edgecolor=st["edgecolor"],
                       linewidths=st["linewidths"], zorder=3,
                       label=f"{st['label_name']} (band, {len(rr)} pts)")
    ax.axhline(81.75, ls=":", color="0.4", lw=1.0, label="data ceiling 81.75 MPa")
    ax.set_xlabel(r"cement [kg/m$^3$]  (minimize)")
    ax.set_ylabel("predicted strength [MPa]  (maximize)")
    ax.set_title("UCI Concrete MO — IDC equality vs NSGA band fronts")
    ax.legend(loc="lower right", fontsize=7)
    _save(fig, "fig_pareto_concrete")


def pareto_moeed13() -> None:
    """MOEED13 cost-emission front-vs-front: IDC equality vs NSGA band."""
    csv = EXAMPLES / "moeed13" / "expected_output.csv"
    if not csv.exists():
        print(f"[skip] {csv} (run ./bin/moeed13 first)")
        return
    df = pd.read_csv(csv)
    band = _load_nsga_band("moeed13", "moeed13_")
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    ax.scatter(df["total_cost"], df["total_emission"], s=4, color="0.55",
               alpha=0.55, label=f"IDC front (eq., {len(df)} pts)", zorder=2)
    if band is not None:
        # pymoo stores F_0 = total_cost, F_1 = total_emission (both minimized).
        for algo, st in _NSGA_STYLE.items():
            rr = band[band["algorithm"] == algo]
            if rr.empty:
                continue
            ax.scatter(rr["F_0"], rr["F_1"], marker=st["marker"], s=st["s"],
                       facecolor=st["facecolor"], edgecolor=st["edgecolor"],
                       linewidths=st["linewidths"], zorder=3,
                       label=f"{st['label_name']} (band, {len(rr)} pts)")
    ax.set_xlabel(r"total cost [\$/h]  (minimize)")
    ax.set_ylabel("total emission [lb/h]  (minimize)")
    ax.set_title("MOEED13 — IDC equality vs NSGA band fronts")
    ax.legend(loc="upper right", fontsize=7)
    _save(fig, "fig_pareto_moeed13")


def mo_catalog_hv() -> None:
    """Mean hypervolume per algorithm across the MO catalog (extra_results)."""
    csv = EXTRA / "mo_catalog_hv_igd.csv"
    if not csv.exists():
        print(f"[skip] {csv} missing")
        return
    df = pd.read_csv(csv)
    # Drop catalog rows with no model/HV (status meta:* -> algorithm "(meta)",
    # e.g. concrete_uci_mo and perovskite_database), so they don't show up as a
    # spurious NaN bar in the mean.
    df = df[df["hv"].notna() & ~df["algorithm"].astype(str).str.startswith("(meta)")]
    piv = df.groupby("algorithm")["hv"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(4.8, 3.0))
    ax.bar(range(len(piv)), piv.values, color=palette(len(piv)))
    ax.set_xticks(range(len(piv)))
    ax.set_xticklabels(piv.index, rotation=30, ha="right")
    ax.set_ylabel("mean hypervolume (catalog)")
    ax.set_title("MO catalog — mean HV per algorithm")
    _save(fig, "fig_mo_catalog_hv")


def main() -> int:
    apply_style()
    pareto_concrete()
    pareto_moeed13()
    mo_catalog_hv()
    print(f"[OK] figures written to {OUT}")
    print("Note: the §7.4 photo_pce10 convergence figure is rendered by "
          "make_convergence_figure.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
