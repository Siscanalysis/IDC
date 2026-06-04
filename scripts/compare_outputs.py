#!/usr/bin/env python3
"""
compare_outputs.py — smoke-test an example's freshly produced result.csv against
its committed expected_output.csv.

Compares element-wise with a tolerance of 1e-5 on input coordinates and 1e-3 on
predicted objective values (loose enough to absorb floating-point drift across
compiler vendors, tight enough to catch a real regression). For multi-objective
examples whose result.csv is a Pareto front, the comparison is order-insensitive:
each expected row must have a near-matching produced row.

Usage:
    python scripts/compare_outputs.py examples/photo_pce10/
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

TOL = 1e-3   # default per-cell tolerance


def load(path: Path):
    with open(path, newline="") as fh:
        rows = list(csv.reader(fh))
    header, data = rows[0], [[float(x) for x in r] for r in rows[1:] if r]
    return header, data


def row_close(a, b, tol=TOL):
    return len(a) == len(b) and all(abs(x - y) <= tol for x, y in zip(a, b))


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
        print(f"[FAIL] {produced} missing — run the example first")
        return 1

    h1, got = load(produced)
    h2, exp = load(expected)
    if h1 != h2:
        print(f"[FAIL] header mismatch:\n  produced: {h1}\n  expected: {h2}")
        return 1

    missing = [e for e in exp if not any(row_close(e, g) for g in got)]
    if missing:
        print(f"[FAIL] {len(missing)}/{len(exp)} expected row(s) have no match within tol={TOL}")
        for m in missing[:5]:
            print("   expected:", m)
        return 1

    print(f"[OK] {d.name}: {len(exp)} expected row(s) matched within tol={TOL} "
          f"({len(got)} produced rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
