# Reproducing the paper

This document gives the recipe to build and run the §8 worked examples
and validation sweeps from a clean clone of this repository. The bundled
tooling covers the three C++ case studies (§8.3–§8.5), the BBOB / Olympus
validation runners, the `photo_pce10` 21-seed sweep + aggregation, the
surrogate-quality audit, and the MO figure-regeneration. The broader
~14-problem SO catalog sweep and the pymoo/pycma baseline comparison are
part of the authors' workspace and are not shipped here.

For the conceptual overview of IDC, see [architecture.md](architecture.md).
For the memorization/hallucination safeguards used in the §8.4 (top-5%
holdout) and §8.5 (age-28 restriction) real-application case studies, see
[holdout_procedure.md](holdout_procedure.md).

---

## Prerequisites

- **C++20 toolchain** (OpenNN requires C++20). Tested on:
  - Windows: MSVC 19.3x (Visual Studio 2022)
  - Linux: GCC 11+ or Clang 14+
  - macOS: Apple Clang 14+
- **CMake ≥ 3.20.**
- **Git** (the build fetches OpenNN via `FetchContent`; the default ref is a
  pinned OpenNN commit — the paper version of record — that carries the
  `ResponseOptimization` API, see
  [`cmake/FindOrFetchOpenNN.cmake`](../cmake/FindOrFetchOpenNN.cmake)).
  Eigen (header-only) is fetched automatically by the build, so no manual
  Eigen install or submodule step is needed.

> **MSVC note.** Building the full OpenNN static library from source can be
> heavy on MSVC. If the link step is slow or fails, point the build at a
> prebuilt local checkout instead with
> `cmake -DOPENNN_ROOT=/path/to/opennn ..` (tier 1 of FindOrFetchOpenNN).
- **Python ≥ 3.10** (only for `benchmarks/` aggregation and figure scripts).

For the Python side, install dependencies with:

