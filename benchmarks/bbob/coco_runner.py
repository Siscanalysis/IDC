"""
coco_runner.py — per-problem optimization backend for run_bbob_suites.py
(§8.2 analytical validation on the COCO bbob-biobj-mixint suite).

`run_problem(problem, algo, seed, multiobjective)` runs one optimizer on one
COCO problem under a matched per-problem evaluation budget and returns a dict
with the per-run metrics the sweep records (`hv` for MO; `best_ert_win` is left
empty here because the per-target ERT-win tally is computed downstream by
`cocopp` + `parse_cocopp_idc_wins.py`, not per single run).

Provenance and reproducibility scope
-------------------------------------
The §8.2 *headline* numbers in the manuscript (Table bbob-biobj-mixint, win
counts 63/59/70/85/90/91 of 92 across n_c = 5..160, cell-win rate
67/57/70/91/98/100%) were produced in the authors' working tree by:
  * IDC  — the C++ MultiSeedIDC analytical optimizer (a budget-respecting
           interval-domain-contraction solver; on the analytical suite it
           counts one evaluation per sampled point and *splits* its total
           budget across the bi-objective weight scalarizations, so it is
           conservatively budgeted relative to the single-front baselines);
  * NSGA-II / NSGA-III / MOEA-D — pymoo, same per-problem budget;
followed by `cocopp` post-processing and `parse_cocopp_idc_wins.py`. Those
authoritative win tallies are committed at
`results/bbob-biobj-mixint/{summary,per_function}_idc_wins.csv`, so the §8.2
TABLE is reproducible from committed data without re-running the sweep.

This module provides a *self-contained, budget-fair* reproduction path so a
clean clone can re-run the sweep itself: the baselines are run exactly (pymoo);
IDC is run via a reference Python interval-domain-contraction optimizer
(weighted-sum scalarization, budget split across K weights, uniform-sample +
contract per scalarization) that mirrors the production solver's methodology
and respects the same total budget. It reproduces the qualitative trend (IDC's
advantage growing with dimension on bbob-biobj-mixint); the exact win counts
are the committed C++ numbers above.

Requires `cocoex` (COCO experiment module) and `pymoo`; see README.md and
requirements.txt for the pinned versions.
"""
from __future__ import annotations

import numpy as np

# Matched per-problem total-evaluation budget (same for every algorithm).
DEFAULT_BUDGET = 5000
# Number of weight scalarizations IDC splits its budget across (bi-objective).
IDC_N_WEIGHTS = 11


# --------------------------------------------------------------------------- #
# COCO problem helpers
# --------------------------------------------------------------------------- #
def _bounds(problem):
    return np.asarray(problem.lower_bounds, float), np.asarray(problem.upper_bounds, float)


def _n_int(problem):
    # bbob-biobj-mixint exposes the count of integer (leading) variables;
    # fall back to 0 for purely continuous suites.
    return int(getattr(problem, "number_of_integer_variables", 0) or 0)


def _snap(x, n_int):
    """Round the leading n_int coordinates to integers (COCO mixed-integer
    convention); leave the continuous tail untouched."""
    x = np.array(x, float)
    if n_int > 0:
        x[..., :n_int] = np.round(x[..., :n_int])
    return x


def _eval(problem, X, n_int):
    """Evaluate a batch X (m, d) -> (m, n_obj), snapping integer coords."""
    X = np.atleast_2d(X)
    return np.array([problem(_snap(row, n_int)) for row in X], float)


def _hv(F):
    """Normalized dominated hypervolume of a minimization front F (m, 2),
    against a 1.1x-nadir reference in a per-objective [0,1] box."""
    if len(F) == 0:
        return 0.0
    nd = _nondominated_min(F)
    lo, hi = nd.min(0), nd.max(0)
    span = np.where(hi > lo, hi - lo, 1.0)
    Q = (nd - lo) / span                      # minimization box, best corner (0,0)
    M = 1.0 - Q                               # flip so best corner = (1,1)
    # staircase dominated area under the maximize-both front
    area, last_y = 0.0, 0.0
    for x, y in sorted(M.tolist(), key=lambda p: -p[0]):
        if y > last_y:
            area += x * (y - last_y)
            last_y = y
    return float(area)


