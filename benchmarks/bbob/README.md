# BBOB / COCO analytical validation

Two distinct BBOB uses appear in the paper. They live in two scripts here.

## 1. `run_bbob_suites.py` — the §7.2 analytical validation

The paper ran IDC against the pymoo MO baselines (NSGA-II / NSGA-III /
MOEA/D) and the pymoo/pycma SO baselines on **every** COCO suite, but
shows only the bi-objective mixed-integer suite explicitly in §7.2,
because that is the analytical regime where IDC wins decisively. The
other four suites are summarized qualitatively in §6.3 and reported in
full only here.

The `--suite` switch selects which COCO suite to run:

| `--suite`            | Objective | Shown in paper? |
|----------------------|-----------|-----------------|
| `bbob`               | continuous SO | no (catalog only) |
| `bbob-mixint`        | SO mixed-integer | no (catalog only) |
| `bbob-constrained`   | SO constrained | no (catalog only) |
| `bbob-biobj`         | continuous MO | no (catalog only) |
| `bbob-biobj-mixint`  | MO mixed-integer | **yes — §7.2 (default)** |

```bash
python run_bbob_suites.py                       # §7.2 (default suite)
python run_bbob_suites.py --list-suites         # show all five
python run_bbob_suites.py --suite bbob-mixint   # a suite NOT in the paper
python run_bbob_suites.py --suite bbob --dimensions 5 10 20
```

This driver needs the official COCO binding `cocoex` (an optional
dependency that does not build on every Python version). If `cocoex` is
unavailable, the script prints install hints and points you to the
stress test below, which needs no COCO.

### Scope, budget, and the matched-budget guarantee (§7.2)

`bbob-biobj-mixint` spans **92** functions × **6** dimensions
($n_c \in \{5,10,20,40,80,160\}$) × **15** instances, run for **21** seeds per
cell. Every algorithm gets the **same per-problem evaluation budget** (default
$5000$). The budget is matched in the strict sense: the BBOB functions are
analytical (no surrogate), so IDC counts one evaluation per sampled point and
*splits* its budget across the bi-objective weight scalarizations it solves —
it is therefore, if anything, *conservatively* budgeted relative to the
single-front population baselines. This is unlike the surrogate-model MO loop of
§7.3/§7.5, where IDC's per-Pareto-point sampling must be capped explicitly
(`set_max_total_evaluations`) to equalize the budget.

### `coco_runner.py` — the per-problem backend

`run_bbob_suites.py` delegates each run to `coco_runner.run_problem(...)`:
- **baselines** (NSGA-II / NSGA-III / MOEA-D) are run exactly, via pymoo under
  `MaximumFunctionCallTermination(budget)`;
- **IDC** is run via a self-contained, budget-fair *reference* Python
  interval-domain-contraction optimizer (weighted-sum scalarization, budget
  split across $K$ weights, uniform-sample + contract). It reproduces the
  qualitative §7.2 trend (IDC's advantage growing with dimension).

**Provenance.** The paper's *headline* §7.2 numbers were produced with the
authors' C++ MultiSeedIDC analytical solver (same budget-fair methodology) plus
`cocopp` post-processing. Those authoritative win tallies are committed under
[`results/bbob-biobj-mixint/`](results/bbob-biobj-mixint/)
(`summary_idc_wins.csv`, `per_function_idc_wins.csv`), and the §7.2 **table is
reproducible directly from them** — no re-run needed:

```bash
python parse_cocopp_idc_wins.py   # re-derives the win tallies from cocopp output
cat results/bbob-biobj-mixint/summary_idc_wins.csv
# bbob-biobj-mixint per dim 5..160: wins 63/59/70/85/90/91 of 92,
# cell-win rate 0.67/0.57/0.70/0.91/0.98/1.00  (Table tab:bbob_biobj_mixint)
```

## 2. `run_bbob_stress.py` — the §6.3 hard-multimodal stress test

The f15–f24 hard-multimodal subset reported in §6.3 (limitations) as the
dimensionality stress test: IDC is competitive at *n*=5 but degrades at
*n*=20. This is a **non-surrogate** test — IDC, CMA-ES, and DE run
directly on the analytical functions — so it deliberately removes the
cheap-evaluation advantage that motivates IDC.

It runs without COCO, on canonical mathematical forms of the functions
(no COCO rotation/normalization; the per-(function, seed) shift is an
origin-symmetry device). Switches:

```bash
python run_bbob_stress.py                              # §6.3 as reported
python run_bbob_stress.py --functions 15 16 --dimensions 5
python run_bbob_stress.py --dimensions 5 20 40        # extra dims (not in paper)
python run_bbob_stress.py --algorithms IDC            # IDC only (no cma/scipy deps)
```

`--algorithms IDC` needs only `numpy`; CMA-ES needs `cma`, DE needs
`scipy`.

## Outputs

```
results/<suite>/<suite>_idc_vs_pymoo.csv         ← run_bbob_suites.py (per-run, gitignored)
results/bbob/bbob_stress.csv                      ← run_bbob_stress.py (gitignored)
results/bbob-biobj-mixint/summary_idc_wins.csv    ← COMMITTED §7.2 win tallies
results/bbob-biobj-mixint/per_function_idc_wins.csv ← COMMITTED per-cell verdicts
```

The per-run sweep CSVs are gitignored, but the **authoritative §7.2 win
tallies are committed** (the two files above), so the §7.2 table reproduces
from committed data via `parse_cocopp_idc_wins.py`. The other four COCO suites
(catalog only, not shown in the paper) are aggregated by the authors' workspace
tooling; see the "Not bundled" note in [`../README.md`](../README.md).