```bash
cd benchmarks
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Step 1 — Clone and configure

```bash
git clone https://github.com/Siscanalysis/IDC.git
cd IDC
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
```

On first configuration, CMake downloads the pinned OpenNN release
(`OPENNN_DEFAULT_TAG` in [`cmake/FindOrFetchOpenNN.cmake`](../cmake/FindOrFetchOpenNN.cmake))
into `build/_deps/opennn-src/`. To pin a different OpenNN version:

```bash
cmake -DOPENNN_TAG=<tag> -DCMAKE_BUILD_TYPE=Release ..
```

To use a local OpenNN checkout instead (useful if you are developing both):

```bash
cmake -DOPENNN_ROOT=/path/to/local/opennn -DCMAKE_BUILD_TYPE=Release ..
```

---

## Step 2 — Build

```bash
cmake --build . --config Release -j
```

Expected build time: a few minutes on a recent multi-core CPU, dominated
by the one-time OpenNN compilation; subsequent rebuilds are incremental.

---

## IDC configuration and evaluation budget (paper §8.1)

These are the hyperparameters the §8 results are reported at. The
runner defaults reproduce them; the switches documented in
[`../benchmarks/README.md`](../benchmarks/README.md) let you change them
to explore configurations **not** shown in the paper.

**IDC default configuration** (all §8 results unless noted):

| Parameter | Symbol | Value |
|-----------|--------|-------|
| Candidates per iteration | `N` | 2000 |
| Zoom factor | `γ` | 0.85 |
| Max iterations (per-problem) | `I_max` | 5 to 20 |
| Min iterations before termination | `I_min` | 4 |
| Relative termination tolerance | `τ` | 1e-6 |
| Affine repair | — | every iteration |

For the multi-objective continuous-front problems (CONSTR / ZDT1,
discussed in §6 termination) the configuration is reduced to `N = 200`,
`I_max = 3` — a temporary setting flagged in the paper as under study in
the follow-up project.

**Evaluation budget and seeds:**

| Case | § | Budget / seed | Seeds |
|------|---|---------------|-------|
| photo_pce10 (SO real) | 8.4 | 40,000 surrogate calls | 21 |
| MOEED13 (simulator MO) | 8.3 | 40,000 surrogate calls | 21 |
| concrete_uci_mo (MO real) | 8.5 | 40,000 surrogate calls (IDC side caps the empirical Pareto front at 10,000 points) | 21 |
| BBOB bi-objective mixed-integer | 8.2 | COCO-recommended schedule; dims n_c ∈ {5,10,20,40,80,160}, 15 instances/cell | 21 |

**Baselines** (all run against the *same* trained surrogate as IDC, at
the matched budget): single-objective — CMA-ES via `pycma`, plus DE, GA,
PSO via `pymoo`; multi-objective — NSGA-II, NSGA-III, MOEA/D via `pymoo`.

**Held-out protocol** (the two real-application cases, §8.4 / §8.5):
top-5% by objective held out, `S = 5` surrogate-training seeds, 80%
subsample of the remaining rows, 5 × 21 = 105 runs per algorithm. See
[holdout_procedure.md](holdout_procedure.md).

---

## Step 3 — Run a single example

The two real-application C++ case studies are built into `bin/`. To
reproduce just §8.4 (photo_pce10, single-objective):

```bash
./bin/photo_pce10
```

The executable writes `examples/photo_pce10/result.csv` containing
the IDC-recommended input configuration and the corresponding surrogate
output. Compare to the headline number in the §8.4 table of the paper.

The four headline §8 examples map to the following entry points:

| § | Example | Entry point | Block |
|---|---------|-------------|-------|
| 8.2 | BBOB bi-objective mixed-integer | `python benchmarks/bbob/run_bbob_suites.py` | Validation (analytical) |
| 8.3 | MOEED13 economic-emission dispatch | `./bin/moeed13` | Validation (simulator) |
| 8.4 | photo_pce10 | `./bin/photo_pce10` | Real application (SO) |
| 8.5 | concrete_uci_mo | `./bin/concrete_uci_mo` | Real application (MO) |

The §8.2 BBOB validation is Python-only (analytical functions, no
surrogate); the other three are OpenNN C++ executables.

---

## Step 4 — Run the validation sweeps

The analytical and Olympus validation are driven from `benchmarks/`:

```bash
cd benchmarks
python bbob/run_bbob_suites.py    # §8.2 analytical validation (default suite)
python bbob/run_bbob_stress.py    # §7.3 f15–f24 hard-multimodal stress test
python run_olympus.py             # §8.4 photo_pce10 (Olympus real-data SO)
python run_idc_21seeds.py         # §8.4 photo_pce10 IDC sweep, 21 seeds
python aggregate_21seeds.py       # per-problem summary (mean ± std, best, feas%)
python audit_surrogates.py        # §8.5 surrogate-quality R² audit table
python make_figures.py            # §8 MO figures from committed CSVs
python make_convergence_figure.py # §8.4 best-feasible-vs-evaluations figure
```

Expected runtime: on the order of a couple of hours on a recent multi-core
CPU. Wall-clock is dominated by the pymoo baselines (~20 s per seed); IDC
itself runs in well under a second per seed, and the three C++ case-study
examples alone finish in seconds. (`run_idc_21seeds.py` on `photo_pce10`
finishes in about a second total — 21 sub-second seeds.)

Each runner writes under `benchmarks/results/`; the 21-seed summary lands
in `benchmarks/results/branch_a/photo_pce10_summary_21seeds.csv` and the
figures in `benchmarks/figures/`. The broader ~14-problem SO catalog
comparison and the pymoo/pycma baselines from the authors' development
workspace are **not** bundled in this companion; the §8 headline numbers
are reproduced by the C++ worked examples (Step 3), the 21-seed sweep, and
the validation runners above.

### Reproducing problems not shown in the paper

The manuscript shows one BBOB suite and one Olympus task. The runners
expose switches for the rest of the catalog (see
[`../benchmarks/README.md`](../benchmarks/README.md)):

```bash
python bbob/run_bbob_suites.py --suite bbob-mixint   # another COCO suite
python bbob/run_bbob_stress.py --dimensions 5 20 40  # extra dimensions
python run_olympus.py --task snar                    # another Olympus task
```

Each runner prints a `[note]` line when asked for something outside the
paper's reported scope.

---

## Step 5 — One-shot reproduction script

For convenience, every step above is wrapped in:

```bash
./scripts/reproduce_paper.sh
```

This runs: (1) configure + build (fetching the pinned OpenNN), (2) the
three C++ case studies (MOEED13 §8.3, photo_pce10 §8.4, concrete_uci_mo
§8.5), (3) the BBOB analytical validation (§8.2) and the f15–f24 stress
test (§7.3), and (4) the §8.4 Olympus real-data SO sweep. Re-running is
safe: the build is incremental and each example overwrites its own
`result.csv`. The broader multi-seed catalog sweep, the held-out
cross-table, and figure generation are not part of this script.

---

## Verifying the output

If an example folder carries a committed `expected_output.csv` reference,
validate a fresh run against it:

```bash
python scripts/compare_outputs.py examples/<name>/
```

This compares the freshly produced `result.csv` against
`expected_output.csv` element-wise with a tolerance of 1e-5 on inputs
and 1e-3 on outputs, reporting any expected row that has no match. When no
`expected_output.csv` is present the script skips with a notice (nothing
to compare against). To create a reference, save a trusted run's
`result.csv` as `expected_output.csv` in the example folder.

If you used the default `OPENNN_TAG` and the same compiler family,
the outputs should match exactly; minor floating-point drift across
compiler vendors is expected and absorbed by the tolerance.

---

## Troubleshooting

- **FetchContent download fails.** Set `OPENNN_ROOT` to a local
  checkout and skip the download.
- **Linker error against `opennn`.** Confirm you are using the
  pinned tag; older or newer tags may have incompatible APIs.
- **Different headline numbers.** The numbers in the paper are
  reported as mean ± std across 21 seeds; single-seed runs of the
  worked examples will differ slightly. To match the paper exactly,
  run the full sweep via `./scripts/reproduce_paper.sh`.
