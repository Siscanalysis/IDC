# §8.5 — Real-application case study (MO): UCI Concrete (max strength, min cement)

**Buildable C++ example.** `main.cpp` loads the trained strength
surrogate (`nn/concrete_uci.json`), applies the six affine constraints in
`problem.yaml`, runs multi-objective IDC (max strength, min cement), and
writes the Pareto front to `result.csv`. Built via the top-level CMake
(target `concrete_uci_mo`).

This is one of the two **real-application** case studies in the paper
(the other is photo_pce10, §8.4). Unlike the SO case, it is **not**
reported under the top-5% held-out protocol: the age-28 slice (425 rows)
is too small for a further 5% removal, so §8.5 instead uses an
**age-28 surrogate restriction** (the surrogate is trained only on the
age-28 mixes) and calibrates against the measured data ceiling
(see [`../../docs/holdout_procedure.md`](../../docs/holdout_procedure.md)).

## Problem

The UCI Concrete dataset (single-objective view kept as a catalog
example in [`../additional/concrete_uci_so/`](../additional/concrete_uci_so/)),
reformulated as a **multi-objective** problem to illustrate IDC's
Pareto-front behavior on a real dataset with linear constraints.

Objectives:

1. **Maximize** 28-day compressive strength (MPa).
2. **Minimize** cement content (kg/m³ of mix), which is a direct proxy
   for embodied CO₂ in the mix.

These two objectives are conflicting: cement is the principal strength
contributor in conventional concrete, but it is also the dominant
source of CO₂ emissions. Recovering a Pareto-front trade-off is
practically relevant to sustainable construction.

**Input dimension:** 8 (`cement, slag, fly_ash, water, sp, coarse_agg,
fine_agg, age`; `age` fixed at 28 days).
**Output dimension:** 1 from the surrogate (strength) + 1 derived
from the input vector (cement amount). The cement objective does not
require an additional model output; it reads directly from
$x_{\text{cement}}$.

**Constraints:** six input-side affine constraints — see
[`constraints.yaml`](constraints.yaml).

## Constraints

The six standard concrete-engineering constraints (EN 206 / ASTM C595),
defined in [`constraints.yaml`](constraints.yaml). `binder` =
cement + slag + fly_ash. Ordered most-reliable → least-reliable, where
"data pass" is the fraction of the 1030 Yeh-1998 rows that individually
satisfy the constraint (audited 2026-06-02):

| Name | Constraint | Source / rationale | Data pass |
|------|-----------|--------------------|-----------|
| `mass_balance` | Σ ingredients ∈ [2200, 2600] | density ~ 2400 kg/m³ (physical identity) | 99.7% |
| `binder_floor` | cement + slag + fly_ash ≥ 200 | BS EN 206 / BS 8500 | 100% |
| `slag_replacement` | slag ≤ 0.70 · binder | ASTM C595 Type IS | 100% |
| `water_cement_lower` | water ≥ 0.30 · cement | hydration minimum | 98.6% |
| `fly_ash_replacement` | fly_ash ≤ 0.40 · binder | ASTM C595 Type IP | 92.1% |
| `water_cement_upper` | water ≤ 0.70 · cement | structural-grade design limit | 51.7% |

All six are affine, so IDC's affine repair operator (§4.4) keeps every
sampled mix feasible. The **binding** constraint is the water/cement
upper bound: it intentionally restricts the feasible region to
structural-grade (w/c ≤ 0.70) mixes and excludes ~half the (mostly
low-strength, high-w/c) measured rows — appropriate for a
strength-maximization objective, but note it is a *design* limit, not a
property of the full dataset. The three composition limits
(binder/slag/fly-ash) exclude no rows beyond those already removed by the
water/cement and mass-balance limits. The full 6-constraint feasible set
retains 518 of 1030 rows.

## Dataset & surrogate

UCI Machine Learning Repository: *Concrete Compressive Strength*
(Yeh 1998).

- In-tree copy: [`../../data/concrete_uci/concrete_uci.csv`](../../data/concrete_uci/concrete_uci.csv)
  (1030 rows).
- Attribution + citation: [`../../data/concrete_uci/SOURCE.md`](../../data/concrete_uci/SOURCE.md).

The MO reformulation is purely in the optimization conditions: the
cement input variable additionally carries a `min` objective condition.
The shipped surrogate `nn/concrete_uci.json` is the
**age-28-restricted** strength model used in §8.5 — trained on the 425
age-28 mixes only (test R² ≈ 0.79, training R² ≈ 0.76, RMSE ≈ 7.2 MPa),
so it shares the curing age of the optimization target and cannot
extrapolate strength patterns from older mixes. (For reference, an
all-ages surrogate over the full 1030 rows fits higher, R² ≈ 0.97, but
at the cost of cross-age extrapolation; §8.5 deliberately uses the
age-28 model instead. That all-ages model is not shipped here.)
Budget: 40,000 surrogate evaluations per seed, 21 independent seeds per
algorithm; the IDC side additionally caps the empirical Pareto front at
10,000 points (paper §8.1).

## Expected output

`result.csv` contains the Pareto front as $(x, \hat{y})$ rows.

To reproduce:

```bash
cd build
cmake --build . --target concrete_uci_mo
./bin/concrete_uci_mo
```

The Pareto front plot is reported in the §8.5 Pareto-front figure of the
paper; the internal-gap and boundary-gap stability metrics in the §8.5
results table.

**Reproducibility scope.** This example runs the **IDC** side only (the
default §8.1 config: $N=2000$, $I_{\max}=20$, seed $0$, Pareto cap
$10\,000$, hardcoded in `main.cpp`). On the pinned OpenNN tag it returns
the §8.5 IDC front to within run-to-run / build variation
($\approx 5{,}500$ points, strength maximum $\approx 77.6$ MPa); the
committed `expected_output.csv` is the smoke-test reference for that run.
The full IDC-vs-NSGA-II/III comparison, the per-algorithm
constraint-violation figures, and the §8.5 normalized-hypervolume and
3-front overlay plots are produced from the authors' workspace (the
pymoo baselines are not bundled here, as noted in the top-level README).
To make the paper and this example byte-identical, regenerate
`expected_output.csv` with `./bin/concrete_uci_mo` on the pinned tag and
report that run's exact $|\mathcal{P}|$ and strength maximum in §8.5.

## Why this is interesting

This example illustrates the **dynamic utopian-point update**
(§6.2 of the paper): because the cement minimization objective starts
its utopian at $\min_{i} x_{i,\text{cement}}$ from the training data,
but IDC pushes the front toward lower cement values within the
constraint manifold, the utopian is repeatedly promoted across
iterations. The log shows the corresponding
`"Utopian promoted to better Pareto coordinate."` lines.
