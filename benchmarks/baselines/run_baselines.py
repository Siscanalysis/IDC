#!/usr/bin/env python3
"""
run_baselines.py — pymoo / pycma baselines for the §8 case studies, evaluated
on the SAME trained surrogate the C++ IDC binaries use, so the per-algorithm
feasibility and constraint-violation comparison reported in the §8.4 / §8.5
tables is reproducible from a clean clone.

What it records, per (algorithm, seed):
  - single-objective: best feasible objective (user units), feasibility, and the
    mean constraint-violation magnitude `max_violation` (how far the returned
    point is from satisfying the YAML constraints — the "how exactly does each
    method meet the equality" metric the paper reports);
  - multi-objective: front size, hypervolume (generic 1.1x-nadir reference),
    feasibility %, and the mean constraint violation over the returned front.

The surrogate is the bundled, self-contained numpy export
`examples/<example>/nn/<basename>.py` (same network as the `.json`/`.bin` the
C++ example loads). Constraints, bounds, and objectives are read from
`examples/<example>/problem.yaml` — the identical YAML the C++ driver uses, so
IDC and the baselines share one source of truth.

IDC's own row is recovered by re-checking the bundled `result.csv` (produced by
the matching C++ example) against the same constraint evaluator, rather than by
having the binary print the residual: this keeps a single constraint
implementation for every algorithm and needs no rebuild. Run the C++ example
first if you want the `idc` row.

SO pool: CMA-ES (pycma, via pymoo), DE, GA, PSO.
MO pool: NSGA-II, NSGA-III, and MOEA/D (the last only when the problem is
unconstrained, since pymoo's MOEA/D does not handle constraints).

Usage:
    python run_baselines.py --example photo_pce10     --seeds 21 --budget 40000
    python run_baselines.py --example concrete_uci_mo --seed  42 --budget 40000
    python run_baselines.py --example moeed13 --algo nsga2 --seed 42
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent          # benchmarks/baselines
ROOT = HERE.parents[1]                           # repo root
EXAMPLES = ROOT / "examples"
sys.path.insert(0, str(HERE))

from problem_pymoo import OpennnProblem          # bundled alongside this file

from pymoo.algorithms.soo.nonconvex.cmaes import CMAES
from pymoo.algorithms.soo.nonconvex.de import DE
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.algorithms.soo.nonconvex.pso import PSO
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.optimize import minimize
from pymoo.termination.max_eval import MaximumFunctionCallTermination
from pymoo.indicators.hv import HV


SO_ALGORITHMS = {
    "cmaes": lambda: CMAES(restarts=0),
    "de":    lambda: DE(),
    "ga":    lambda: GA(pop_size=100),
    "pso":   lambda: PSO(pop_size=100),
}


def load_nn(example: str, override=None):
    """Import the self-contained numpy NN export for an example, or, when
    `override` is given, a specific exported NN .py (used by the held-out
    driver to score a freshly trained surrogate)."""
    if override is not None:
        py = Path(override)
        if not py.exists():
            raise FileNotFoundError(f"--nn-py path not found: {py}")
    else:
        nn_dir = EXAMPLES / example / "nn"
        pys = sorted(nn_dir.glob("*.py"))
        if not pys:
            raise FileNotFoundError(
                f"No exported NN .py in {nn_dir}; the pymoo baselines evaluate the "
                f"surrogate through it.")
        py = pys[0]
    spec = importlib.util.spec_from_file_location(f"nn_{example}", py)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "NeuralNetwork"):
        raise AttributeError(f"{py} does not define class NeuralNetwork.")
    return mod.NeuralNetwork()


def _mo_algorithms(problem: OpennnProblem):
    n_obj = problem.n_obj
    ref = get_reference_directions("uniform", n_obj, n_partitions=max(12 - n_obj, 4))
    algos = {
        "nsga2": lambda: NSGA2(pop_size=100),
        "nsga3": lambda: NSGA3(pop_size=100, ref_dirs=ref),
    }
    if problem.n_ieq_constr == 0:
        algos["moead"] = lambda: MOEAD(ref_dirs=ref, n_neighbors=15,
                                       prob_neighbor_mating=0.7)
    return algos


def _n_eval(res, budget: int) -> int:
    try:
        return int(res.algorithm.evaluator.n_eval)
    except Exception:
        return budget


def run_so(problem: OpennnProblem, algo_name: str, seed: int, budget: int) -> dict:
    np.random.seed(seed)
    algo = SO_ALGORITHMS[algo_name]()
    t0 = time.perf_counter()
    res = minimize(problem, algo,
                   termination=MaximumFunctionCallTermination(budget),
                   seed=seed, save_history=True, verbose=False)
    walltime = time.perf_counter() - t0

    Xs, Fs, Gs = [], [], []
    def _add(pop):
        if pop is None or len(pop) == 0:
            return
        Xs.append(pop.get("X"))
        Fs.append(pop.get("F").reshape(-1, 1))
        g = pop.get("G")
        Gs.append(g if (g is not None and g.size > 0) else None)
    _add(res.pop)
    for h in (res.history or []):
        _add(h.pop)
    if not Xs:
        raise RuntimeError("pymoo returned no evaluated population.")

    X = np.vstack(Xs)
    F = np.vstack(Fs).ravel()
    if any(g is not None for g in Gs):
        G = np.vstack([np.zeros((len(x), problem.n_ieq_constr)) if g is None else g
                       for x, g in zip(Xs, Gs)])
        feas = (G <= 1e-6).all(axis=1)
    else:
        G = None
        feas = np.ones_like(F, dtype=bool)

    if feas.any():
        pool = np.where(feas)[0]
        i = int(pool[int(np.argmin(F[pool]))])
        notes = ""
    else:
        i = int(np.argmin(np.maximum(G, 0).sum(axis=1)))
        notes = "no feasible point in history"

    x_best = X[i]
    f_signed = problem.signed_objective(x_best)
    f_signed = f_signed if isinstance(f_signed, float) else float(f_signed[0])
    ok, viol = problem.feasible(x_best)
    return {
        "algorithm": algo_name, "seed": seed, "best_f": float(f_signed),
        "feasible": ok, "max_violation": viol, "evals": _n_eval(res, budget),
        "walltime_s": walltime, "notes": notes,
    }


def run_mo(problem: OpennnProblem, algo_name: str, seed: int, budget: int):
    np.random.seed(seed)
    algo = _mo_algorithms(problem)[algo_name]()
    t0 = time.perf_counter()
    res = minimize(problem, algo,
                   termination=MaximumFunctionCallTermination(budget),
                   seed=seed, verbose=False)
    walltime = time.perf_counter() - t0

    if res.X is None or res.F is None:
        F = np.atleast_2d(res.pop.get("F"))
        X = np.atleast_2d(res.pop.get("X"))
        notes = "no non-dominated front; using final population"
    else:
        F = np.atleast_2d(res.F)
        X = np.atleast_2d(res.X)
        notes = ""

    try:
        hv = float(HV(ref_point=F.max(axis=0) * 1.1)(F))
    except Exception:
        hv = float("nan")

    viols, nfeas = [], 0
    for x in X:
        ok, v = problem.feasible(x)
        viols.append(v)
        nfeas += int(ok)
    summary = {
        "algorithm": algo_name, "seed": seed, "n_pareto": int(F.shape[0]),
        "hv": hv, "feasible_pct": 100.0 * nfeas / len(X),
        "mean_violation": float(np.mean(viols)) if viols else 0.0,
        "evals": _n_eval(res, budget), "walltime_s": walltime, "notes": notes,
    }
    return summary, F, X


def idc_from_result(problem: OpennnProblem, example: str):
    """Best-effort: re-check the bundled C++ IDC result.csv against the same
    constraints. Returns (so_row | mo_row, F, X) or None if result.csv is
    absent / its columns can't be matched (then run the C++ example first)."""
    rcsv = EXAMPLES / example / "result.csv"
    note = "re-checked from result.csv"
    if not rcsv.exists():
        # fall back to the committed smoke-test reference if present
        rcsv = EXAMPLES / example / "expected_output.csv"
        if not rcsv.exists():
            return None
        note = ("re-checked from committed expected_output.csv "
                "(precision-limited; run the C++ example for an exact residual)")
    rows = list(csv.DictReader(open(rcsv, newline="")))
    if not rows:
        return None
    cols = rows[0].keys()
    names = problem.input_names
    # result.csv may name decision columns "x_<name>" or "<name>".
    if all(("x_" + n) in cols for n in names):
        key = lambda n: "x_" + n
    elif all(n in cols for n in names):
        key = lambda n: n
    else:
        print(f"[warn] idc: {rcsv.name} columns don't match input names "
              f"{names}; skipping the idc row.")
        return None
    X = np.array([[float(r[key(n)]) for n in names] for r in rows], dtype=float)

    if problem._is_mo:
        viols, nfeas = [], 0
        for x in X:
            ok, v = problem.feasible(x)
            viols.append(v); nfeas += int(ok)
        row = {"algorithm": "idc", "seed": 0, "n_pareto": int(X.shape[0]),
               "hv": float("nan"), "feasible_pct": 100.0 * nfeas / len(X),
               "mean_violation": float(np.mean(viols)),
               "evals": 0, "walltime_s": 0.0, "notes": note}
        return row, None, None
    # SO: result.csv holds the single returned point (take the best by objective)
    best = min(X, key=lambda x: (problem.signed_objective(x)
               if isinstance(problem.signed_objective(x), float)
               else problem.signed_objective(x)[0]))
    f = problem.signed_objective(best)
    ok, v = problem.feasible(best)
    return ({"algorithm": "idc", "seed": 0,
             "best_f": float(f if isinstance(f, float) else f[0]),
             "feasible": ok, "max_violation": v, "evals": 0, "walltime_s": 0.0,
             "notes": note}, None, None)


