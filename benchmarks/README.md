# Benchmark suite

The analytical / catalog sweeps behind §8 of the paper, plus the
switch-driven runners for the broader catalog of ~30 problems that §8.1
points to but does not show explicitly.

## Contents

```
benchmarks/
├── README.md                ← this file
├── requirements.txt         ← pip dependencies
├── run_idc_21seeds.py       ← drives IDC on all catalog problems
├── run_olympus.py           ← Olympus real-data runner; --task switch (default photo_pce10)
├── aggregate_21seeds.py     ← per-problem + combined summaries
├── make_figures.py          ← regenerates the figures in the paper
├── make_convergence_figure.py ← renders the §8.4 photo_pce10 convergence-vs-budget figure
├── extra_results/           ← committed result snapshots beyond §8 (see its README)
├── bbob/
│   ├── README.md            ← BBOB switch reference
│   ├── run_bbob_suites.py   ← COCO suite driver; --suite switch (default bbob-biobj-mixint, §8.2)
│   ├── run_bbob_stress.py   ← f15–f24 hard-multimodal stress test (§7.3), no COCO
│   └── results/             ← output CSVs (gitignored)
└── results/
    ├── branch_a/            ← per-problem CSVs from the catalog sweep (gitignored)
    └── olympus/             ← per-task CSVs from run_olympus.py (gitignored)
```

## What maps to which §

| Script | Paper § | Default behavior |
|--------|---------|------------------|
| `bbob/run_bbob_suites.py` | §8.2 analytical validation | runs `bbob-biobj-mixint` (the only suite shown) |
| `bbob/run_bbob_stress.py` | §7.3 limitations | runs f15–f24 at *n*=5 and *n*=20 |
| `run_olympus.py`          | §8.4 real-application SO | runs `photo_pce10` (the only task shown) |
| `run_idc_21seeds.py`      | §8.1 catalog pointer | runs every catalog problem, 21 seeds |

## Switches for problems NOT shown in the paper

The manuscript shows one BBOB suite and one Olympus task. The runners can
reproduce the rest of the catalog through switches:

```bash
# Other COCO suites (paper shows only bbob-biobj-mixint)
python bbob/run_bbob_suites.py --list-suites
python bbob/run_bbob_suites.py --suite bbob-mixint
python bbob/run_bbob_suites.py --suite bbob --dimensions 5 10 20

# Hard-multimodal stress test at extra dimensions (paper shows 5 and 20)
python bbob/run_bbob_stress.py --dimensions 5 20 40
python bbob/run_bbob_stress.py --functions 15 16 --algorithms IDC

# Other Olympus tasks (paper shows only photo_pce10)
python run_olympus.py --list-tasks
python run_olympus.py --task snar
python run_olympus.py --task alkox --objective so
```

Each runner prints a `[note]` line whenever it is asked for a
problem/suite/task that is not shown explicitly in the manuscript, so it
is always clear when output falls outside the paper's reported scope.

Committed result snapshots for the broader catalog (single-objective
top-5% holdout over 15 problems, and the multi-objective HV/IGD table)
live in [`extra_results/`](extra_results/) — these are the "additional
reproducible tests" the manuscript points to.

The §8.4 convergence figure is rendered from a committed trace:

```bash
python make_convergence_figure.py     # -> fig_conv_photo_pce10.pdf
```

It reads `extra_results/photo_pce10_convergence.csv` (best feasible
photo-degradation vs surrogate evaluations for IDC and the SO baselines
on the five top-5% holdout surrogates) and needs only matplotlib + numpy.

## Reproducing the §8.2 / catalog numbers

```bash
cd benchmarks
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python bbob/run_bbob_suites.py     # §8.2 analytical validation (default suite)
python bbob/run_bbob_stress.py     # §7.3 f15–f24 stress test
python run_olympus.py              # §8.4 photo_pce10 real-application SO
python run_idc_21seeds.py          # full catalog, 21 seeds each
python aggregate_21seeds.py        # produces all_problems_21seeds.csv
python make_figures.py             # regenerates the figures in §8
```

Expected runtime on commodity hardware (i7 8-core): ~[TBD] hours.

## Optional dependencies

- `run_bbob_suites.py` needs `cocoex` (official COCO binding). When it is
  missing the script prints install hints and points to
  `run_bbob_stress.py`, which needs no COCO.
- `run_bbob_stress.py` needs only `numpy` for `--algorithms IDC`; `cma`
  for CMA-ES and `scipy` for DE.
- `run_olympus.py` needs the `olympus` package to materialize task data,
  or a pre-exported CSV under `../data/olympus/<task>/`.

## Status

This is a scaffold. The runner scripts above expose the full switch
surface and the self-contained pieces (the f15–f24 stress test) run
today; the COCO-suite and Olympus optimization back-ends are ported from
the authors' working trees at `experiments/IDC_benchmark/` and
`experiments/Papers/first_IDC_paper/afte_first_review/experiments/` once
§8 of the paper is finalized.

## Per-problem CSV schema

Every `branch_a/<problem>_idc.csv` produced by `run_idc_21seeds.py`
follows the schema:

| Column          | Type    | Description |
|-----------------|---------|-------------|
| `seed`          | int     | 0–20 |
| `algorithm`     | string  | `idc_default`, `idc_tight`, `cmaes`, … |
| `best_f`        | float   | best objective value found |
| `feasible`      | bool    | True if the returned point is feasible |
| `walltime_s`    | float   | wall-clock seconds |
| `n_evals`       | int     | total surrogate evaluations |
| `n_iters`       | int     | IDC iterations (1 for non-IDC baselines) |
| extra per-problem columns | float   | input coordinates of the best point, where relevant |

The aggregator (`aggregate_21seeds.py`) consumes these and produces the
cross-problem summary in `all_problems_21seeds.csv`.
