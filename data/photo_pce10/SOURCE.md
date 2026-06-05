# SOURCE — Olympus `photo_pce10` (quaternary OPV photostability)

Used by §7.4 (`examples/photo_pce10/`, the real-application SO case study).

## Files

| File | Rows | Description |
|------|------|-------------|
| `photo_pce10.csv` | 1040 | Measured blends. Columns: `mat_1, mat_2, mat_3, mat_4, degradation`. The four `mat_*` are mass fractions in [0,1] summing to 1: `mat_1`=PCE10, `mat_2`=P3HT (donors), `mat_3`=PCBM, `mat_4`=oIDTBR (acceptors). `degradation` is the normalized post-ageing efficiency drop (lower is better). |

## Upstream

- **Dataset:** task `photo_pce10` in the **Olympus** benchmark suite
  (the suite re-packages the Langner et al. campaign data).
  <https://github.com/aspuru-guzik-group/olympus>
- **Original campaign data:**
  <https://github.com/aspuru-guzik-group/quaterny_opvs>
- **License:** MIT (Olympus). Redistribution with attribution permitted.

## Citations (please cite both the campaign and Olympus)

Original high-throughput campaign that produced the measurements:

> Langner, S.; Häse, F.; Perea, J. D.; Stubhan, T.; Hauch, J.;
> Roch, L. M.; Heumüller, T.; Aspuru-Guzik, A.; Brabec, C. J. (2020).
> "Beyond Ternary OPV: High-Throughput Experimentation and Self-Driving
> Laboratories Optimize Multicomponent Systems." *Advanced Materials*,
> 32(14), 1907801. https://doi.org/10.1002/adma.201907801

Benchmark suite that packages the task:

> Häse, F.; Aldeghi, M.; Hickman, R. J.; Roch, L. M.; Christensen, M.;
> Liles, E.; Hein, J. E.; Aspuru-Guzik, A. (2021). "Olympus: a benchmarking
> framework for noisy optimization and experiment planning."
> *Machine Learning: Science and Technology*, 2(3), 035021.
> https://doi.org/10.1088/2632-2153/abedc8

BibTeX:

```bibtex
@article{Langner2020OPV,
  author  = {Langner, Stefan and H\"ase, Florian and Perea, Jos\'e Dar\'io
             and Stubhan, Tobias and Hauch, Jens and Roch, Lo\"ic M. and
             Heum\"uller, Thomas and Aspuru-Guzik, Al\'an and Brabec,
             Christoph J.},
  title   = {Beyond Ternary OPV: High-Throughput Experimentation and
             Self-Driving Laboratories Optimize Multicomponent Systems},
  journal = {Advanced Materials},
  volume  = {32},
  number  = {14},
  pages   = {1907801},
  year    = {2020},
  doi     = {10.1002/adma.201907801}
}

@article{Hase2021Olympus,
  author  = {H\"ase, Florian and Aldeghi, Matteo and Hickman, Riley J. and
             Roch, Lo\"ic M. and Christensen, Melodie and Liles, Elena and
             Hein, Jason E. and Aspuru-Guzik, Al\'an},
  title   = {Olympus: a benchmarking framework for noisy optimization and
             experiment planning},
  journal = {Machine Learning: Science and Technology},
  volume  = {2},
  number  = {3},
  pages   = {035021},
  year    = {2021},
  doi     = {10.1088/2632-2153/abedc8}
}
```

## Notes

- The optimization **minimizes** photo-degradation (not "maximize PCE").
- Constraints applied at optimization time (the 4-component simplex and
  the donor-processability band) are defined in
  [`../../examples/photo_pce10/constraints.yaml`](../../examples/photo_pce10/constraints.yaml).
- Other Olympus tasks reachable via `benchmarks/run_olympus.py --task ...`
  are materialized on demand from the `olympus` package and are not
  shipped in-tree.
