#!/usr/bin/env python3
"""
Hard-multimodal BBOB stress test (§6.3 limitations), run WITHOUT COCO.

This is the f15--f24 hard-multimodal subset reported in §6.3 of the paper
as the dimensionality stress test: IDC is competitive at n=5 but its
relative performance degrades at n=20, quantifying the geometric coverage
loss of uniform sampling in higher dimensions. It is a *non-surrogate*
stress test --- IDC, CMA-ES, and DE run directly on the analytical
functions, so the cheap-evaluation regime that motivates IDC does NOT
apply here; this is deliberately the adversarial setting.

Implementation note (faithful to the working-tree runner):
    cocoex is unavailable on some Python versions, so this script uses
    canonical mathematical forms of the BBOB f15--f24 functions with
    deterministic per-(function, seed) input shifts, but without COCO
    rotations or full instance normalization. Some canonical functions
    are not zero-centered, so the shift is an origin-symmetry stress
    device rather than a guarantee that every true optimum sits at the
    sampled offset. For a strict COCO-protocol sweep across the five
    suites use the sibling script `run_bbob_suites.py` (needs cocoex).

Switches
--------
    --functions   subset of {15..24} to run        (default: all of 15..24)
    --dimensions  dimensions to run                 (default: 5 20)
    --seeds       independent seeds per cell         (default: 21)
    --algorithms  subset of {IDC,CMA-ES,DE}          (default: all three)
    --budget      function evaluations per run       (default: 50000)

Examples
--------
    python run_bbob_stress.py                        # §6.3 as reported
    python run_bbob_stress.py --functions 15 16 --dimensions 5
    python run_bbob_stress.py --dimensions 5 20 40   # extra dims, not in paper

Output
------
    results/bbob/bbob_stress.csv
"""
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent

# ---------- BBOB function library (canonical forms) -----------------------


def f15_rastrigin(x):
    n = len(x)
    return 10 * n + np.sum(x**2 - 10 * np.cos(2 * np.pi * x))


def f16_weierstrass(x, k_max: int = 20, a: float = 0.5, b: float = 3.0):
    n = len(x)
    ks = np.arange(k_max + 1)
    coef_a = a**ks
    coef_b = b**ks
    s = 0.0
    for xi in x:
        s += np.sum(coef_a * np.cos(2 * np.pi * coef_b * (xi + 0.5)))
    s -= n * np.sum(coef_a * np.cos(2 * np.pi * coef_b * 0.5))
    return s


def f17_schaffer_f7(x):
    n = len(x)
    s = 0.0
    for i in range(n - 1):
        si = np.sqrt(x[i] ** 2 + x[i + 1] ** 2)
        s += np.sqrt(si) + np.sqrt(si) * (np.sin(50.0 * si**0.2) ** 2)
    return (s / (n - 1)) ** 2


def f18_schaffer_f7_illcond(x):
    # Same shape, but with ill-conditioned rescaling: x_i *= 10^(2*(i-1)/(n-1)).
    # This is the SO building block of the §7.2 worked cell (Schaffer F7, cond 1e3).
    n = len(x)
    scales = 10 ** (2 * np.arange(n) / max(n - 1, 1))
    return f17_schaffer_f7(x * scales)


def f19_composite_griewank_rosenbrock(x):
    n = len(x)
    z = np.maximum(np.sqrt(n) / 8.0, 1.0) * x + 1.0
    s = 0.0
    for i in range(n - 1):
        t = 100 * (z[i] ** 2 - z[i + 1]) ** 2 + (z[i] - 1) ** 2
        s += t / 4000.0 - np.cos(t)
    return 10 * s / (n - 1) + 10


def f20_schwefel(x):
    n = len(x)
    return 418.9828872724337 * n - np.sum(x * np.sin(np.sqrt(np.abs(x))))


def _gallagher(x, n_peaks: int):
    # Sum-of-Gaussian-peaks landscape with one global optimum at peak 0.
    n = len(x)
    rng = np.random.default_rng(42 + n_peaks)
    centers = rng.uniform(-4, 4, size=(n_peaks, n))
    centers[0] = 0.0  # global optimum at origin
    weights = np.linspace(1.1, 9.0, n_peaks)
    weights[0] = 10.0  # global peak has highest weight
    val = 0.0
    for k in range(n_peaks):
        d = np.sum((x - centers[k]) ** 2)
        val = max(val, weights[k] * np.exp(-d / (2 * n)))
    return 10 - val  # minimum is at 0 (when val=10)


