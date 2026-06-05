"""
parse_cocopp_idc_wins.py

Walk the five BBOB/COCO suites,
read each pptables_f<NN>_<D>D.tex per (function, dimension) cell, and emit:

  results/per_function_idc_wins.csv   ← (suite, fn, dim, idc_ratio, idc_wins_count, total_targets, baselines_bold)
  results/summary_idc_wins.csv        ← per (suite, dim): wins, losses, ties
  results/headline_idc_wins.csv       ← top-N functions where IDC wins (mention-worthy in §7.6)

Algorithm-row mapping per suite (verified from legend in ppfigs.tex):
  bbob, bbob-mixint, bbob-constrained:    A=cmaes, B=de, C=ga, D=pso, E=idc
  bbob-biobj, bbob-biobj-mixint:          A=nsga2, B=nsga3, C=moead, D=idc

A cell entry like "\textbf{4} \textbf{.0}\mbox{\tiny (2)}" indicates the algorithm has the
best (smallest) ERT at that target precision — i.e., a win at that target.

We count, per (function, dim), how many of the target-precision columns IDC has the bold
(winning) entry. A function counts as an "IDC win" if IDC has bold at at least one target.
"""
from __future__ import annotations

import os
import re
import csv
from pathlib import Path
from collections import defaultdict

# Raw cocopp post-processing output (per-function pptables_*.tex). Author-workspace
# only: the PARSED result (results/summary_idc_wins.csv etc., committed) is the
# reproducible §7.2/§7.6 artifact; set BBOB_PPDATA only to re-parse from scratch.
PPDATA = Path(os.environ.get("BBOB_PPDATA", "ppdata"))

OUT = Path(__file__).parent / "results"
OUT.mkdir(parents=True, exist_ok=True)

# (suite-folder-prefix, user-folder, algorithm row index for IDC zero-indexed, suite-label)
SUITES = [
    ("exdat_exdat_exdat_exdat_",            "User_052922h4314", 4, "bbob"),
    ("mixint_exdat_exdat_exdat_exdat_",     "User_052922h4607", 4, "bbob-mixint"),
    ("constrained_exdat_exdat_exdat_exdat_", "User_052922h5028", 4, "bbob-constrained"),
    ("biobj_exdat_exdat_exdat_",            "User_052922h5648", 3, "bbob-biobj"),
    ("biobj-mixint_exdat_exdat_exdat_",     "User_052923h0302", 3, "bbob-biobj-mixint"),
]

# Each target-precision cell with a WINNER renders as two adjacent \textbf{} groups
# separated by a column break: \textbf{<int>} & \textbf{<decimal-or-empty>}.
# We exclude bolded $\infty$ entries — those appear inside \multicolumn cells when
# ALL algorithms fail at that target, which carries no relative-performance signal.
NUMERIC_BOLD_PAIR = re.compile(
    r"\\textbf\{(?!\$\\infty\$)[^}]*\}\s*&\s*\\textbf\{(?!\$\\infty\$)[^}]*\}"
)

# Filename pattern: pptables_f001_05D.tex .. f024_40D.tex
FILE_RE = re.compile(r"pptables_f(\d{3})_(\d+)D\.tex$")


def parse_file(path: Path, idc_row_idx: int) -> tuple[int, int]:
    """Return (idc_numeric_wins, total_resolved_targets) for the table.

    A *resolved* target is one in which at least one algorithm produced a
    finite ERT (i.e., reached the target). Targets where every algorithm
    returned $\\infty$ carry no relative-performance signal and are excluded.
    """
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    body_rows = [l for l in lines if l.startswith("\\alg") and "tables" in l]
    if idc_row_idx >= len(body_rows):
        return 0, 0
    idc_line = body_rows[idc_row_idx]
    idc_wins = len(NUMERIC_BOLD_PAIR.findall(idc_line))
    # Total resolved targets = total numeric bold pairs across ALL algorithm rows.
    # Each resolved target has exactly one winner ⇒ exactly one numeric bold pair.
    total_resolved = sum(len(NUMERIC_BOLD_PAIR.findall(r)) for r in body_rows)
    return idc_wins, total_resolved


