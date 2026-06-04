# BBOB / COCO analytical validation

Two distinct BBOB uses appear in the paper. They live in two scripts here.

## 1. `run_bbob_suites.py` — the §8.2 analytical validation

The paper ran IDC against the pymoo MO baselines (NSGA-II / NSGA-III /
MOEA/D) and the pymoo/pycma SO baselines on **every** COCO suite, but
shows only the bi-objective mixed-integer suite explicitly in §8.2,
because that is the analytical regime where IDC wins decisively. The
other four suites are summarized qualitatively in §7.3 and reported in
full only here.

The `--suite` switch selects which COCO suite to run:

| `--suite`            | Objective | Shown in paper? |
|----------------------|-----------|-----------------|
| `bbob`               | continuous SO | no (catalog only) |
| `bbob-mixint`        | SO mixed-integer | no (catalog only) |
| `bbob-constrained`   | SO constrained | no (catalog only) |
| `bbob-biobj`         | continuous MO | no (catalog only) |
| `bbob-biobj-mixint`  | MO mixed-integer | **yes — §8.2 (default)** |

```bash
python run_bbob_suites.py                       # §8.2 (default suite)
python run_bbob_suites.py --list-suites         # show all five
python run_bbob_suites.py --suite bbob-mixint   # a suite NOT in the paper
python run_bbob_suites.py --suite bbob --dimensions 5 10 20
```

This driver needs the official COCO binding `cocoex` (an optional
dependency that does not build on every Python version). If `cocoex` is
unavailable, the script prints install hints and points you to the
stress test below, which needs no COCO.

## 2. `run_bbob_stress.py` — the §7.3 hard-multimodal stress test

The f15–f24 hard-multimodal subset reported in §7.3 (limitations) as the
dimensionality stress test: IDC is competitive at *n*=5 but degrades at
*n*=20. This is a **non-surrogate** test — IDC, CMA-ES, and DE run
directly on the analytical functions — so it deliberately removes the
cheap-evaluation advantage that motivates IDC.

It runs without COCO, on canonical mathematical forms of the functions
(no COCO rotation/normalization; the per-(function, seed) shift is an
origin-symmetry device). Switches:

```bash
python run_bbob_stress.py                              # §7.3 as reported
python run_bbob_stress.py --functions 15 16 --dimensions 5
python run_bbob_stress.py --dimensions 5 20 40        # extra dims (not in paper)
python run_bbob_stress.py --algorithms IDC            # IDC only (no cma/scipy deps)
```

`--algorithms IDC` needs only `numpy`; CMA-ES needs `cma`, DE needs
`scipy`.

## Outputs

```
results/<suite>/<suite>_idc_vs_pymoo.csv   ← run_bbob_suites.py
results/bbob/bbob_stress.csv               ← run_bbob_stress.py
```

Both are gitignored. Aggregate the suite win/tie/loss tallies with
[`../aggregate_21seeds.py`](../aggregate_21seeds.py).
