# IDC default hyperparameters — how they were chosen

All §7 results use a **single default IDC configuration**

| Hyperparameter | Symbol | Value |
|---|---|---|
| candidates per iteration | `N` | 2000 |
| zoom factor | `γ` | 0.85 |
| max iterations | `I_max` | 20 |
| relative tolerance | `τ` | 1e-6 |

(shorthand `e2000_i20_z85`). This default was **not** hand-picked: it is the
cross-problem-stable winner of an offline grid search, run once and then frozen.
Per-problem tuning is **not** used anywhere in the paper.

## The grid search

An adaptive two-phase search over IDC's three free hyperparameters
(`τ` fixed at 1e-6):

- `evals_per_iter ∈ {500, 1000, 2000, 4000, 8000}`
- `max_iter      ∈ {10, 20, 40}`
- `zoom_factor   ∈ {0.30, 0.45, 0.60, 0.75, 0.85, 0.95}`

**Phase 1** — 90 coarse configurations × 5 seeds on every problem.
**Phase 2** — ±1-step refinement around each problem's top-3, at 21 seeds.
Each configuration is scored by its **mean rank across the problems**; the
configuration with the best cross-problem mean rank (restricted to configs that
ran on ≥ 19 of the problems, so problem-specific outliers do not win) is
promoted. At the 40 000-evaluation budget used for the IDC-vs-baseline
comparisons, that winner is `e2000_i20_z85` — the default above.

The driver, orchestrator, the auto-generated per-problem config JSONs, and the
per-problem / mean-rank result tables are maintained in the authors' separate
benchmark workspace (not bundled in this companion); the grid is reproduced by
re-running the two-phase procedure described above (driver `grid_idc.cpp`,
orchestrator `run_grid.py`), so the search is reproducible from the procedure
rather than from committed sweep outputs.

## Tuning problems (23)

The search ranks each configuration across a broad Level-1 suite. **Note:** this
suite overlaps the §7 case studies (`concrete_uci`, `photo_pce10` appear in
both); because the default is selected for cross-problem stability rather than
per-problem performance, it is not tuned to any single case study, but the
overlap is stated here for transparency.

```
agnp  airfoil  alkox  autoam  benzylation  colors_bob  colors_n9
concrete_uci  crossed_barrel  fullerenes  hplc  oer_plate_3496
oer_plate_3851  oer_plate_3860  oer_plate_4098  p3ht  photo_pce10
photo_wf3  snar  suzuki  thin_film  wine_white  yacht
```

## Where to find the data

We do not redistribute the datasets here; the list below locates them at source.

- **Olympus experiment-planning campaigns** — `agnp`, `alkox`, `autoam`,
  `benzylation`, `colors_bob`, `colors_n9`, `crossed_barrel`, `fullerenes`,
  `hplc`, `oer_plate_3496/3851/3860/4098`, `p3ht`, `photo_pce10`, `photo_wf3`,
  `snar`, `suzuki`, `thin_film`:
  <https://github.com/aspuru-guzik-group/olympus>
  (Häse et al., *Olympus: a benchmarking framework for noisy optimization and
  experiment planning*, 2021).
- **UCI Machine Learning Repository** — `concrete_uci` (Concrete Compressive
  Strength), `wine_white` (Wine Quality), `yacht` (Yacht Hydrodynamics),
  `airfoil` (Airfoil Self-Noise): <https://archive.ics.uci.edu/>

Per-entry source/citation and the exact column mapping used to train each
surrogate are catalogued in the benchmark dataset tree (`<entry>/description.txt`).
