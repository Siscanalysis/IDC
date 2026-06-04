#!/usr/bin/env python3
"""
compute_holdout_gaps.py — value_gap / space_gap for the §8.4 held-out protocol
(docs/holdout_procedure.md), computed from a trained held-out surrogate run.

Given the full dataset (for the global argmax y*_data / x_argmax), a held-out
training split (for y*_train / x_train_best), and an optimizer's recommended
point (x*, ŷ*), reports:

  value_gap = (y*_data - ŷ*) / (y*_data - y*_train)
  space_gap = dist(x_argmax, x*) / dist(x_argmax, x_train_best)

with input distances Euclidean over per-coordinate min-max-scaled inputs,
normalized by sqrt(D_free). Sign convention per docs/holdout_procedure.md.

Usage:
  python compute_holdout_gaps.py \
     --full ../data/photo_pce10/photo_pce10.csv \
     --train results/holdout/photo_pce10/train_seed0.csv \
     --point results/holdout/photo_pce10/idc_seed0_result.csv \
     --inputs mat_1 mat_2 mat_3 mat_4 --target degradation --sense min

Self-contained: standard library only.
"""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


def rows(p: Path) -> list[dict]:
    return list(csv.DictReader(open(p, newline="")))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--full", type=Path, required=True, help="full dataset CSV")
    ap.add_argument("--train", type=Path, required=True, help="held-out training split CSV")
    ap.add_argument("--point", type=Path, required=True,
                    help="optimizer result CSV (one row: inputs + target prediction)")
    ap.add_argument("--inputs", nargs="+", required=True, help="input column names")
    ap.add_argument("--target", required=True, help="objective column name")
    ap.add_argument("--sense", choices=["min", "max"], default="min")
    args = ap.parse_args(argv)

    full, train, pt = rows(args.full), rows(args.train), rows(args.point)
    better = min if args.sense == "min" else max
    INP, T = args.inputs, args.target

    mn = {k: min(float(r[k]) for r in full) for k in INP}
    mx = {k: max(float(r[k]) for r in full) for k in INP}

    def scale(r):
        return [(float(r[k]) - mn[k]) / ((mx[k] - mn[k]) or 1.0) for k in INP]

    def dist(a, b):
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    argmax = better(full, key=lambda r: float(r[T]))
    y_data = float(argmax[T])
    tb = better(train, key=lambda r: float(r[T]))
    y_train = float(tb[T])
    p = pt[0]
    yhat = float(p[T])

    denom = (y_data - y_train) or float("nan")
    value_gap = (y_data - yhat) / denom
    D = len(INP)
    sden = dist(scale(argmax), scale(tb)) or float("nan")
    space_gap = dist(scale(argmax), scale(p)) / sden / math.sqrt(D)

    print(f"y_data={y_data:.6g}  y_train={y_train:.6g}  yhat={yhat:.6g}")
    print(f"value_gap={value_gap:.4f}  space_gap={space_gap:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
