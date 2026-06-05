# SOURCE — BBOB / COCO analytical functions

Used by §7.2 (`benchmarks/bbob/`, the analytical validation) and §6.3
(the f15–f24 hard-multimodal stress test).

## No dataset

BBOB is an **analytical** benchmark: there is no measured table to ship.
The objective values are computed directly from the COCO function
definitions (or, for the no-COCO stress test, from the canonical
mathematical forms ported into
[`../../benchmarks/bbob/run_bbob_stress.py`](../../benchmarks/bbob/run_bbob_stress.py)).

- **Suite source / definitions:** the COCO platform,
  <https://github.com/numbbo/coco>, suites `bbob`, `bbob-mixint`,
  `bbob-constrained`, `bbob-biobj`, `bbob-biobj-mixint`.
- **License:** COCO is released under the 3-clause BSD license.

## Citations

> Hansen, N.; Auger, A.; Ros, R.; Mersmann, O.; Tušar, T.; Brockhoff, D.
> (2021). "COCO: A platform for comparing continuous optimizers in a
> black-box setting." *Optimization Methods and Software*, 36(1), 114–144.
> https://doi.org/10.1080/10556788.2020.1808977

> Tušar, T.; Brockhoff, D.; Hansen, N.; Auger, A. (2016). "COCO: The
> bi-objective black box optimization benchmarking (bbob-biobj) test
> suite." arXiv:1604.00359.

BibTeX:

```bibtex
@article{Hansen2021COCO,
  author  = {Hansen, Nikolaus and Auger, Anne and Ros, Raymond and
             Mersmann, Olaf and Tu\v{s}ar, Tea and Brockhoff, Dimo},
  title   = {{COCO}: A platform for comparing continuous optimizers in a
             black-box setting},
  journal = {Optimization Methods and Software},
  volume  = {36}, number = {1}, pages = {114--144}, year = {2021},
  doi     = {10.1080/10556788.2020.1808977}
}
```

## Constraints

The mixed-integer suites impose two structural constraints, documented in
[`../../benchmarks/bbob/constraints_bbob_biobj_mixint.md`](../../benchmarks/bbob/constraints_bbob_biobj_mixint.md):
box bounds on every coordinate and integrality on the integer block.
