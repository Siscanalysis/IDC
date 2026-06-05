# SCI 2026 — worked examples

This branch is the reproduction companion for the conference paper

> **Diseño industrial óptimo con redes neuronales** (Optimal industrial design
> with neural networks). Scala, S., López, R. (2026). *XXI Simposio CEA de
> Control Inteligente* (SCI 2026), Salamanca.

It contains **only** the two case studies reported in that paper, each built on
the `ResponseOptimization` (Iterative Domain Contraction, IDC) class of the
open-source library [OpenNN](https://github.com/Artelnics/opennn):

| Sec. | Example | Type | Problem |
|------|---------|------|---------|
| 3 | [`photo_wf3_so/`](photo_wf3_so/) | Single-objective | Minimize photodegradation of a quaternary OPV blend on the 3-simplex, under a functional donor:acceptor window (Olympus `photo_wf3`). |
| 4 | [`yacht_mo/`](yacht_mo/) | Multi-objective | Trade off residuary resistance vs. hull beam (minimize L/B) at fixed Froude (Delft Yacht Hydrodynamics). |

> **Relationship to the other paper.** This is the **`sci2026` branch** — a
> standalone tree for the SCI 2026 conference paper, with its own root. The
> separate *journal*-paper companion ("Neural network response optimization via
> iterative domain contraction") lives on the **`main` branch** (frozen at tag
> `v1.0-aims-paper`). The two share no files and no history — only the same
> repository and the same pinned OpenNN release.

## Build

```bash
cmake -B build               # downloads + builds the pinned OpenNN (v1.2-IDC-paper)
cmake --build build --config Release
```

Binaries are written to `build/bin/`. To build against a local OpenNN checkout
instead of downloading, pass `-DOPENNN_ROOT=/path/to/opennn`; to pin a different
OpenNN ref, pass `-DOPENNN_TAG=<tag>` (see [`cmake/FindOrFetchOpenNN.cmake`](cmake/FindOrFetchOpenNN.cmake)).

## Run

```bash
./build/bin/sci2026_photo_wf3_so    # writes photo_wf3_so/result.csv
./build/bin/sci2026_yacht_mo        # writes yacht_mo/result.csv
```

Each example writes a `result.csv` next to its sources. A committed
`expected_output.csv` records the reference result; verify a fresh run with the
bundled smoke-test:

```bash
python scripts/compare_outputs.py photo_wf3_so/
python scripts/compare_outputs.py yacht_mo/
```

IDC is stochastic and OpenNN's sampling/repair draw from non-portable `std::`
distributions, so a clean clone on a different compiler reaches the same
objective value / Pareto-front extent but a different feasible argmin; the
smoke-test asserts the reproducible quantities within a 5% tolerance.

## Layout

```
. (sci2026 branch root)
├── README.md
├── CMakeLists.txt              ← standalone build entry point
├── cmake/
│   └── FindOrFetchOpenNN.cmake ← OpenNN resolver, pinned to v1.2-IDC-paper
├── common/
│   └── yaml_constraints.h      ← YAML→ResponseOptimization constraint helper
├── scripts/
│   └── compare_outputs.py      ← reproduce-check (objective / front-extent, 5% tol)
├── photo_wf3_so/               ← Sec. 3 (SO): main.cpp, problem.yaml, nn/, data/
└── yacht_mo/                   ← Sec. 4 (MO): main.cpp, problem.yaml, nn/, data/
```

## Data and surrogates

Each example ships its trained OpenNN surrogate (`nn/*.json` + `.bin` weights)
and the source dataset (`data/*.csv`). Provenance and citations are in each
example's `problem.yaml` and `README.md`. The surrogates are the compact networks
reported in the paper (photo: 8 neurons, R²≈0.77; yacht: 4 neurons, R²≈0.995).

## License / funding

Released under LGPL-3.0-or-later, matching OpenNN. Funded by the European Union
(Marie Skłodowska-Curie Grant Agreement no. 101169541 — NEUTEN). Views and
opinions expressed are those of the authors only and do not necessarily reflect
those of the European Union or the granting authority.
