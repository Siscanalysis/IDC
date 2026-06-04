# Extra reproducible tests (beyond the manuscript §8)

These are committed result snapshots from the broader benchmark catalog
that §8.1 of the paper points to but does not tabulate. They are produced
by the same code paths as the §8 examples — the runners in
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
| `so_holdout_top05_per_entry.csv` | Single-objective top-5% holdout cross-table over 15 catalog problems, 5 surrogate seeds each. Four metrics per (entry, optimizer): `absolute_gap`, `relative_gap` (value-space), `absolute_geo`, `relative_geo` (input-space), reported as median/p25/p75. IDC is run at 5 configs (`idc_default` + 4 sweep variants); pymoo at cmaes/de/ga/pso. |
| `mo_catalog_hv_igd.csv` | Multi-objective catalog: hypervolume (HV, higher better) and IGD (lower better) per (problem, algorithm) at the 40k matched budget, IDC vs NSGA-II / NSGA-III / MOEA/D. |
| `photo_pce10_convergence.csv` | Convergence trace for the §8.4 figure: best feasible photo-degradation vs surrogate evaluations for IDC and the SO baselines, averaged over the five top-5% holdout surrogates. Rendered by [`../make_convergence_figure.py`](../make_convergence_figure.py). |

> **Metric note.** This SO cross-table uses the earlier **four-metric**
> variant of the holdout protocol (`absolute_gap` / `relative_gap` for
> value-space, `absolute_geo` / `relative_geo` for input-space). It
> captures the same value-vs-space distinction as the paper's consolidated
> **two-metric** `value_gap` / `space_gap` pair, which is what the headline
> §8.4 / §8.5 case studies report. See
> [`../../docs/holdout_procedure.md`](../../docs/holdout_procedure.md).

## Headline single-objective reads (input-space recovery)

The paper's central reliability claim is that IDC recovers the *region*
of the held-out optimum in **input space**, not just a surrogate-pleasing
value. `relative_geo` (median, `idc_default` vs the best pymoo baseline;
lower = closer to the held-out optimum) bears this out:

| Problem | IDC `relative_geo` | best pymoo `relative_geo` | IDC advantage |
|---------|-------------------|---------------------------|---------------|
| yacht_hydrodynamics | 0.232 | 0.744 | ~3.2× closer |
| olympus_fullerenes | 0.138 | 0.448 | ~3.2× closer |
| olympus_hplc | 0.193 | 0.414 | ~2.1× closer |
| olympus_oer_plate_3851 | 0.067 | 0.111 (ga) | ~1.7× closer |
| concrete_compressive_strength | 0.368 | 0.519 | ~1.4× closer |

(pymoo often edges IDC on the *value* gap by pushing the surrogate into
extrapolation at a distant point — exactly the failure mode the
input-space metric is designed to expose. See
[`../../docs/holdout_procedure.md`](../../docs/holdout_procedure.md).)

## Headline multi-objective reads (HV / IGD at 40k budget)

| Problem | IDC HV | best pymoo HV | Verdict |
|---------|--------|---------------|---------|
| moeed13 | **2,948,429** (IGD **1.75**) | 2,448,850 (NSGA-II, IGD 193.9) | IDC wins HV +20% and IGD decisively |
| lnp3 | **943,499** | 33,645 | IDC wins HV ~28× |
| biochar_ec | 49.1 (IGD **0.0015**) | 60.8 (NSGA-II, IGD 0.13) | split: pymoo wins HV, IDC wins IGD + Pareto density |
| suzuki_i / ii / iv | 1,553 / 643 / 1,862 | 1,753 / 672 / 2,176 | pymoo wins HV narrowly (5–17%) |

`moeed13` is the validation case promoted into the manuscript (§8.3);
the rest stay in the catalog.

## Reproducing

```bash
# Single-objective catalog (holdout protocol)
python ../run_olympus.py --task hplc      # or fullerenes, snar, alkox, ...
# the full SO catalog sweep (run_idc_21seeds.py) runs from the authors'
# workspace and is not bundled in this companion

# Multi-objective catalog
#   moeed13 is the §8.3 example; the other MO entries (lnp3, biochar_ec,
#   suzuki_*) are run from the authors' MO drivers in
#   experiments/IDC_benchmark/ and mirrored here.
```

IDC default config and budget are documented in
[`../../docs/reproducing.md`](../../docs/reproducing.md).
