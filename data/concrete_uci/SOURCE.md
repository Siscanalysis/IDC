# SOURCE — UCI Concrete Compressive Strength

Used by §8.5 (`examples/concrete_uci_mo/`, the multi-objective case study)
and by the catalog single-objective example
(`examples/additional/concrete_uci_so/`).

## Files

| File | Rows | Description |
|------|------|-------------|
| `concrete_uci.csv` | 1030 | The dataset used to train the surrogate. Columns: `cement, slag, fly_ash, water, sp, coarse_agg, fine_agg, age, strength`. Ingredient masses in kg/m³, `age` in days, `strength` (28-day compressive) in MPa. |
| `Concrete_Readme.txt` | — | The original UCI variable descriptions, verbatim. |

## Upstream

- **Dataset:** *Concrete Compressive Strength*, UCI Machine Learning
  Repository, dataset 165.
  <https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength>
- **License:** Creative Commons Attribution 4.0 International (CC-BY 4.0).
  Redistribution with attribution is permitted; this directory ships the
  data unmodified except for the CSV column-name header.

## Citation (please cite when you reuse this data)

> Yeh, I-C. (1998). "Modeling of strength of high-performance concrete
> using artificial neural networks." *Cement and Concrete Research*,
> 28(12), 1797–1808. https://doi.org/10.1016/S0008-8846(98)00165-3

BibTeX:

```bibtex
@article{Yeh1998Concrete,
  author  = {Yeh, I-Cheng},
  title   = {Modeling of strength of high-performance concrete using
             artificial neural networks},
  journal = {Cement and Concrete Research},
  volume  = {28},
  number  = {12},
  pages   = {1797--1808},
  year    = {1998},
  doi     = {10.1016/S0008-8846(98)00165-3}
}
```

## Notes

- The multi-objective framing (maximize strength, minimize cement) is an
  internal reformulation for the paper; it is **not** part of the
  original Yeh 1998 dataset, which is single-target (strength). The
  cement objective is a passthrough on the `cement` input column — no
  extra data is needed for it.
- Engineering constraints applied at optimization time
  (water/cement bounds, mass balance, binder floor, slag/fly-ash
  replacement) are defined in
  [`../../examples/concrete_uci_mo/constraints.yaml`](../../examples/concrete_uci_mo/constraints.yaml);
  their standards provenance (EN 206, ASTM C595) is documented there.
