# IDC — Iterative Domain Contraction for Neural-Network Response Optimization

This repository is the public companion to the paper
**"Neural network response optimization via iterative domain contraction"**
(Scala, Lopez, Assumpção, Dewil — under review at *Advances in Computational Science and Engineering* / AIMS).

It contains the worked examples reported in §8 of the paper, the benchmark
suite, the held-out validation protocol, and a reproduction recipe — all
built on top of the open-source library
[OpenNN](https://github.com/Artelnics/opennn).

> **Status.** Scaffold. Worked-example implementations land once the paper
> is accepted; the OpenNN tag pinned for byte-reproducibility is set then.

---

## About OpenNN

OpenNN ([Artelnics/opennn](https://github.com/Artelnics/opennn)) is an
open-source neural-networks C++ library released under LGPL v3.
IDC is implemented as the `ResponseOptimization` class inside OpenNN; this
companion repository ships **worked examples and reproduction tooling**
around that core, version-pinned to a specific OpenNN release so the
paper's numbers are byte-reproducible.

If you want to use IDC inside your own project, depend on OpenNN directly.
This repo is the paper-reproduction layer.

---

## Quick start

```bash
git clone https://github.com/Siscanalysis/IDC.git
cd IDC
mkdir build && cd build
cmake ..        # downloads + builds the pinned OpenNN release
cmake --build . --config Release
./bin/photo_pce10   # runs the §8.4 real-application SO case study
```

Expected output: a `result.csv` containing the IDC-recommended input
configuration and corresponding surrogate output, matching the headline
number in the §8.4 table of the paper.

---

## Reproducing the paper

```bash
./scripts/reproduce_paper.sh   # runs all §8 examples end-to-end
```

Expected runtime on commodity hardware (i7 8-core, no GPU): ~[TBD] minutes.
The script regenerates every results CSV, every plot, and the holdout
validation cross-table.

---

## Worked examples

The paper's §8 reports four headline case studies, split into a
**validation** block and a **real-applications** block. The two C++
neural-network case studies are under `examples/`; the analytical BBOB
validation is driven from `benchmarks/bbob/`:

| §   | Example                          | Block            | Type           | Location |
|-----|----------------------------------|------------------|----------------|----------|
| 8.2 | BBOB bi-objective mixed-integer  | Validation       | Analytical MO  | [`benchmarks/bbob/`](benchmarks/bbob/) |
| 8.3 | MOEED13 economic-emission dispatch | Validation     | Simulator MO   | [`examples/moeed13/`](examples/moeed13/) |
| 8.4 | photo_pce10 (Olympus OPV)        | Real application | Real SO        | [`examples/photo_pce10/`](examples/photo_pce10/) |
| 8.5 | concrete_uci_mo (UCI Concrete)   | Real application | Real MO        | [`examples/concrete_uci_mo/`](examples/concrete_uci_mo/) |

The broader catalog (~30 additional benchmark problems §8.1 refers to —
other BBOB suites, other Olympus tasks, classical engineering, chemistry
HTE) is reproduced from [`benchmarks/`](benchmarks/), plus two extra
real-data examples under
[`examples/additional/`](examples/additional/) that are **not** shown in
the manuscript.

---

## Benchmark suite

`benchmarks/` contains the 21-seed sweep and the catalog runners used in
the paper:

- `run_idc_21seeds.py` — drives IDC on all catalog problems
- `run_olympus.py` — Olympus real-data runner; `--task` selects the task
  (default `photo_pce10`; other tasks are *not* shown in the paper)
- `bbob/run_bbob_suites.py` — COCO suite driver; `--suite` selects the
  suite (default `bbob-biobj-mixint`, the only one shown explicitly)
- `bbob/run_bbob_stress.py` — the f15–f24 hard-multimodal stress test
  (§7.3 limitations) at *n*=5 and *n*=20
- `aggregate_21seeds.py` — per-problem and combined summaries
- `make_figures.py` — regenerates the figures in the paper

See [`benchmarks/README.md`](benchmarks/README.md) for the switch
reference and details.

---

## Repository structure

```
IDC/
├── README.md                    ← this file
├── LICENSE                      ← LGPL v3, matching OpenNN
├── CITATION.cff                 ← paper citation metadata
├── CMakeLists.txt               ← C++ build entry point
├── cmake/
│   └── FindOrFetchOpenNN.cmake  ← three-tier OpenNN resolution
├── examples/                    ← C++ NN case studies (§8.3–§8.5) + additional/
├── benchmarks/                  ← BBOB (§8.2) + catalog sweep + figures + switches
├── scripts/                     ← reproduction orchestrators
├── data/                        ← curated dataset subset
└── docs/
    ├── architecture.md          ← IDC overview + how OpenNN is used
    ├── reproducing.md           ← exact reproduction recipe
    └── holdout_procedure.md     ← held-out validation protocol
```

---

## Citation

```bibtex
@article{Scala2026IDC,
  author  = {Scala, Simone and Lopez, Roberto and Assump\c{c}\~ao, Jos\'e Matias and Dewil, Raf},
  title   = {Neural network response optimization via iterative domain contraction},
  journal = {Advances in Computational Science and Engineering},
  year    = {2026},
  note    = {Under review}
}
```

(Update once the paper is accepted.)

---

## License

Released under the GNU Lesser General Public License v3.0
(LGPL-3.0-or-later) — matching OpenNN.

See [LICENSE](LICENSE) for the full text.

---

## Acknowledgments

Funded by the European Union (Marie Skłodowska-Curie Grant Agreement
no. 101169541 — **NEUTEN**). Views and opinions expressed are however
those of the author(s) only and do not necessarily reflect those of the
European Union or the European Research Executive Agency (REA). Neither
the European Union nor the granting authority can be held responsible for
them.
