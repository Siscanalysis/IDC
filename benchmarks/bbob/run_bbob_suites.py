#!/usr/bin/env python3
"""
COCO/BBOB suite driver for the §8.2 analytical validation.

The paper reports IDC against NSGA-II / NSGA-III / MOEA/D on *every* COCO
suite, but shows only the bi-objective mixed-integer suite explicitly
(§8.2), because that is the analytical regime where IDC's combination of
categorical block elimination and affine repair translates into a
decisive advantage. The other four suites are summarized qualitatively in
§7.3 and reported in full only here in the companion repository.

This driver exposes a `--suite` switch so any of the five COCO suites can
be run. The default is the one shown in the manuscript.

    bbob                  continuous single-objective       (24 functions)
    bbob-mixint           single-objective mixed-integer
    bbob-constrained      single-objective constrained
    bbob-biobj            continuous bi-objective
    bbob-biobj-mixint     bi-objective mixed-integer        (§8.2, default)

Suites are provided by the official COCO `cocoex` binding. cocoex is an
optional dependency (it does not build on every Python version); when it
is missing this script prints an actionable message instead of failing
silently. For the hard-multimodal f15--f24 stress test reported in §7.3
(which runs without COCO, on canonical analytical forms) use the sibling
script `run_bbob_stress.py`.

Examples
--------
    # §8.2 as shown in the paper (default suite)
    python run_bbob_suites.py

    # a suite NOT shown explicitly in the manuscript
    python run_bbob_suites.py --suite bbob-mixint
    python run_bbob_suites.py --suite bbob --dimensions 5 10 20

Output
------
    results/<suite>/<suite>_idc_vs_pymoo.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent

# The five COCO suites. Only bbob-biobj-mixint is shown explicitly in §8.2;
# the others are reachable via --suite but are reported only in this repo.
SUITES = {
    "bbob": "Continuous single-objective (24 noiseless functions).",
    "bbob-mixint": "Single-objective mixed-integer.",
    "bbob-constrained": "Single-objective constrained.",
    "bbob-biobj": "Continuous bi-objective.",
    "bbob-biobj-mixint": "Bi-objective mixed-integer (paper Sec 8.2, default).",
}
DEFAULT_SUITE = "bbob-biobj-mixint"

# Dimension cohort used in §8.2. COCO-default dimensions per suite differ;
# pass --dimensions to override (the suite filters to those it supports).
DEFAULT_DIMENSIONS = [5, 10, 20, 40, 80, 160]

# Multi-objective suites use the pymoo MO baselines; single-objective
# suites use the pymoo SO baselines + pycma. IDC is always included.
MO_BASELINES = ["nsga2", "nsga3", "moead"]
SO_BASELINES = ["de", "ga", "pso", "cmaes"]


def is_multiobjective(suite: str) -> bool:
    return "biobj" in suite


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Run a COCO/BBOB suite (IDC vs pymoo baselines).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--suite",
        choices=sorted(SUITES),
        default=DEFAULT_SUITE,
        help=f"COCO suite to run (default: {DEFAULT_SUITE}, the one shown in §8.2).",
    )
    p.add_argument(
        "--dimensions",
        type=int,
        nargs="+",
        default=None,
        help=f"Dimensions to run (default: {DEFAULT_DIMENSIONS}, filtered to "
        "those the suite supports).",
    )
    p.add_argument(
        "--seeds",
        type=int,
        default=21,
        help="Independent seeds per (function, dimension, instance) cell (default: 21).",
    )
    p.add_argument(
        "--algorithms",
        nargs="+",
        default=None,
        help="Override the algorithm list (default: IDC + the suite-appropriate "
        "pymoo/pycma baselines).",
    )
    p.add_argument(
        "--list-suites",
        action="store_true",
        help="Print the available suites and exit.",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output CSV path (default: results/<suite>/<suite>_idc_vs_pymoo.csv).",
    )
    return p.parse_args(argv)


def require_cocoex():
    try:
        import cocoex  # noqa: F401
    except ImportError:
        sys.exit(
            "cocoex (the official COCO binding) is required for the COCO-suite\n"
            "sweep but is not installed in this environment.\n\n"
            "  pip install cocoex            # may be unavailable on the newest Python\n"
            "  conda install -c conda-forge coco   # alternative\n\n"
            "If cocoex will not install, the f15--f24 hard-multimodal stress test\n"
            "reported in Sec 7.3 runs WITHOUT COCO via canonical analytical forms:\n"
            "  python run_bbob_stress.py\n"
        )
    import cocoex

    return cocoex


def main(argv=None) -> int:
    args = parse_args(argv)

    if args.list_suites:
        print("Available COCO suites (--suite):")
        for name, desc in SUITES.items():
            marker = "  (default, shown in Sec 8.2)" if name == DEFAULT_SUITE else ""
            print(f"  {name:<20} {desc}{marker}")
        return 0

    suite = args.suite
    mo = is_multiobjective(suite)
    dims = args.dimensions or DEFAULT_DIMENSIONS
    algorithms = args.algorithms or (["idc"] + (MO_BASELINES if mo else SO_BASELINES))

    out_path = args.out or (HERE / "results" / suite / f"{suite}_idc_vs_pymoo.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[suite]      {suite}  ({'MO' if mo else 'SO'})")
    print(f"[dimensions] {dims}")
    print(f"[algorithms] {', '.join(algorithms)}")
    print(f"[seeds]      {args.seeds}")
    print(f"[out]        {out_path}")
    if suite != DEFAULT_SUITE:
        print(
            f"[note]       '{suite}' is NOT shown explicitly in the manuscript; "
            "Sec 8.2 reports only bbob-biobj-mixint."
        )

    cocoex = require_cocoex()
    coco_suite = cocoex.Suite(suite, "", "")

    # The per-problem optimization is delegated to the shared runner used by
    # the rest of the benchmark suite (IDC via the built OpenNN binary or the
    # reference Python IDC; pymoo/pycma for the baselines). The runner is
    # imported lazily so --list-suites works without the heavy deps.
    from coco_runner import run_problem  # type: ignore

    with open(out_path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            ["suite", "function", "dimension", "instance", "algorithm", "seed",
             "best_ert_win", "hv", "walltime_s"]
        )
        for problem in coco_suite:
            if problem.dimension not in dims:
                continue
            for algo in algorithms:
                for seed in range(args.seeds):
                    t0 = time.time()
                    rec = run_problem(problem, algo, seed, multiobjective=mo)
                    dt = time.time() - t0
                    writer.writerow([
                        suite, problem.id_function, problem.dimension,
                        problem.id_instance, algo, seed,
                        rec.get("best_ert_win", ""), rec.get("hv", ""),
                        f"{dt:.3f}",
                    ])
                    fh.flush()
            print(f"[done] {problem.id} ({problem.dimension}D)")

    print(f"\n[OK] wrote {out_path}")
    print("Aggregate per-suite win/tie/loss with: python ../aggregate_21seeds.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
