# Held-out validation procedure

This document specifies the safeguards that separate **optimizer
behavior** from **surrogate memorization / hallucination risk** in the
real-application case studies. They differ by case:

- The **single-objective** §8.4 (photo_pce10) case uses the top-K%
  held-out cross-validation defined below — its 1040-row dataset is large
  enough to absorb a 5% removal.
- The **multi-objective** §8.5 (concrete_uci_mo) case **cannot** use it:
  its age-28 slice (425 rows) is too small for a further 5% removal
  without losing surrogate fidelity. It instead uses an **age-28
  surrogate restriction** plus a measured-data-ceiling check (see the
  "Multi-objective case" section at the end).

The simulator and analytical validation cases (§8.2 BBOB, §8.3 MOEED13)
are not held out, because their objective surfaces are exact and there is
no measurement data to withhold. The protocol below is defined in §8.1
of the paper.

---

## Why a holdout protocol

A naive evaluation that runs IDC and the baselines against a surrogate
trained on the **entire** dataset rewards memorization: an optimizer that
finds the highest-fitness training point wins, even if that point is an
outlier the surrogate has overfit to.

The protocol below ensures that the surrogate has **never seen** the
candidate optimal configurations during training, so the optimizer is
judged on its ability to find good configurations from generalization,
not memorization.

---

## Protocol — top-5% holdout

For the held-out single-objective case study (§8.4 photo_pce10, and, in
the companion repo, each catalog entry in
`benchmarks/results/branch_a/`):

1. **Rank** all dataset rows by the objective value.
2. **Hold out** the top 5% by objective value, **always including the
   argmax** (the single best row). Call this set $H$.
3. **Train** a surrogate using the remaining 95% of rows, with the same
   Growing Neurons architecture-selection sweep used in the full
   experiments. Repeat training with $S = 5$ independent random seeds to
   produce $S$ surrogates $\{f^{(s)}\}_{s=1}^{S}$.
4. **Sample 80%** of the 95% training pool uniformly at random (per seed)
   to introduce additional variance into the holdout assessment.
5. **Run IDC and each baseline** against each $f^{(s)}$ for 21 seeds.
   The optimizer's recommended point $\xvec_*^{(s)}$ and surrogate output
   $\hat{y}_*^{(s)} = f^{(s)}(\xvec_*^{(s)})$ are recorded.
6. **Cap the surrogate output** at the maximum value observed in the
   training 95%. Outputs above this cap are clamped (with the cap value
   also recorded as a diagnostic). This prevents an optimizer from
   "winning" by pushing the surrogate into an extrapolation regime.

---

## Metrics

For each (problem, optimizer, surrogate seed) combination, **two** metrics
are reported — the `value_gap` / `space_gap` pair defined in §8.1 of the
paper. Let $y^*_{\rm data}$ be the dataset-wide best objective (always in
the held-out set $H$, since the top-$X\%$ contains the argmax),
$\xvec_{\rm argmax}$ its input vector; $y^*_{\rm train}$ and
$\xvec_{\rm train\,best}$ the best objective and input in the truncated
($95\%$) training set; and $\hat y_*^{(s)}, \xvec_*^{(s)}$ the optimizer's
best NN-predicted objective and returned input under surrogate seed $s$.

### Value gap

$$
\mathrm{value\_gap}^{(s)} =
\frac{y^*_{\rm data} - \hat{y}_*^{(s)}}{y^*_{\rm data} - y^*_{\rm train}},
$$

the fraction of the headroom past the training peak that the optimizer
failed to close (smaller is better; $0$ = reached the dataset-wide best,
$<0$ = surrogate predicts past it). For minimized objectives the
numerators are taken in the "better-than" direction, so the sign
convention is identical.

### Space gap

$$
\mathrm{space\_gap}^{(s)} =
\frac{\mathrm{dist}\!\bigl(\xvec_{\rm argmax}, \xvec_*^{(s)}\bigr)}
     {\mathrm{dist}\!\bigl(\xvec_{\rm argmax}, \xvec_{\rm train\,best}\bigr)},
$$

how far (in input space) the returned point landed from the true argmax,
relative to how far the training-best already sits from it. Distances are
Euclidean over per-coordinate min-max-scaled inputs, normalized by
$\sqrt{D_{\rm free}}$; locked optimization coordinates are excluded.
Smaller is better.

### 2×2 diagnostic

The two metrics together give a $2 \times 2$ read:

| Regime | `value_gap` | `space_gap` | Meaning |
|--------|-------------|-------------|---------|
| Ideal | ≈ 0 | ≈ 0 | rediscovered the argmax in value **and** input space |
| Honest progress | ∈ (0, 1) | < 1 | extrapolated past the training peak, sensible region |
| No improvement | ≥ 1 | ≥ 1 | failed to reach past the training peak |
| Surrogate hallucination | < 0 | > 1 | surrogate predicts past the data best, but far from the argmax — the failure mode the protocol **guards against** |

