#!/usr/bin/env python3
"""
compare_outputs.py — smoke-test an example's freshly produced result.csv against
its committed expected_output.csv.

IDC is a STOCHASTIC optimizer, and OpenNN's uniform sampling and randomized
repair sweep draw from std:: distributions whose bit-stream is not portable
across C++ standard libraries. A clean clone built with a different compiler
therefore lands on a DIFFERENT feasible argmin (different input coordinates)
that nonetheless reaches the SAME objective value / Pareto-front extent.
Asserting the raw input vector across compilers is thus not a meaningful
reproducibility test; we compare the reproducible quantities instead:

  * single-objective examples: the best (returned) objective value;
  * multi-objective examples : the per-objective extent (min, max) of the
    front (the front size is reported, not asserted).

Objective columns are the headers NOT prefixed with an input marker
(``x_``, ``P_``, ``mat_``). Tolerance is relative (default 5%) with a small
absolute floor: loose enough to absorb cross-compiler nondeterminism, tight
enough to catch a real regression. Input columns are reported but not asserted.

Usage:
    python scripts/compare_outputs.py examples/photo_pce10/
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

RTOL = 5e-2                      # relative tolerance on objective quantities
ATOL = 1e-6                      # absolute floor (keeps near-zero objectives sane)
INPUT_PREFIXES = ("x_", "P_", "mat_")


def load(path: Path):
    with open(path, newline="") as fh:
        rows = list(csv.reader(fh))
    header = rows[0]
    data = [[float(x) for x in r] for r in rows[1:] if r]
    return header, data


def close(a: float, b: float) -> bool:
    return abs(a - b) <= ATOL + RTOL * abs(b)


def column(header, data, name):
    j = header.index(name)
    return [r[j] for r in data]


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 1:
        print("usage: compare_outputs.py <example-dir>")
        return 2
    d = Path(argv[0])
    produced, expected = d / "result.csv", d / "expected_output.csv"
    if not expected.exists():
        print(f"[skip] no expected_output.csv in {d} (nothing to compare against)")
        return 0
    if not produced.exists():
        print(f"[FAIL] {produced} missing -- run the example first")
        return 1

    h1, got = load(produced)
    h2, exp = load(expected)
    if h1 != h2:
        print(f"[FAIL] header mismatch:\n  produced: {h1}\n  expected: {h2}")
        return 1

    objs = [c for c in h1 if not c.startswith(INPUT_PREFIXES)]
    if not objs:
        objs = [h1[-1]]   # fallback: treat the last column as the objective

    fails = []
    if len(exp) <= 1:
        # single-objective: compare the returned objective value(s)
        for c in objs:
            g, e = column(h1, got, c)[0], column(h2, exp, c)[0]
            ok = close(g, e)
            print(f"  [{'OK' if ok else 'FAIL'}] {c}: produced={g:.6g} expected={e:.6g}")
            if not ok:
                fails.append(c)
    else:
        # multi-objective: compare the per-objective front extent (min, max)
        print(f"  front size: produced={len(got)} expected={len(exp)} "
              f"(reported, not asserted)")
        for c in objs:
            g, e = column(h1, got, c), column(h2, exp, c)
            for stat, fn in (("min", min), ("max", max)):
                gv, ev = fn(g), fn(e)
                ok = close(gv, ev)
                print(f"  [{'OK' if ok else 'FAIL'}] {c} {stat}: "
                      f"produced={gv:.6g} expected={ev:.6g}")
                if not ok:
                    fails.append(f"{c}.{stat}")

    if fails:
        print(f"[FAIL] {d.name}: {len(fails)} objective check(s) outside tol "
              f"(rtol={RTOL}, atol={ATOL}): {', '.join(fails)}")
        return 1
    print(f"[OK] {d.name}: objective checks within tol (rtol={RTOL}, atol={ATOL}); "
          f"input argmin not asserted (cross-compiler RNG).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
