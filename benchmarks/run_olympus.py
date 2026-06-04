#!/usr/bin/env python3
"""
Olympus real-data runner with a task switch.

The paper's §8.4 real-application case study uses the Olympus
`photo_pce10` task (organic-photovoltaic blend, simplex constraint). That
is the only Olympus task shown explicitly. Olympus ships many more
emulator-backed real datasets, and IDC was run across a catalog of them
during development; this driver exposes a `--task` switch so any of the
catalog tasks can be run. The default is the one shown in the paper.

The Olympus tasks reachable here (the catalog subset used by the authors):

    photo_pce10     OPV blend, minimize photo-degradation  (§8.4, default)
    alkox           alkoxylation yield
    benzylation     N-benzylation yield
    crossed_barrel  mechanical toughness
    fullerenes      fullerene synthesis yield
    hplc            HPLC peak response
    snar            nucleophilic aromatic substitution

Each task is run the same way as §8.4: a Growing-Neurons surrogate is
trained on the task's rows, then IDC and the pymoo/pycma baselines are run
against that *same* surrogate under the top-5% held-out protocol
(docs/holdout_procedure.md). The actual optimization is delegated to the
built example binary (preferred) or the shared Python harness; this script
owns task selection, surrogate training, seeds, and result aggregation.

Examples
--------
    python run_olympus.py                        # §8.4 (photo_pce10)
    python run_olympus.py --list-tasks
    python run_olympus.py --task snar            # a task NOT shown in the paper
    python run_olympus.py --task alkox --objective so --seeds 21

Output
------
    results/olympus/<task>_idc_vs_baselines.csv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).parent

# Olympus catalog subset. Only photo_pce10 is shown explicitly in §8.4;
# the rest are reachable via --task but reported only in this repo.
TASKS = {
    "photo_pce10": "OPV blend, minimize photo-degradation (paper Sec 8.4, default).",
    "alkox": "Alkoxylation yield.",
    "benzylation": "N-benzylation yield.",
    "crossed_barrel": "Mechanical toughness of a printed barrel.",
    "fullerenes": "Fullerene synthesis yield.",
    "hplc": "HPLC peak response.",
    "snar": "Nucleophilic aromatic substitution (SNAr) yield.",
}
DEFAULT_TASK = "photo_pce10"

# Which baseline pool to use. photo_pce10 is reported single-objective in
# the paper; other Olympus tasks can be run in either mode.
DEFAULT_OBJECTIVE = "so"
SO_BASELINES = ["cmaes", "de", "ga", "pso"]
MO_BASELINES = ["nsga2", "nsga3", "moead"]


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Run an Olympus real-data task (IDC vs baselines).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--task",
        choices=sorted(TASKS),
        default=DEFAULT_TASK,
        help=f"Olympus task to run (default: {DEFAULT_TASK}, the one shown in Sec 8.4).",
    )
    p.add_argument(
        "--objective",
        choices=["so", "mo"],
        default=DEFAULT_OBJECTIVE,
        help="Single- or multi-objective formulation (default: so).",
    )
    p.add_argument(
        "--seeds",
        type=int,
        default=21,
        help="Independent optimizer seeds per (task, algorithm) cell (default: 21, the paper value).",
    )
    p.add_argument(
        "--budget",
        type=int,
        default=40_000,
        help="Surrogate evaluations per seed (default: 40000, the paper §8.4 budget). "
        "IDC defaults: N=2000 candidates/iter, gamma=0.85 zoom, I_max in 5..20, "
        "I_min=4, tau=1e-6 (see docs/reproducing.md).",
    )
    p.add_argument(
        "--surrogate-seeds",
        type=int,
        default=5,
        help="Held-out surrogate-training seeds (default: 5, the top-5%% protocol).",
    )
    p.add_argument(
        "--holdout",
        type=float,
        default=0.05,
        help="Top fraction held out by objective value (default: 0.05).",
    )
    p.add_argument(
        "--algorithms",
        nargs="+",
        default=None,
        help="Override the algorithm list (default: idc + the objective-appropriate baselines).",
    )
    p.add_argument(
        "--list-tasks",
        action="store_true",
        help="Print the available Olympus tasks and exit.",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output CSV path (default: results/olympus/<task>_idc_vs_baselines.csv).",
    )
    return p.parse_args(argv)


def require_olympus():
    try:
        import olympus  # noqa: F401
    except ImportError:
        sys.exit(
            "The 'olympus' package is required to materialize the task datasets\n"
            "but is not installed.\n\n"
            "  pip install olympus            # from aspuru-guzik-group/olympus\n\n"
            "Alternatively, drop a pre-exported CSV at\n"
            "  ../data/olympus/<task>/<task>.csv\n"
            "and re-run; the loader uses the local copy when present.\n"
        )
    import olympus

    return olympus


def main(argv=None) -> int:
    args = parse_args(argv)

    if args.list_tasks:
        print("Available Olympus tasks (--task):")
        for name, desc in TASKS.items():
            marker = "  (default)" if name == DEFAULT_TASK else ""
            print(f"  {name:<16} {desc}{marker}")
        return 0

    task = args.task
    baselines = SO_BASELINES if args.objective == "so" else MO_BASELINES
    algorithms = args.algorithms or (["idc"] + baselines)
    out_path = args.out or (HERE / "results" / "olympus" / f"{task}_idc_vs_baselines.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[task]       {task}  ({args.objective.upper()})")
    print(f"[algorithms] {', '.join(algorithms)}")
    print(f"[budget]     {args.budget} surrogate evals/seed")
    print(f"[holdout]    top-{args.holdout:.0%}, {args.surrogate_seeds} surrogate seeds, "
          f"{args.seeds} optimizer seeds")
    print(f"[out]        {out_path}")
    if task != DEFAULT_TASK:
        print(f"[note]       '{task}' is NOT shown explicitly in the manuscript; "
              "Sec 8.4 reports only photo_pce10.")

    # Load (or materialize) the task dataset, train the held-out surrogate(s),
    # and run IDC + baselines. Delegated to the shared harness so this script
    # stays focused on task selection and switches.
    require_olympus()
    from olympus_runner import run_task  # type: ignore

    run_task(
        task=task,
        objective=args.objective,
        algorithms=algorithms,
        seeds=args.seeds,
        budget=args.budget,
        surrogate_seeds=args.surrogate_seeds,
        holdout=args.holdout,
        out_path=out_path,
        data_dir=HERE.parent / "data" / "olympus" / task,
    )

    print(f"\n[OK] wrote {out_path}")
    print("Aggregate with: python aggregate_21seeds.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