> **Note on the cap.** Step 6 clamps the surrogate output at the truncated-training maximum, so a capped run cannot enter the `value_gap < 0` regime by construction: the cap *prevents* hallucination rather than letting the diagnostic observe it (seeing `value_gap < 0` would mean the cap was disabled). The explicit detector of the same risk is the count of returned points whose prediction exceeds the measured data ceiling, used directly on the un-capped multi-objective Concrete case.

---

## Aggregation

Each metric is aggregated across the $5 \times 21 = 105$
(optimizer seed, surrogate seed) pairs per (problem, optimizer) cell as a
median with the $p25$–$p75$ interquartile range; these populate the
held-out table of the §8.4 single-objective case study. The
multi-objective §8.5 case does not use this holdout (see below); it is
reported with the empirical-reference hypervolume on the age-28
surrogate, since a single-argmax attribution is ambiguous on a Pareto
set.

---

## Interpretation

`value_gap` measures surrogate-side performance ("how close did the
optimizer get to the dataset-wide best, according to the surrogate?");
`space_gap` measures input-space performance ("did the optimizer find the
right *region* in input space, regardless of whether the surrogate scored
it correctly?").

An optimizer that scores well on `value_gap` but poorly on `space_gap` is
exploiting surrogate overfit (the hallucination regime); one that scores
well on both is doing the right thing for the right reasons.

This is the headline reason IDC's reliability on the real-data case
studies (photo_pce10 §8.4, concrete_uci_mo §8.5) is interpreted as a
strength rather than just luck: IDC's recommended points are close in
input space to the actual held-out best, not just in surrogate-output
space.

> **Reproducing the §8.4 diagnostics.** The two-metric `value_gap` /
> `space_gap` pair above is reproduced from a clean clone by the held-out
> pipeline in [`../benchmarks/holdout/`](../benchmarks/holdout/):
> `gen_holdout_splits.py` (top-5% splits) → `train_surrogate` (OpenNN
> Growing Neurons on each split, exporting `.json` + numpy `.py`) → IDC
> (`./bin/photo_pce10 --nn ...`) and the pymoo/pycma baselines
> (`../benchmarks/baselines/run_baselines.py --nn-py ...`) →
> `compute_holdout_gaps.py`. The broader single-objective catalog held-out
> sweep (15 problems) is maintained in the authors' workspace and is not
> bundled here.

---

## Multi-objective case (§8.5 concrete_uci_mo): age-28 restriction

The age-28 slice of the Yeh dataset is only 425 rows — too small to
remove a further 5% without dropping below the size at which the Growing
Neurons selector returns a faithful proxy. So §8.5 uses a different
safeguard against the same memorization/hallucination risk:

1. **Lock the curing age** at 28 days (the standard strength-comparison
   reference) and train the surrogate on the age-28 rows **only**. This
   removes the cross-age extrapolation that would otherwise let the
   network learn long-curing-age strength patterns and apply them at the
   locked age input.
2. **Calibrate against the measured data ceiling**
   $y^*_{\rm data} = 81.75$ MPa (the maximum measured 28-day strength in
   the dataset). Any returned Pareto point whose surrogate-predicted
   strength exceeds this ceiling is, by definition, surrogate
   extrapolation past the measurements; the count of points above the
   ceiling is the hallucination check (it is zero for all algorithms in
   §8.5).

The "too small for a 5% removal" concern is not merely asserted: we
attempted the top-5% holdout on the 425-row slice anyway, and the
surrogate collapses into the hallucination regime — IDC's returned
strengths rise to 118–134 MPa with 100% of points above the 81.75 MPa
ceiling on all five seeds, against 77.6 MPa / 0 above-ceiling for the
full-data age-28 surrogate. See
[`../experiments/concrete_age28/holdout_too_small.md`](../experiments/concrete_age28/holdout_too_small.md)
for the numbers and a one-command reproduction. Note also that the
holdout's value/space-gap attribution is built around a single argmax and
is in general harder to apply to a multi-objective Pareto set.

The §8.5 comparison is then run with 21 optimizer seeds against this
single age-28 surrogate and ranked by empirical-reference hypervolume,
rather than by the value/space-gap pair above.

---

## What the holdout protocol does **not** do

- It does not validate against the **true** physical system; it
  validates against a surrogate that has not seen the candidate optima
  during training. A full physical-system validation would require new
  measurements, which is the deferred follow-up project on an upgraded
  IDC with active learning.

- It does not measure feasibility separately; constraint satisfaction is
  reported in a separate feasibility column of the §8.4 held-out table
  and of the §8.5 Concrete results table (the latter under the strict
  yaml-constraint filter, not a held-out split).
