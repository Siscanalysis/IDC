# SOURCE — MOEED13 (13-unit economic-emission dispatch)

Used by §7.3 (`examples/moeed13/`, the simulator-grounded MO validation).

## Files

| File | Rows | Description |
|------|------|-------------|
| `moeed13_sample.csv` | 200 | A small **illustrative sample** of the simulator output so the schema is visible at a glance. Columns: `P_0 … P_12` (per-unit power setpoints, MW) and `total_cost` ($/h), `total_emission` (lb/h). |

> **This is simulator output, not measurement data.** MOEED13 has no
> measured table to redistribute: the objective surface is the two
> closed-form formulas below, evaluated over box-uniform samples of the
> 13 power setpoints. The full $10^5$-row training table used in the
> paper is regenerated on demand from the coefficient tables (it is not
> stored in-tree because it is large and reproducible); the 200-row
> sample here is only to show the column layout and value ranges.

## Formulas (the "simulator")

For power setpoints $P_i$, $i = 0 \ldots 12$:

```
cost(P)     = Σ_i [ a_i + b_i P_i + c_i P_i^2 + |e_i sin(f_i (P_min,i − P_i))| ]   [$/h]
emission(P) = Σ_i [ α_i + β_i P_i + γ_i P_i^2 + ξ_i exp(λ_i P_i) ]                 [lb/h]
```

- Cost coefficients $(a_i, b_i, c_i, e_i, f_i)$: **Walters & Sheblé 1993,
  Table I** (13-unit valve-point bus).
- Emission coefficients $(\alpha_i, \beta_i, \gamma_i, \xi_i, \lambda_i)$:
  **Abido 2003** type-based NOₓ parameterization.

## Citations

> Walters, D. C.; Sheblé, G. B. (1993). "Genetic algorithm solution of
> economic dispatch with valve point loading." *IEEE Transactions on
> Power Systems*, 8(3), 1325–1332. https://doi.org/10.1109/59.260861

> Abido, M. A. (2003). "Environmental/economic power dispatch using
> multiobjective evolutionary algorithms." *IEEE Transactions on Power
> Systems*, 18(4), 1529–1537. https://doi.org/10.1109/TPWRS.2003.818693

BibTeX:

```bibtex
@article{WaltersSheble1993,
  author  = {Walters, David C. and Shebl\'e, Gerald B.},
  title   = {Genetic algorithm solution of economic dispatch with valve
             point loading},
  journal = {IEEE Transactions on Power Systems},
  volume  = {8}, number = {3}, pages = {1325--1332}, year = {1993},
  doi     = {10.1109/59.260861}
}

@article{Abido2003,
  author  = {Abido, M. A.},
  title   = {Environmental/economic power dispatch using multiobjective
             evolutionary algorithms},
  journal = {IEEE Transactions on Power Systems},
  volume  = {18}, number = {4}, pages = {1529--1537}, year = {2003},
  doi     = {10.1109/TPWRS.2003.818693}
}
```

## Notes

- Per-unit box bounds and the power-balance equality constraint are
  defined in
  [`../../examples/moeed13/constraints.yaml`](../../examples/moeed13/constraints.yaml).
- The full table is box-sampled per $[P_{\min,i}, P_{\max,i}]$ and does
  **not** itself satisfy the power-balance equality; the equality is
  enforced at optimization time (IDC affine repair / pymoo penalty).
