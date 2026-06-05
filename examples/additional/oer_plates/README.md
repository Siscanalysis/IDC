# Catalog example — OER plate (catalyst composition, 6-simplex)

**Not a manuscript example.** This OER-catalyst screen was a headline
example in an earlier draft; the final manuscript carries the simplex /
affine-repair story through the §7.4 photo_pce10 case study and the §7.2
BBOB bi-objective mixed-integer validation instead. It is kept here as an
extra affine-repair showcase on a strict 6-simplex equality constraint,
part of the broader chemistry-HTE catalog.

## Problem

High-throughput electrocatalysis screening of multi-metal catalyst
plates for the oxygen-evolution reaction (OER). Each plate position has a
metal-loading composition vector $\xvec = (x_1, \ldots, x_6) \in \Delta^5$
(6-simplex: $x_i \geq 0$, $\sum_i x_i = 1$) over six metals
(Ni, Fe, Co, Mn, Ce, La), and the measured response is the catalyst's
**overpotential**.

Objective:

- **Minimize** the OER overpotential (a lower overpotential is a more
  active catalyst). This is a single-objective real-data task; there is
  one measured target, not an activity/stability trade-off.

**Input dimension:** 6 (loading fractions over six metal elements:
`ni`, `fe`, `co`, `mn`, `ce`, `la`).
**Output dimension:** 1 (overpotential, minimized).
**Constraint type:** linear equality (simplex sum-to-one); per-element
non-negativity.

The 6-simplex equality constraint is exactly the geometry where IDC's
algebraically exact affine repair operator (§4.4 of the paper) repairs
random samples back onto the simplex in a single pass without rejection.

Olympus ships several OER plate campaigns (plate IDs 3496, 3851, 3860,
4098), each with ~2120 measured compositions; they are run as independent
single-objective instances.

## Dataset

Olympus benchmark suite (Häse et al. 2021), the `oer_plate_*` tasks — one
redistributed campaign per plate. Source:

- Olympus package: <https://github.com/aspuru-guzik-group/olympus>
- Olympus paper: <https://arxiv.org/abs/2010.04153>

- Local copy: `../../../data/oer_plates/`

## Surrogate

Single-output OpenNN model (overpotential) selected by Growing Neurons
over the plate's measured compositions. Trained model JSON at
`nn/oer_plate_<id>.json`.

## Expected output

`result.csv` contains the recommended composition and its predicted
overpotential: a row of
$(x_1, \ldots, x_6, \hat{y}_{\text{overpotential}})$.

To reproduce:

```bash
cd build
cmake --build . --target oer_plates
./bin/oer_plates
```
