#!/usr/bin/env python3
"""
gen_holdout_splits.py — generate the top-X% held-out train/test splits for the
§8.4 memorization-suppression protocol (paper §8.1, docs/holdout_procedure.md).

This ships the *way to generate* the holdout datasets rather than the
materialized splits. For a single-objective real-data table it:

  1. holds out the top-X% of rows by the objective (the best slice, including
     the argmax) as the never-trained reference set;
  2. for each of S surrogate-training seeds, draws an 80% subsample of the
     remaining rows as that seed's training set;
  3. writes train_seed<k>.csv + the shared heldout_reference.csv.

Training a surrogate on each generated split (Growing Neurons) is then done
with OpenNN exactly as for the shipped models — see docs/holdout_procedure.md.
The optimizer runs on the trained holdout surrogates are scored by
compute_holdout_metrics.py.

    python gen_holdout_splits.py --data ../data/photo_pce10/photo_pce10.csv \
        --objective degradation --sense min --out results/holdout/photo_pce10

Self-contained: numpy + pandas only.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, required=True, help="input CSV (rows = measured points)")
    ap.add_argument("--objective", required=True, help="objective column name")
    ap.add_argument("--sense", choices=["min", "max"], default="min",
                    help="min: best = smallest objective (e.g. photo-degradation)")
    ap.add_argument("--holdout", type=float, default=0.05, help="top fraction held out (default 0.05)")
    ap.add_argument("--surrogate-seeds", type=int, default=5)
    ap.add_argument("--subsample", type=float, default=0.80, help="train subsample of the remaining rows")
    ap.add_argument("--out", type=Path, required=True, help="output directory")
    args = ap.parse_args(argv)

    df = pd.read_csv(args.data)
    if args.objective not in df.columns:
        raise SystemExit(f"objective '{args.objective}' not in {list(df.columns)}")
    args.out.mkdir(parents=True, exist_ok=True)

    # "Top-X%" = the best slice by the objective sense (includes the argmax).
    ascending = (args.sense == "min")  # min-sense: smallest objective is best -> head after sort asc
    ordered = df.sort_values(args.objective, ascending=ascending)
    n_hold = max(1, int(round(args.holdout * len(df))))
    heldout = ordered.iloc[:n_hold]
    remaining = ordered.iloc[n_hold:]

    heldout.to_csv(args.out / "heldout_reference.csv", index=False)
    print(f"[holdout] {n_hold} rows (top-{args.holdout:.0%} by {args.objective}, "
          f"sense={args.sense}) -> heldout_reference.csv")

    for k in range(args.surrogate_seeds):
        rng = np.random.default_rng(k)  # deterministic per surrogate seed
        m = max(1, int(round(args.subsample * len(remaining))))
        idx = rng.choice(len(remaining), size=m, replace=False)
        train = remaining.iloc[np.sort(idx)]
        train.to_csv(args.out / f"train_seed{k}.csv", index=False)
        print(f"[seed {k}] train rows = {len(train)} ({args.subsample:.0%} of {len(remaining)})")

    print(f"[OK] splits written to {args.out}")
    print("Next: train a Growing-Neurons surrogate on each train_seed<k>.csv with "
          "OpenNN (see docs/holdout_procedure.md), run the optimizers on those "
          "surrogates, then score with compute_holdout_metrics.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