def f21_gallagher_101(x):
    return _gallagher(x, 101)


def f22_gallagher_21(x):
    return _gallagher(x, 21)


def f23_katsuura(x):
    n = len(x)
    prod = 1.0
    for i in range(n):
        s = 0.0
        for j in range(1, 33):
            t = 2**j * x[i]
            s += np.abs(t - np.round(t)) / 2**j
        prod *= (1 + (i + 1) * s) ** (10.0 / n**1.2)
    return 10.0 / (n * n) * (prod - 1)


def f24_lunacek_birastrigin(x):
    n = len(x)
    mu0, mu1 = 2.5, np.sqrt((2.5**2 - 1) / 1)
    s = 1 - 1 / (2 * np.sqrt(n + 20) - 8.2)
    d = 1.0
    t1 = np.sum((x - mu0) ** 2)
    t2 = d * n + s * np.sum((x - mu1) ** 2)
    t3 = 10 * (n - np.sum(np.cos(2 * np.pi * (x - mu0))))
    return min(t1, t2) + t3


FN_REGISTRY = {
    15: f15_rastrigin,
    16: f16_weierstrass,
    17: f17_schaffer_f7,
    18: f18_schaffer_f7_illcond,
    19: f19_composite_griewank_rosenbrock,
    20: f20_schwefel,
    21: f21_gallagher_101,
    22: f22_gallagher_21,
    23: f23_katsuura,
    24: f24_lunacek_birastrigin,
}

BOUNDS = {
    15: (-5, 5),
    16: (-0.5, 0.5),
    17: (-100, 100),
    18: (-100, 100),
    19: (-5, 5),
    20: (-500, 500),
    21: (-5, 5),
    22: (-5, 5),
    23: (-5, 5),
    24: (-5, 5),
}


# ---------- per-instance translation --------------------------------------


def get_xopt(fid: int, seed: int, dim: int, lo: float, hi: float) -> np.ndarray:
    """Deterministic per-(function, seed) translation offset in the inner box."""
    rng = np.random.default_rng(1000 * fid + 17 * seed + 3)
    margin = 0.2 * (hi - lo)
    return rng.uniform(lo + margin, hi - margin, size=dim)


def translate(f_base, x_opt):
    """Wrap a base function so f_translated(x) = f_base(x - x_opt)."""
    return lambda x: f_base(np.asarray(x) - x_opt)


# ---------- algorithms -----------------------------------------------------


def run_cma_es(f, dim, seed, budget, lo, hi):
    import cma

    es = cma.CMAEvolutionStrategy(
        np.zeros(dim),
        (hi - lo) / 4.0,
        {"maxfevals": budget, "seed": int(seed + 1), "verbose": -9,
         "bounds": [[lo] * dim, [hi] * dim]},
    )
    while not es.stop():
        sols = es.ask()
        vals = [float(f(np.asarray(x))) for x in sols]
        es.tell(sols, vals)
    return float(es.result.fbest)