def main() -> None:
    per_function_rows = []
    summary_counts: dict[tuple[str, int], dict[str, int]] = defaultdict(
        lambda: {"wins": 0, "losses": 0, "ties": 0, "total_fn_dim": 0,
                 "idc_targets_won": 0, "total_targets": 0}
    )

    for prefix, user, idc_idx, label in SUITES:
        suite_dir = PPDATA / prefix / user
        if not suite_dir.exists():
            print(f"[skip] {label}: {suite_dir} missing")
            continue
        files = sorted(suite_dir.glob("pptables_f*_*D.tex"))
        for f in files:
            m = FILE_RE.search(f.name)
            if not m:
                continue
            fn = int(m.group(1))
            dim = int(m.group(2))
            idc_bold, total = parse_file(f, idc_idx)
            ratio = idc_bold / total if total > 0 else 0.0
            verdict = (
                "win" if idc_bold > total / 2
                else "tie" if idc_bold > 0
                else "loss"
            )
            per_function_rows.append({
                "suite": label, "fn": fn, "dim": dim,
                "idc_wins": idc_bold, "total_targets": total,
                "win_ratio": round(ratio, 3), "verdict": verdict,
            })
            key = (label, dim)
            summary_counts[key]["total_fn_dim"] += 1
            summary_counts[key]["idc_targets_won"] += idc_bold
            summary_counts[key]["total_targets"] += total
            if verdict == "win":
                summary_counts[key]["wins"] += 1
            elif verdict == "loss":
                summary_counts[key]["losses"] += 1
            else:
                summary_counts[key]["ties"] += 1

    # Per-function output
    per_fn_csv = OUT / "per_function_idc_wins.csv"
    with per_fn_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["suite", "fn", "dim", "idc_wins",
                                          "total_targets", "win_ratio", "verdict"])
        w.writeheader()
        w.writerows(per_function_rows)
    print(f"[ok] wrote {per_fn_csv} ({len(per_function_rows)} rows)")

    # Per-suite-dim summary
    summary_csv = OUT / "summary_idc_wins.csv"
    with summary_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["suite", "dim", "n_functions", "idc_wins", "idc_ties", "idc_losses",
                    "idc_target_cells_won", "total_target_cells", "cell_win_ratio"])
        for (label, dim), counts in sorted(summary_counts.items()):
            cell_ratio = counts["idc_targets_won"] / counts["total_targets"] \
                if counts["total_targets"] > 0 else 0.0
            w.writerow([label, dim, counts["total_fn_dim"],
                        counts["wins"], counts["ties"], counts["losses"],
                        counts["idc_targets_won"], counts["total_targets"],
                        round(cell_ratio, 3)])
    print(f"[ok] wrote {summary_csv}")

    # Headline: top IDC-wins functions across the whole catalog, sorted by win_ratio desc
    headline = [r for r in per_function_rows if r["verdict"] == "win"]
    headline.sort(key=lambda r: (-r["win_ratio"], -r["idc_wins"], r["suite"], r["fn"], r["dim"]))
    headline_csv = OUT / "headline_idc_wins.csv"
    with headline_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["suite", "fn", "dim", "idc_wins",
                                          "total_targets", "win_ratio", "verdict"])
        w.writeheader()
        w.writerows(headline)
    print(f"[ok] wrote {headline_csv} ({len(headline)} winning (fn,dim) cells)")

    # Console summary
    print("\n=== Per-suite-dim summary ===")
    print(f"{'suite':22s} {'dim':>3s} {'n_fn':>5s} {'wins':>5s} {'ties':>5s} {'loss':>5s} {'cell_win%':>10s}")
    for (label, dim), counts in sorted(summary_counts.items()):
        cell_pct = 100 * counts["idc_targets_won"] / counts["total_targets"] \
            if counts["total_targets"] > 0 else 0.0
        print(f"{label:22s} {dim:>3d} {counts['total_fn_dim']:>5d} "
              f"{counts['wins']:>5d} {counts['ties']:>5d} {counts['losses']:>5d} "
              f"{cell_pct:>9.1f}%")


if __name__ == "__main__":
    main()
