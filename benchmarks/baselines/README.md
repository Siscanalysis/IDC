# pymoo / pycma baselines for the §8 examples

This bundles the baseline optimizers the paper compares IDC against, run on the
**same** trained surrogate and the **same** `problem.yaml` (bounds, objectives,
constraints) the C++ IDC examples use. It makes the per-algorithm feasibility
and constraint-violation comparison of the §8.4 (photo_pce10), §8.5
(concrete_uci_mo), and §8.3 (moeed13) tables reproducible from a clean clone.

## Files

| File | What it is |
|------|-----------|
| `problem_pymoo.py` | `OpennnProblem` — a `pymoo` problem driven by `examples/<ex>/problem.yaml` and the bundled numpy NN export. One source of truth for bounds/objectives/constraints, shared with the C++ side. Its `feasible(x)` returns `(is_feasible, max_violation)`. |
| `run_baselines.py` | Runs the SO pool (CMA-ES, DE, GA, PSO) or MO pool (NSGA-II, NSGA-III, MOEA/D) per `(algorithm, seed)` and writes `results/<ex>_baselines.csv` with `best_f` / hypervolume, feasibility, and the mean `max_violation`. |

The surrogate is evaluated through the self-contained numpy export
`examples/<ex>/nn/<basename>.py` (the same network as the `.json`/`.bin` the C++
example loads).

## Constraint-violation metric

`max_violation` is the largest residual of the returned point across the YAML
constraints (`max(0, g(x))` over each `g(x) <= 0`, including the simplex /
power-balance equalities encoded as tight bands). It is the same quantity the
paper's tables report as "mean constraint violation". IDC's affine repair drives
this to rounding precision; the penalty-based baselines only approach it.

**IDC row.** Rather than have the C++ binary print its own residual,
`run_baselines.py` recovers IDC's `max_violation` by re-checking the bundled
`examples/<ex>/result.csv` (or `expected_output.csv`) against the *same*
constraint evaluator — so every algorithm's violation is computed by one
implementation, and no rebuild is needed. Run the matching C++ example first to
produce `result.csv`.

## Usage

```bash
pip install -r ../requirements.txt          # pymoo, cma, numpy, pandas, pyyaml
python run_baselines.py --example photo_pce10     --seeds 21 --budget 40000   # SO
python run_baselines.py --example concrete_uci_mo --seed  42 --budget 40000   # MO
python run_baselines.py --example moeed13         --seed  42 --budget 40000   # MO
```

Output lands in `benchmarks/baselines/results/<ex>_baselines.csv` (and
`_fronts.csv` for the MO cases). The MO hypervolume here uses a generic
`1.1 x nadir` reference; the paper's normalized-HV ranking is computed in the
authors' workspace.

## Scope

This covers the three §8 example problems. The broader ~30-problem catalog
baseline comparison still runs from the authors' workspace
(`experiments/IDC_benchmark/`), as noted in the top-level README.