def _write(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"[OK] wrote {len(rows)} row(s) -> {path}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--example", required=True,
                    help="example folder under examples/ (e.g. photo_pce10, "
                         "concrete_uci_mo, moeed13)")
    ap.add_argument("--algo", default="all")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--seeds", type=int, default=None,
                    help="run seeds 42..42+N-1 (overrides --seed)")
    ap.add_argument("--budget", type=int, default=40000)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--nn-py", type=Path, default=None, dest="nn_py",
                    help="Override the surrogate .py (e.g. a held-out surrogate "
                         "from benchmarks/holdout/train_surrogate).")
    args = ap.parse_args()

    yaml_path = EXAMPLES / args.example / "problem.yaml"
    if not yaml_path.exists():
        print(f"[ERROR] no problem.yaml at {yaml_path}", file=sys.stderr)
        return 1

    nn = load_nn(args.example, args.nn_py)
    problem = OpennnProblem(yaml_path, nn)
    seeds = (list(range(42, 42 + args.seeds)) if args.seeds else [args.seed])
    out = args.out or (HERE / "results" / f"{args.example}_baselines.csv")

    if problem._is_mo:
        algos = list(_mo_algorithms(problem)) if args.algo == "all" else [args.algo]
        summaries, fronts = [], []
        for algo in algos:
            for seed in seeds:
                print(f"[run] {args.example} {algo} seed={seed} budget={args.budget}")
                s, F, X = run_mo(problem, algo, seed, args.budget)
                print(f"   n_pareto={s['n_pareto']} HV={s['hv']:.4g} "
                      f"feas%={s['feasible_pct']:.1f} mean_viol={s['mean_violation']:.2e}")
                summaries.append(s)
                fronts.append((algo, seed, F, X))
        idc = idc_from_result(problem, args.example)
        if idc is not None:
            summaries.insert(0, idc[0])
        _write(summaries, out)
        front_rows = []
        for algo, seed, F, X in fronts:
            for r in range(F.shape[0]):
                row = {"algorithm": algo, "seed": seed}
                for j in range(F.shape[1]):
                    row[f"F_{j}"] = float(F[r, j])
                for j in range(X.shape[1]):
                    row[f"x_{j}"] = float(X[r, j])
                front_rows.append(row)
        if front_rows:
            _write(front_rows, out.with_name(out.stem + "_fronts.csv"))
    else:
        algos = list(SO_ALGORITHMS) if args.algo == "all" else [args.algo]
        rows = []
        for algo in algos:
            for seed in seeds:
                print(f"[run] {args.example} {algo} seed={seed} budget={args.budget}")
                r = run_so(problem, algo, seed, args.budget)
                print(f"   best_f={r['best_f']:.5g} feasible={r['feasible']} "
                      f"max_violation={r['max_violation']:.2e}")
                rows.append(r)
        idc = idc_from_result(problem, args.example)
        if idc is not None:
            rows.insert(0, idc[0])
        _write(rows, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