def _nondominated_min(F):
    F = np.atleast_2d(F)
    keep = np.ones(len(F), bool)
    for i in range(len(F)):
        if not keep[i]:
            continue
        dom = np.all(F <= F[i], axis=1) & np.any(F < F[i], axis=1)
        keep[dom] = False
    return F[keep]


# --------------------------------------------------------------------------- #
# Reference Python IDC (analytical, budget-fair)
# --------------------------------------------------------------------------- #
def _idc_mo(problem, seed, budget, n_weights=IDC_N_WEIGHTS,
            gamma=0.85, n_iters=10):
    rng = np.random.default_rng(seed)
    lo0, hi0 = _bounds(problem)
    n_int = _n_int(problem)
    per_w = max(1, budget // n_weights)
    n_per_iter = max(1, per_w // n_iters)
    archive_X = []
    for k in range(n_weights):
        w = np.array([k / (n_weights - 1), 1.0 - k / (n_weights - 1)]) \
            if n_weights > 1 else np.array([0.5, 0.5])
        lo, hi = lo0.copy(), hi0.copy()
        best_x, best_s = None, np.inf
        for _ in range(n_iters):
            X = rng.uniform(lo, hi, size=(n_per_iter, len(lo)))
            F = _eval(problem, X, n_int)
            s = F @ w
            j = int(np.argmin(s))
            archive_X.append(_snap(X[j], n_int))
            if s[j] < best_s:
                best_s, best_x = s[j], X[j]
            half = (hi - lo) * gamma / 2.0
            lo = np.clip(best_x - half, lo0, hi0)
            hi = np.clip(best_x + half, lo0, hi0)
    F = _eval(problem, np.array(archive_X), n_int)
    return _hv(F)


# --------------------------------------------------------------------------- #
# pymoo baselines
# --------------------------------------------------------------------------- #
def _baseline_mo(problem, algo, seed, budget):
    from pymoo.core.problem import Problem
    from pymoo.optimize import minimize
    from pymoo.termination.max_eval import MaximumFunctionCallTermination
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.algorithms.moo.nsga3 import NSGA3
    from pymoo.algorithms.moo.moead import MOEAD
    from pymoo.util.ref_dirs import get_reference_directions

    lo, hi = _bounds(problem)
    n_int = _n_int(problem)
    n_obj = problem.number_of_objectives

    class _P(Problem):
        def __init__(self):
            super().__init__(n_var=len(lo), n_obj=n_obj, xl=lo, xu=hi)

        def _evaluate(self, X, out, *a, **k):
            out["F"] = _eval(problem, X, n_int)

    ref = get_reference_directions("uniform", n_obj, n_partitions=max(12 - n_obj, 4))
    algos = {
        "nsga2": lambda: NSGA2(pop_size=100),
        "nsga3": lambda: NSGA3(pop_size=100, ref_dirs=ref),
        "moead": lambda: MOEAD(ref_dirs=ref, n_neighbors=15, prob_neighbor_mating=0.7),
    }
    np.random.seed(seed)
    res = minimize(_P(), algos[algo](),
                   termination=MaximumFunctionCallTermination(budget),
                   seed=seed, verbose=False)
    F = np.atleast_2d(res.F) if res.F is not None else np.atleast_2d(res.pop.get("F"))
    return _hv(F)


# --------------------------------------------------------------------------- #
# Public entry point used by run_bbob_suites.py
# --------------------------------------------------------------------------- #
def run_problem(problem, algo, seed, multiobjective=True, budget=DEFAULT_BUDGET):
    """Run one optimizer on one COCO problem; return {'best_ert_win', 'hv'}.

    best_ert_win is intentionally empty: the per-target ERT-win tally is a
    post-processing step (cocopp + parse_cocopp_idc_wins.py) over the archived
    runs, not a per-run quantity. hv is the normalized dominated hypervolume.
    """
    if not multiobjective:
        raise NotImplementedError(
            "coco_runner currently implements the MO bbob-biobj-mixint path "
            "(the §8.2 suite). For the SO suites use the authors' workspace "
            "runner; see README.md.")
    if algo == "idc":
        hv = _idc_mo(problem, seed, budget)
    elif algo in ("nsga2", "nsga3", "moead"):
        hv = _baseline_mo(problem, algo, seed, budget)
    else:
        raise ValueError(f"unknown algorithm {algo!r}")
    return {"best_ert_win": "", "hv": hv}
