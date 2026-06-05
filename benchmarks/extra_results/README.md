# Extra reproducible tests (beyond the manuscript §7)

These are committed result snapshots from the broader benchmark catalog
that §7.1 of the paper points to but does not tabulate. They are produced
by the same code paths as the §7 examples — the runners in
[`../`](../) with the `--task` / `--suite` switches — at the same IDC
default configuration and matched 40k budget. They are included so the
catalog claims in the paper are inspectable without re-running the full
sweep.

> **Scope and honesty.** This is the *full* per-problem output, not a
> cherry-picked subset: IDC wins decisively on some problems, ties on
> others, and loses to the pymoo baselines on a few. The headlines below
> point at both. The numbers are snapshots from the authors' working
> tree (`experiments/IDC_benchmark/`); re-running the switches reproduces
> them up to seed/compiler drift.

## Files

| File | What it is |
|------|-----------|
| `mo_catalog_hv_igd.csv` | Multi-objective catalog: hypervolume (HV, higher better) per (problem, algorithm) at the 40k matched budget, IDC vs NSGA-II / NSGA-III / MOEA/D. (The `igd` column is a legacy extra; the paper ranks by HV and reports the geometric front-quality metrics, not IGD.) |
| `photo_pce10_convergence.csv` | Convergence trace for the §7.4 figure: best feasible photo-degradation vs surrogate evaluations for IDC and the SO baselines, averaged over the five top-5% holdout surrogates. Rendered by [`../make_convergence_figure.py`](../make_convergence_figure.py). |

## Single-objective held-out diagnostics (value_gap / space_gap)

The §7.4 held-out diagnostics use the two-metric `value_gap` / `space_gap`
pair (§7.1 of the paper) and are **reproduced from a clean clone** by the
held-out pipeline in [`../holdout/`](../holdout/):
`gen_holdout_splits.py` → `train_surrogate` (OpenNN Growing Neurons on the
top-5% split) → IDC / `baselines/run_baselines.py` →
`compute_holdout_gaps.py`. On the representative photo_pce10 held-out
seed, IDC has the smallest `value_gap` (it reaches the held-out
surrogate's feasible optimum) while every algorithm's `space_gap` is
small. The broader single-objective catalog held-out cross-table
(15 problems) is maintained in the authors' workspace and is not bundled
here. See [`../../docs/holdout_procedure.md`](../../docs/holdout_procedure.md).

## Headline multi-objective reads (HV at 40k budget)

| Problem | IDC HV | best pymoo HV | Verdict |
|---------|--------|---------------|---------|
| moeed13 | **2,948,429** | 2,448,850 (NSGA-II) | IDC wins HV +20% |
| lnp3 | **943,499** | 33,645 | IDC wins HV ~28× |
| biochar_ec | 49.1 | 60.8 (NSGA-II) | split: pymoo wins HV, IDC wins on Pareto density |
| suzuki_i / ii / iv | 1,553 / 643 / 1,862 | 1,753 / 672 / 2,176 | pymoo wins HV narrowly (5–17%) |

`moeed13` is the validation case promoted into the manuscript (§7.3);
the rest stay in the catalog.

## Reproducing

```bash
# Single-objective catalog (holdout protocol)
python ../run_olympus.py --task hplc      # or fullerenes, snar, alkox, ...
# the full SO catalog sweep (run_idc_21seeds.py) runs from the authors'
# workspace and is not bundled in this companion

# Multi-objective catalog
#   moeed13 is the §7.3 example; the other MO entries (lnp3, biochar_ec,
#   suzuki_*) are run from the authors' MO drivers in
#   experiments/IDC_benchmark/ and mirrored here.
```

IDC default config and budget are documented in
[`../../docs/reproducing.md`](../../docs/reproducing.md).
