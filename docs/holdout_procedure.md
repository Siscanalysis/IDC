# Held-out validation procedure

This document specifies the top-K% held-out cross-validation protocol
used in the §8.4 (photo_pce10) and §8.5 (concrete_uci_mo)
real-application case studies to separate **optimizer behavior** from
**surrogate memorization risk**. The protocol is defined once in §8.1
(setup) and applied to both real-data cases; the simulator and analytical
validation cases (§8.2 BBOB, §8.3 MOEED13) are not held out, because
their objective surfaces are exact and there is no measurement data to
withhold.

This file mirrors §2 of the
`experiments/docs/BENCHMARKING_PROCEDURE.md` document in the authors'
internal workspace.

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

For each held-out problem (the two real-application case studies §8.4 /
§8.5, and, in the companion repo, each catalog entry in
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
| Surrogate hallucination | < 0 | > 1 | surrogate predicts past the data best, but far from the argmax — the failure mode the protocol is designed to expose |

---

## Aggregation

Each metric is aggregated across the $5 \times 21 = 105$
(optimizer seed, surrogate seed) pairs per (problem, optimizer) cell as a
median with the $p25$–$p75$ interquartile range; these populate the
held-out tables of the §8.4 / §8.5 real-application case studies. For the
multi-objective case (§8.5) a single-argmax attribution is ambiguous on a
Pareto set, so the per-objective generalization is replaced by the
empirical-reference hypervolume.

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

> **Note on the broader catalog.** The committed single-objective
> cross-table in [`../benchmarks/extra_results/`](../benchmarks/extra_results/)
> was produced with an earlier **four-metric** variant of this protocol
> (`absolute_gap`, `relative_gap`, `absolute_geo`, `relative_geo` —
> absolute/relative value gaps plus input-space distance to the nearest
> held-out point). It captures the same value-vs-space distinction; the
> paper's two-metric `value_gap` / `space_gap` pair is the consolidated
> form used for the headline §8.4 / §8.5 case studies.

---

## What the holdout protocol does **not** do

- It does not validate against the **true** physical system; it
  validates against a surrogate that has not seen the candidate optima
  during training. A full physical-system validation would require new
  measurements, which is the deferred follow-up project on an upgraded
  IDC with active learning.

- It does not measure feasibility separately; constraint satisfaction is
  reported in a separate column of the §8.4 / §8.5 held-out tables.
