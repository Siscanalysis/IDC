"""
paper_style.py — single source of truth for the paper figure look.

  from paper_style import apply_style, palette, marker_cycle
  apply_style()        # B/W by default (set IDC_PAPER_BW=0 to switch to color)
  colors = palette(4)  # 4 colors / greys
  markers = marker_cycle()

Flip the whole paper to color by setting IDC_PAPER_BW=0 in the shell env
before running figure scripts, or by editing the default in this file.
"""
from __future__ import annotations
import os
import itertools
import matplotlib as mpl
import matplotlib.pyplot as plt


def is_bw() -> bool:
    """B/W mode = default unless IDC_PAPER_BW is explicitly set to 0/false/off."""
    val = os.environ.get("IDC_PAPER_BW", "1").lower()
    return val not in ("0", "false", "off", "no")


def apply_style() -> None:
    """Apply paper-wide matplotlib style. Idempotent — call once at script start."""
    mpl.rcParams.update({
        "font.family":       "serif",
        "font.size":         9,
        "axes.titlesize":    10,
        "axes.labelsize":    9,
        "legend.fontsize":   8,
        "xtick.labelsize":   8,
        "ytick.labelsize":   8,
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "axes.grid":         True,
        "grid.alpha":        0.25,
        "grid.linestyle":    "-",
        "lines.linewidth":   1.3,
        "lines.markersize":  4,
        "figure.dpi":        150,
        "savefig.dpi":       300,
        "savefig.bbox":      "tight",
    })


def palette(n: int) -> list[str]:
    """Return n distinguishable colors / greys."""
    if is_bw():
        if n <= 1:
            return ["0.15"]
        step = (0.65 - 0.05) / (n - 1)
        return [f"{0.05 + i * step:.3f}" for i in range(n)]
    color_pool = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd",
                  "#ff7f0e", "#17becf", "#8c564b", "#e377c2"]
    return color_pool[:n]


def marker_cycle() -> itertools.cycle:
    """Return a fresh marker iterator for line + scatter plots."""
    return itertools.cycle(["o", "s", "^", "D", "v", "p", "X", "*"])


def linestyle_cycle() -> itertools.cycle:
    """For B/W mode, line styles do most of the differentiation work."""
    return itertools.cycle(["-", "--", "-.", ":", (0, (3, 1, 1, 1))])
