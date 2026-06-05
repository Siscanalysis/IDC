# §7.4 — Real-application case study (SO): photo_pce10 (OPV, simplex constraint)

**Buildable C++ example.** `main.cpp` loads the trained surrogate
(`nn/photo_pce10.json`), applies the constraints in `problem.yaml`, runs
IDC, and writes `result.csv`. Built via the top-level CMake (target
`photo_pce10`).

This is one of the two **real-application** case studies in the paper
(the other is concrete_uci_mo, §7.5). It is the single-objective
simplex-constrained showcase: the donor:acceptor mass fractions sum to
one, so IDC's affine repair operator (§4.4) projects every random sample
back onto the simplex in a single algebraic pass. Reported under the
top-5% held-out validation protocol (see
[`../../docs/holdout_procedure.md`](../../docs/holdout_procedure.md)).

> **Other Olympus tasks.** Only photo_pce10 is shown in the paper. The
> broader Olympus catalog (alkox, benzylation, crossed_barrel,
> fullerenes, hplc, snar, …) is reachable through the `--task` switch of
> [`../../benchmarks/run_olympus.py`](../../benchmarks/run_olympus.py).

## Problem

A quaternary organic-photovoltaic (OPV) blend of two donors
(PCE10, P3HT) and two acceptors (PCBM, oIDTBR). Find the four-component
mass fraction that **minimizes the measured photo-degradation rate**
(normalized post-ageing efficiency drop, lower is better) on the
3-simplex, under the donor-processability band reported by Langner et
al. 2020 — pure-donor and pure-acceptor films do not form a usable bulk
heterojunction. This is the paper's
Equation (eq:pce10_objective):

```
min  y(x)                 over  x in Δ³ = { x ∈ ℝ⁴₊ : Σ xᵢ = 1 }
s.t. 1/6 ≤ x_PCE10 + x_P3HT ≤ 5/6
```

**Input dimension:** 4 (mass fractions `mat_1`=PCE10, `mat_2`=P3HT,
`mat_3`=PCBM, `mat_4`=oIDTBR).
**Output dimension:** 1 (photo-degradation in [0,1], minimized).
**Constraints:** a simplex equality (sum to 1) plus a donor-band
double inequality — see [`constraints.yaml`](constraints.yaml).

## Dataset

Olympus benchmark suite (Häse et al. 2021): `photo_pce10` task, 1040
measured blends from the Langner et al. 2020 high-throughput campaign.

- In-tree copy: [`../../data/photo_pce10/photo_pce10.csv`](../../data/photo_pce10/photo_pce10.csv)
  (1040 rows, columns `mat_1,mat_2,mat_3,mat_4,degradation`).
- Attribution + citations: [`../../data/photo_pce10/SOURCE.md`](../../data/photo_pce10/SOURCE.md).
- License: MIT (Olympus).
- Physical context: §7.4 of the paper covers the OPV device physics and
  why the donor:acceptor morphology drives both efficiency and stability.

## Constraints

Defined in [`constraints.yaml`](constraints.yaml):

| Name | Constraint | Type |
|------|-----------|------|
| `simplex_sum_to_one` | `mat_1 + mat_2 + mat_3 + mat_4 = 1` (xᵢ ≥ 0) | affine equality (required) |
| `donor_band_lower` | `mat_1 + mat_2 ≥ 1/6` | affine inequality (required) |
| `donor_band_upper` | `mat_1 + mat_2 ≤ 5/6` | affine inequality (required) |

The simplex equality is repaired by IDC's affine repair operator
(§4.4) in one closed-form pass; the donor band is enforced on top of it.

## Surrogate

OpenNN Growing Neurons selection over the Olympus `photo_pce10` rows
(`4 → hidden → 1`; test-set R² ≈ 0.90, full-data fit R² = 0.93,
RMSE ≈ 0.028). Trained model JSON at `nn/photo_pce10.json`.
Budget: 40,000 surrogate evaluations per seed, 21 independent seeds per
algorithm (paper §7.1).

## Expected output

`result.csv`:

```
[POST-CHAIN: paste the headline once the post-refactor sweep lands.]
```

To reproduce:

```bash
cd build
cmake --build . --target photo_pce10
./bin/photo_pce10
```

Headline number reported in the §7.4 results table of the paper
(Photo-PCE10 held-out cross-validation).
