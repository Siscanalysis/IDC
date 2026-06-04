# §8.3 — Validation (simulator-grounded MO): MOEED13 economic-emission dispatch

**Buildable C++ example.** `main.cpp` loads the 2-output simulator
surrogate (`nn/moeed13.json`), applies the per-unit bounds and the
power-balance equality in `problem.yaml`, runs multi-objective IDC
(min cost, min emission), and writes the Pareto front to `result.csv`.
Built via the top-level CMake (target `moeed13`).

This is the **validation** counterpart to the analytical
`bbob-biobj-mixint` sweep ([`../../benchmarks/bbob/`](../../benchmarks/bbob/)).
Where photo_pce10 (§8.4) and concrete_uci_mo (§8.5) expose IDC to a
surrogate fitted on *measurement* data, MOEED13 is **simulator-grounded**:
the objective surface is a known closed-form simulator, so the surrogate
fit can be checked directly against ground truth and there is no
measurement noise to confound the optimizer comparison.

## Problem

MOEED13 is the bi-objective extension of the Walters–Sheblé 1993 13-unit
power-system economic dispatch problem. Choose the output $P_i$ (MW) of
each of 13 generation units to supply a fixed demand while minimizing
**both** hourly fuel cost and NOₓ emission.

Objectives (both minimized):

1. **Fuel cost** $C(\mathbf{P})$ — quadratic baseline plus a valve-point
   ripple (absolute-sine term) that makes the cost non-smooth.
2. **NOₓ emission** $E(\mathbf{P})$ — polynomial baseline plus an
   exponential high-load term.

**Input dimension:** 13 (one power setpoint per unit, `P_0 … P_12`).
**Output dimension:** 2 (`total_cost`, `total_emission`).
**Constraints:** a linear-equality power balance plus per-unit box
bounds — see [`constraints.yaml`](constraints.yaml).

## Constraints

Defined in [`constraints.yaml`](constraints.yaml):

- **Power balance** (required): $\bigl|\sum_i P_i - D_{\text{total}}\bigr|
  \le 0.5$ MW with $D_{\text{total}} = 1800$ MW (paper
  Eq. eq:moeed13_problem), encoded as the interval
  $\sum_i P_i \in [1799.5, 1800.5]$. The training table is box-sampled
  and does **not** satisfy this equality; it is enforced at optimization
  time by IDC's affine repair (pymoo uses a penalty).
- **Per-unit box bounds** $[P_{\min,i}, P_{\max,i}]$ from Walters–Sheblé
  1993 Table I (e.g. `P_0 ∈ [0, 680]`, `P_3 ∈ [60, 180]`,
  `P_9 ∈ [40, 120]` MW).

Cost coefficients $(a_i, b_i, c_i, e_i, f_i)$ are from Walters–Sheblé
1993 Table I; emission coefficients
$(\alpha_i, \beta_i, \gamma_i, \xi_i, \lambda_i)$ follow the Abido 2003
type-based parameterization.

## Dataset & surrogate

$10^5$ box-uniform configurations are sampled over
$\prod_i [P_{\min,i}, P_{\max,i}]$, evaluated with the closed-form
cost/emission simulator, and a 2-output OpenNN feed-forward network is
fitted by the Growing Neurons selector. Reported surrogate fit:
$R^2 = 0.9934$ (cost, RMSE ≈ 179 \$/h), $R^2 = 0.9997$ (emission,
RMSE ≈ 14 lb/h). Trained model JSON at `nn/moeed13.json`.
Budget: 40,000 surrogate evaluations per seed, 21 independent seeds per
algorithm (paper §8.1).

A small illustrative sample of the simulator output ships at
[`../../data/moeed13/moeed13_sample.csv`](../../data/moeed13/moeed13_sample.csv)
(200 rows, columns `P_0 … P_12, total_cost, total_emission`); the full
$10^5$-row table is regenerated on demand because it is large and
reproducible. Coefficient provenance and citations are in
[`../../data/moeed13/SOURCE.md`](../../data/moeed13/SOURCE.md).

Because the simulator is closed-form, the example also re-scores the
IDC / pymoo Pareto fronts against ground truth — that comparison
(Figure in §8.3) is produced by the simulator-truth script in
`benchmarks/`.

## Why this is in the validation block, not the real-applications block

Holding out the top-5% of the *sampled* table (the held-out protocol used
for photo_pce10 / concrete_uci_mo) would test how well the NN refits
without those rows, not how well it extrapolates beyond measurement
data — there *are* no measurements here, only simulator samples. So
MOEED13 is reported as an optimizer-vs-optimizer comparison against
simulator truth, not under the memorization-suppression holdout.

## Expected output

`result.csv` contains the Pareto front as
$(P_0, \ldots, P_{12}, \hat{C}, \hat{E})$ rows. Headline HV vs NSGA-II /
NSGA-III is reported in the §8.3 table.

To reproduce:

```bash
cd build
cmake --build . --target moeed13
./bin/moeed13
```