def run_de(f, dim, seed, budget, lo, hi):
    from scipy.optimize import differential_evolution

    bounds = [(lo, hi)] * dim
    maxiter = max(1, budget // (15 * dim))
    res = differential_evolution(
        f, bounds, seed=seed, maxiter=maxiter, popsize=15, tol=1e-12, polish=False
    )
    return float(res.fun)


def run_idc(f, dim, seed, budget, lo, hi, gamma=0.45, n_iters=10):
    """Reference pure-Python IDC (uniform sample + contract). Matches the
    canonical-form runner in the authors' working tree; the production IDC
    is the OpenNN ResponseOptimization C++ implementation."""
    rng = np.random.default_rng(seed)
    lo_v = np.full(dim, float(lo))
    hi_v = np.full(dim, float(hi))
    n_per_iter = max(1, budget // n_iters)
    best_x = None
    best_f = float("inf")
    for _ in range(n_iters):
        xs = lo_v + rng.random((n_per_iter, dim)) * (hi_v - lo_v)
        vals = np.apply_along_axis(lambda v: float(f(v)), 1, xs)
        idx = int(np.argmin(vals))
        if vals[idx] < best_f:
            best_f = float(vals[idx])
            best_x = xs[idx].copy()
        half = (hi_v - lo_v) / 2 * gamma
        lo_v = np.maximum(np.full(dim, lo), best_x - half)
        hi_v = np.minimum(np.full(dim, hi), best_x + half)
    return best_f


def run_idc_multistart(f, dim, seed, budget, lo, hi, K=5, gamma=0.45, n_iters=10):
    """K full-domain restarts at fixed TOTAL budget (B/K each), best-of-K.

    A minimal *tested* mitigation for the local-minima trap discussed in
    Section 6.3 of the paper: each restart re-samples the full [lo, hi]^dim
    box from a fresh seed, so a contraction that trapped one restart in a
    suboptimal basin does not bind the others. Total surrogate budget is held
    equal to the single-run IDC (B/K evaluations per restart)."""
    per = max(1, budget // K)
    best = float("inf")
    for k in range(K):
        bf = run_idc(f, dim, seed * 1000 + k, per, lo, hi, gamma=gamma, n_iters=n_iters)
        best = min(best, bf)
    return best


RUNNERS = {
    "IDC": run_idc,
    "IDC-MS5": lambda f, dim, seed, budget, lo, hi: run_idc_multistart(
        f, dim, seed, budget, lo, hi, K=5),
    "IDC-MS10": lambda f, dim, seed, budget, lo, hi: run_idc_multistart(
        f, dim, seed, budget, lo, hi, K=10),
    "CMA-ES": run_cma_es,
    "DE": run_de,
}


# ---------- driver ---------------------------------------------------------


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="f15--f24 hard-multimodal BBOB stress test (§6.3), no COCO.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--functions", type=int, nargs="+", default=list(range(15, 25)),
                   choices=list(range(15, 25)),
                   help="BBOB function ids to run (default: 15..24).")
    p.add_argument("--dimensions", type=int, nargs="+", default=[5, 20],
                   help="Dimensions to run (default: 5 20, the values in §6.3).")
    p.add_argument("--seeds", type=int, default=21,
                   help="Independent seeds per cell (default: 21).")
    p.add_argument("--algorithms", nargs="+", default=list(RUNNERS),
                   choices=list(RUNNERS),
                   help="Algorithms to run (default: IDC CMA-ES DE).")
    p.add_argument("--budget", type=int, default=50_000,
                   help="Function evaluations per run (default: 50000).")
    p.add_argument("--out", type=Path, default=HERE / "results" / "bbob" / "bbob_stress.csv",
                   help="Output CSV path.")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    extra_dims = [d for d in args.dimensions if d not in (5, 20)]
    if extra_dims or sorted(args.functions) != list(range(15, 25)):
        print(f"[note] Sec 7.3 reports functions 15..24 at dimensions 5 and 20; "
              f"this run = functions {args.functions} at dimensions {args.dimensions}.")

    with open(args.out, "w", newline="") as fout:
        writer = csv.writer(fout)
        writer.writerow(["function", "dim", "algorithm", "seed", "best_f", "walltime_s"])
        for fid in args.functions:
            for dim in args.dimensions:
                f_base = FN_REGISTRY[fid]
                lo, hi = BOUNDS[fid]
                for algo_name in args.algorithms:
                    runner = RUNNERS[algo_name]
                    for seed in range(args.seeds):
                        x_opt = get_xopt(fid, seed, dim, lo, hi)
                        f = translate(f_base, x_opt)
                        t0 = time.time()
                        try:
                            best_f = runner(f, dim, seed, args.budget, lo, hi)
                        except Exception as e:  # noqa: BLE001
                            print(f"[err]  f{fid} D{dim} {algo_name} seed={seed}: {e}")
                            continue
                        dt = time.time() - t0
                        writer.writerow([fid, dim, algo_name, seed,
                                         f"{best_f:.6g}", f"{dt:.3f}"])
                        fout.flush()
                    print(f"[done] f{fid} D={dim} {algo_name}")
    print(f"\n[OK] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
