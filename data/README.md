# Datasets

Curated subset of the benchmark datasets used by the §8 worked
examples in [`../examples/`](../examples/). The two real-measurement
datasets are small and permissively licensed, so they ship **in-tree** —
you can open them directly without running any fetch step.

## What is here

| Path                       | Used by §                | In-tree file(s) | Source | License |
|----------------------------|--------------------------|-----------------|--------|---------|
| `concrete_uci/`            | 8.5 (and catalog SO)     | `concrete_uci.csv` (1030 rows, 57 KB) + `Concrete_Readme.txt` | UCI ML repository (Yeh 1998) | CC-BY-4.0 |
| `photo_pce10/`             | 8.4                      | `photo_pce10.csv` (1040 rows, 32 KB) | Olympus / Langner et al. 2020 | MIT |
| `moeed13/`                 | 8.3                      | `moeed13_sample.csv` (200-row sample, 32 KB) | Walters–Sheblé 1993 + Abido 2003 (simulator) | coefficients in-paper; generator MIT |
| `bbob/`                    | 8.2 / 7.3                | none (analytical) | COCO / BBOB | BSD-3 |
| `olympus/`                 | catalog (`run_olympus.py`) | none (fetched on demand) | Olympus | MIT |
| `oer_plates/`              | catalog (`additional/`)  | [TBD] | [TBD upstream attribution] | [TBD] |

Each folder carries a **`SOURCE.md`** with the full citation, license,
and BibTeX — please cite the original dataset paper(s) when you reuse the
data. The per-example **constraints** are not in `data/`; they live next
to each example as `examples/<name>/constraints.yaml` (the file the
optimizer actually loads).

Notes:

- The §8.2 BBOB bi-objective mixed-integer validation needs **no
  dataset**: it is evaluated directly from the analytical COCO functions
  (see [`../benchmarks/bbob/`](../benchmarks/bbob/) and
  [`bbob/SOURCE.md`](bbob/SOURCE.md)).
- `moeed13/` ships only a small illustrative **sample** of the simulator
  output; the full $10^5$-row training table is regenerated on demand
  from the coefficient tables (large and reproducible, so not stored
  in-tree).
- `olympus/` is populated on demand from the `olympus` package by
  `run_olympus.py`; only `photo_pce10` is shown in the paper, and it is
  shipped in-tree above.

The full benchmark dataset workspace used by the authors during
development lives at `experiments/benchmark_datasets/` in the authors'
working tree; this companion repository ships only the subset needed to
reproduce the §8 examples.

## Upstream attribution

Each subfolder includes a `SOURCE.md` describing the upstream dataset,
the exact subset used in the paper, any preprocessing applied, and the
citation. Please cite the original dataset paper in addition to this
work if you reuse them.

## Adding a new dataset

If you want to extend the worked examples with an additional dataset:

1. Add a new `<example_name>/` folder under `../examples/`.
2. Add the dataset (or fetcher) under `data/<example_name>/`.
3. Add a `SOURCE.md` with the upstream citation and license.
4. Wire up the `add_subdirectory(...)` line in the top-level
   `CMakeLists.txt`.
5. Submit a pull request — community datasets are welcome.
