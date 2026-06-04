#!/usr/bin/env python3
"""
make_figures.py — regenerate the paper's §8 multi-objective figures from the
committed result CSVs.

Self-contained: reads only files shipped in this repository
(`examples/<case>/expected_output.csv` and `benchmarks/extra_results/*.csv`),
so it runs from a clean clone with just numpy + pandas + matplotlib — no sweep
or build step required. The §8.4 photo_pce10 convergence figure is rendered
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


def pareto_concrete() -> None:
    """§8.5 UCI Concrete MO Pareto front (strength vs cement)."""
    csv = EXAMPLES / "concrete_uci_mo" / "expected_output.csv"
    if not csv.exists():
        print(f"[skip] {csv} (run ./bin/concrete_uci_mo first)")
        return
    df = pd.read_csv(csv)
    fig, ax = plt.subplots(figsize=(4.2, 3.2))
    ax.scatter(df["cement"], df["strength"], s=4, color=palette(1)[0], alpha=0.55,
               label=f"IDC front ({len(df)} pts)")
    ax.axhline(81.75, ls=":", color="0.4", lw=1.0, label="data ceiling 81.75 MPa")
    ax.set_xlabel(r"cement [kg/m$^3$]  (minimize)")
    ax.set_ylabel("predicted strength [MPa]  (maximize)")
    ax.set_title("UCI Concrete MO — Pareto front (§8.5)")
    ax.legend(loc="lower right")
    _save(fig, "fig_pareto_concrete")


def pareto_moeed13() -> None:
    """§8.3 MOEED13 cost-emission Pareto front."""
    csv = EXAMPLES / "moeed13" / "expected_output.csv"
    if not csv.exists():
        print(f"[skip] {csv} (run ./bin/moeed13 first)")
        return
    df = pd.read_csv(csv)
    fig, ax = plt.subplots(figsize=(4.2, 3.2))
    ax.scatter(df["total_cost"], df["total_emission"], s=4, color=palette(1)[0],
               alpha=0.55, label=f"IDC front ({len(df)} pts)")
    ax.set_xlabel(r"total cost [\$/h]  (minimize)")
    ax.set_ylabel("total emission [lb/h]  (minimize)")
    ax.set_title("MOEED13 — cost/emission Pareto front (§8.3)")
    ax.legend(loc="upper right")
    _save(fig, "fig_pareto_moeed13")


def mo_catalog_hv() -> None:
    """Mean hypervolume per algorithm across the MO catalog (extra_results)."""
    csv = EXTRA / "mo_catalog_hv_igd.csv"
    if not csv.exists():
        print(f"[skip] {csv} missing")
        return
    df = pd.read_csv(csv)
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
    print("Note: the §8.4 photo_pce10 convergence figure is rendered by "
          "make_convergence_figure.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
