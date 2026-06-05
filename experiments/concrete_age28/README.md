# Concrete @ age = 28 — companion-repo experiment

Companion experiment to the IDC paper's §7.5 Concrete MO case study.

## Motivation

The §7.5 setup locks `age = 28` at optimisation time but trains the
surrogate on the full UCI Concrete dataset (1030 rows, age ∈ [1, 365]).
This allows the NN to learn age-dependent strength patterns from
90–365-day rows and apply them at the locked age = 28 input, producing
NN-predicted strengths above the measured 28-day data ceiling. The §7.5
holdout result shows IDC reaching predicted strengths of 97–112 MPa
against a data ceiling of 82.6 MPa (at 91 days; 81.75 MPa at 28 days),
landing in the procedure's *surrogate-hallucination* regime under the
SO `value_gap` diagnostic.

This experiment tests whether restricting the surrogate's training set
to the locked-age slice (425 rows, age = 28 only) removes the
cross-age extrapolation and keeps IDC's predicted strengths inside the
data envelope.

## Files

| File | Purpose |
|---|---|
| `run_age28_chain.py` | Orchestrator: swaps age28 NN into the canonical `concrete_uci_mo/nn/` path, runs IDC + pymoo (full-data + 5 holdout surrogates), restores parent NN at the end. Outputs land in `results/`. |
| `compare_age28_vs_full.py` | Side-by-side aggregator: HV, strength-max range, post-hoc strict-yaml feasibility, against the parent (age-mixed) numbers. |
| `results/` | Auto-populated: `age28_concrete_uci_mo_{idc,pymoo}_*_full.csv` and `_holdout_seed{0..4}.csv` (+ `_fronts.csv`). |

## Data + surrogate

- Filtered dataset (425 rows): `benchmark_datasets/.../concrete_uci_age28/data/concrete_uci_age28.csv`
- Constraints + dataset metadata: `benchmark_datasets/.../concrete_uci_age28/constraints.yaml` + `description.txt`
- Surrogate (baseline + 5 holdout seeds): trained by `baseline_trainer --mode holdout --only concrete_uci_age28`. The 7 free inputs (cement, slag, fly_ash, water, superplasticizer, coarse_agg, fine_agg) are the same as the parent entry; `age` is retained as a constant feature so the surrogate's input shape matches the existing IDC binary without rebuilds.

## Comparison plan

Headline numbers to compare against §7.5 (age-mixed surrogate):

| Metric | Age-mixed (current §7.5) | Age=28 only (this experiment) |
|---|---|---|
| IDC strength_max range | 97.9 – 112.3 MPa | ? |
| IDC HV mean (union-ref) | 1828 | ? |
| pymoo strength_max range | 69.9 – 74.5 MPa | ? |
| pymoo HV | 0 (dominated) | ? |
| Data ceiling at age=28 | 81.75 MPa | 81.75 MPa (identical, fixed input restriction) |

If the age=28 surrogate's IDC strength_max stays below ~82 MPa, the
hallucination regime resolves and the holdout protocol's headline
becomes "honest progress" rather than "surrogate hallucination".
Promotion criterion: under-data-ceiling IDC + clear pymoo dominance.
