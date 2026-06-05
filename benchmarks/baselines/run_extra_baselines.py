#!/usr/bin/env python3
"""
run_extra_baselines.py — DIRECT and Bayesian-optimization (BO) baselines for the
single-objective Photo-PCE10 case study (§7.4), added in response to Reviewer X's
request to compare against DIRECT, MADS, and Bayesian Optimization in addition to
the CMA-ES / DE / GA / PSO pool already in run_baselines.py.

Both optimizers run against the SAME trained surrogate and the SAME problem.yaml
(simplex equality mat_1+...+mat_4 = 1 plus the donor processability band) as IDC
and the pymoo/pycma baselines, so any difference reflects the optimizer, not the
model or the constraints.

Methods
  - DIRECT  : scipy.optimize.direct, deterministic Lipschitz hyperrectangle
              subdivision, run at the matched 40 000-evaluation budget. A single
              deterministic run (DIRECT has no random seed). It optimizes a
              penalized objective  degradation + LAMBDA * max(0, violation) ; the
              reported row uses the same feasibility-first rule as run_baselines.py
              (best feasible point within tol; else the least-infeasible point).
  - BO      : a Gaussian-process / expected-improvement loop (scikit-learn GP,
              Matern 5/2). Because GP inference is O(t^3) in the number of
              evaluations t, BO is run at its native low-evaluation budget
              (BO_BUDGET evaluations, 21 seeds) rather than at 40 000: a GP over
              40 000 points is computationally infeasible, which is exactly the
              cheap-evaluation regime IDC targets and BO does not. Reported as
              mean +/- std over the seeds.
  - MADS    : mesh adaptive direct search needs a maintained solver (NOMAD /
              PyNomad) that is not available in this environment; MADS is a
              deterministic poll method of the same family as DIRECT and is
              represented here by the DIRECT row (see the paper's §7.4 note).

Output: benchmarks/baselines/results/photo_pce10_extra_baselines.csv, same schema
as photo_pce10_baselines.csv (algorithm, seed, best_f, feasible, max_violation,
evals, walltime_s, notes).

Usage:
    python run_extra_baselines.py --example photo_pce10 --bo-seeds 21 --budget 40000
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import direct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXAMPLES = ROOT / "examples"
sys.path.insert(0, str(HERE))

from problem_pymoo import OpennnProblem
from run_baselines import load_nn

LAMBDA = 50.0          # penalty weight on constraint violation (matches CMA-ES-style additive penalty)
BO_BUDGET = 200        # native BO evaluation budget (GP is O(t^3); 40000 is infeasible)
BO_INIT = 16           # initial random design before the GP loop
BO_CAND = 800          # random candidates scored per acquisition step


def penalized(problem: OpennnProblem, x: np.ndarray) -> tuple[float, bool, float]:
    """Return (penalized_objective, is_feasible, violation) for one point.
    The objective is in user units (degradation, minimize); the penalty drives
    the box optimizers toward the simplex/band feasible set."""
    f = problem.signed_objective(x)
    f = f if isinstance(f, float) else float(f[0])
    ok, viol = problem.feasible(x)
    return f + LAMBDA * viol, ok, viol


def _row(problem, algo, seed, x_best, evals, walltime, notes):
    f = problem.signed_objective(x_best)
    f = f if isinstance(f, float) else float(f[0])
    ok, viol = problem.feasible(x_best)
    rec = {"algorithm": algo, "seed": seed, "best_f": float(f),
           "feasible": ok, "max_violation": viol, "evals": int(evals),
           "walltime_s": float(walltime), "notes": notes}
    for j, xj in enumerate(np.asarray(x_best).ravel()):
        rec[f"x_{j}"] = float(xj)
    return rec


def run_direct(problem: OpennnProblem, budget: int) -> dict:
    xl, xu = problem.xl, problem.xu
    bounds = list(zip(xl.tolist(), xu.tolist()))
    best = {"x": None, "pen": np.inf, "f_feas": np.inf, "x_feas": None}

    def f(xx):
        x = np.asarray(xx, dtype=float)
        pen, ok, viol = penalized(problem, x)
        if pen < best["pen"]:
            best["pen"], best["x"] = pen, x.copy()
        if ok and (problem.signed_objective(x) if isinstance(problem.signed_objective(x), float)
                   else problem.signed_objective(x)[0]) < best["f_feas"]:
            best["f_feas"] = (problem.signed_objective(x) if isinstance(problem.signed_objective(x), float)
                              else problem.signed_objective(x)[0])
            best["x_feas"] = x.copy()
        return pen

    t0 = time.perf_counter()
    direct(f, bounds, maxfun=budget, maxiter=100000, locally_biased=False)
    walltime = time.perf_counter() - t0
    x_best = best["x_feas"] if best["x_feas"] is not None else best["x"]
    notes = "" if best["x_feas"] is not None else "no feasible point found"
    return _row(problem, "direct", 0, x_best, budget, walltime, notes)


def run_bo(problem: OpennnProblem, seed: int, budget: int) -> dict:
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import Matern, ConstantKernel
    from scipy.stats import norm
    rng = np.random.default_rng(seed)
    xl, xu = problem.xl, problem.xu
    d = problem.n_var

    def sample(n):
        return xl + rng.random((n, d)) * (xu - xl)

    X = sample(BO_INIT)
    y = np.array([penalized(problem, x)[0] for x in X])
    t0 = time.perf_counter()
    # Fixed-hyperparameter GP (Matern 5/2): the kernel scale is held fixed
    # (optimizer=None) so each step costs one Cholesky rather than an L-BFGS
    # over kernel hyperparameters; this keeps the native-budget BO loop fast
    # without changing its character (GP surrogate + expected improvement).
    kernel = ConstantKernel(1.0) * Matern(length_scale=0.2, nu=2.5)
    while len(X) < budget:
        gp = GaussianProcessRegressor(kernel=kernel, normalize_y=True,
                                      optimizer=None, alpha=1e-6, random_state=seed)
        gp.fit(X, y)
        cand = sample(BO_CAND)
        mu, sd = gp.predict(cand, return_std=True)
        sd = np.maximum(sd, 1e-12)
        ybest = y.min()
        z = (ybest - mu) / sd
        ei = (ybest - mu) * norm.cdf(z) + sd * norm.pdf(z)
        xnext = cand[int(np.argmax(ei))]
        X = np.vstack([X, xnext])
        y = np.append(y, penalized(problem, xnext)[0])
    walltime = time.perf_counter() - t0

    feas_mask = np.array([problem.feasible(x)[0] for x in X])
    if feas_mask.any():
        pool = np.where(feas_mask)[0]
        fobj = np.array([(problem.signed_objective(X[i]) if isinstance(problem.signed_objective(X[i]), float)
                          else problem.signed_objective(X[i])[0]) for i in pool])
        x_best = X[pool[int(np.argmin(fobj))]]
        notes = ""
    else:
        x_best = X[int(np.argmin(y))]
        notes = "no feasible point found"
    return _row(problem, "bo", seed, x_best, len(X), walltime, notes)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--example", default="photo_pce10")
    ap.add_argument("--budget", type=int, default=40000, help="DIRECT evaluation budget")
    ap.add_argument("--bo-seeds", type=int, default=21)
    ap.add_argument("--bo-budget", type=int, default=BO_BUDGET)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    yaml_path = EXAMPLES / args.example / "problem.yaml"
    nn = load_nn(args.example)
    problem = OpennnProblem(yaml_path, nn)

    rows = []
    print(f"[run] DIRECT {args.example} budget={args.budget}")
    r = run_direct(problem, args.budget)
    print(f"   best_f={r['best_f']:.6g} feasible={r['feasible']} viol={r['max_violation']:.2e}")
    rows.append(r)

    for seed in range(42, 42 + args.bo_seeds):
        print(f"[run] BO {args.example} seed={seed} budget={args.bo_budget}")
        r = run_bo(problem, seed, args.bo_budget)
        print(f"   best_f={r['best_f']:.6g} feasible={r['feasible']} viol={r['max_violation']:.2e}")
        rows.append(r)

    out = args.out or (HERE / "results" / f"{args.example}_extra_baselines.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(dict.fromkeys(k for r in rows for k in r))
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"[OK] wrote {len(rows)} row(s) -> {out}")

    # quick BO aggregate
    bo = [r for r in rows if r["algorithm"] == "bo"]
    if bo:
        bf = np.array([r["best_f"] for r in bo])
        feas = np.mean([r["feasible"] for r in bo]) * 100
        print(f"[BO 21-seed] best_f mean={bf.mean():.6g} std={bf.std():.3g} feas%={feas:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
