# Why the age-28 Concrete surrogate is not held out (the 425-row slice is too small)

§7.5 of the paper locks curing age at 28 days and trains the MO surrogate on
the age-28 slice of the Yeh dataset (425 rows), guarded by the measured 28-day
data ceiling `y*_data = 81.75 MPa` rather than by the top-5% held-out split used
for the single-objective photo-PCE10 case (`docs/holdout_procedure.md`).

This note records the empirical check behind that choice: we **did** try the
top-5% holdout on the 425-row slice, and it collapses into the
surrogate-hallucination regime — confirming the slice is too small to spare a
further 5% removal.

## What we ran

`run_age28_chain.py` trains the age-28 surrogate two ways and runs IDC against
each:

- **full-data** age-28 surrogate (the deployed §7.5 target), and
- **5 holdout seeds** — top-5% by strength removed (~21 rows, including the
  argmax), 80% subsample, Growing-Neurons retrain: the exact protocol of
  `docs/holdout_procedure.md`.

`compare_age28_vs_full.py` aggregates, per surrogate, the IDC maximum predicted
strength and the number of returned points above the 81.75 MPa ceiling.

## Result

- **Full-data** age-28 surrogate: IDC max predicted strength **77.6 MPa**,
  **0** points above the ceiling — cleanly inside the measured envelope.
- **Top-5% holdout**, the five seeds: IDC max predicted strength
  **118.6 / 129.5 / 133.5 / 127.8 / 132.8 MPa**, with **100% of returned points
  above the ceiling** on every seed — full hallucination from the first front
  point onward.

Removing the top 5% by strength from a 425-row slice strips the high-strength
anchor out of an already-small training set. Because the MO objective
*maximises* strength, the surrogate is then left with no information near the
optimum and the optimizer extrapolates straight past the ceiling. This is
precisely the failure mode the holdout protocol exists to **detect**, not to
**manufacture** — so on this slice the holdout damages the surrogate rather than
testing the optimizer, which is why §7.5 uses the full-data age-28 surrogate
plus the measured-ceiling check instead.

> Note: the `pymoo` columns printed by `compare_age28_vs_full.py` are not a
> valid holdout signal — the chain currently writes the same NSGA-II/III front
> file for every tag. Only the IDC fronts are genuine per-seed holdout runs, and
> they alone are cited above.

## Reproduce

```sh
cd experiments/concrete_age28
python run_age28_chain.py        # trains surrogates, runs IDC, writes results/
python compare_age28_vs_full.py  # prints the full-data vs 5-holdout-seed summary above
```

Outputs land in
`results/age28_concrete_uci_mo_idc_fronts_{full,holdout_seed0..4}.csv`.
