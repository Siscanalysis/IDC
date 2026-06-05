# Architecture

This document gives a high-level view of how IDC is structured and how
this paper companion sits on top of [OpenNN](https://github.com/Artelnics/opennn).

For the rigorous mathematical formulation, refer to §2–§7 of the paper.

---

## Where IDC lives

IDC is **not** a separate library. It is implemented as the
`opennn::ResponseOptimization` class inside OpenNN
(`opennn/opennn/response_optimization.{h,cpp}`).

```
opennn/                                ← Artelnics/opennn on GitHub
├── opennn/
│   ├── neural_network.{h,cpp}         ← trained surrogate
│   ├── response_optimization.{h,cpp}  ← IDC implementation (SO + MO)
│   ├── bounding_layer.{h,cpp}         ← search-domain bounds
│   └── …                              ← rest of OpenNN
└── …

IDC_paper_companion/                   ← this repository
├── examples/                          ← worked examples (§7)
├── benchmarks/                        ← 21-seed sweep
└── …
```

The companion repository links against OpenNN as a build-time dependency
(see [`cmake/FindOrFetchOpenNN.cmake`](../cmake/FindOrFetchOpenNN.cmake))
and ships only the paper-reproduction layer: worked examples, datasets,
benchmark scripts, and figure generation.

---

## The IDC pipeline (one iteration)

The single- and multi-objective variants share a common inner loop. Both
operate on a hyperrectangular search domain $\mathcal{D}_x^{(t)}$ and
contract it iteratively.

```
            ┌──────────────────────────────────┐
            │  initial domain D_x^{(0)}        │
            │  trained surrogate f             │
            │  variable conditions             │
            └────────────────┬─────────────────┘
                             ▼
        ┌──────────────────────────────────────────────┐
        │  for t = 1, …, I_max:                        │
        │                                              │
        │    [Sampling]      uniform random in D_x^{(t)}│
        │       │                                      │
        │       ▼                                      │
        │    [Repair]        affine repair op (linear) │
        │       │            rejection (other)         │
        │       ▼                                      │
        │    [Feasibility]   filter by all conditions  │
        │       │                                      │
        │       ▼                                      │
        │    [Selection]     SO: nearest to utopian    │
        │                    MO: Pareto + local refine │
        │       │                                      │
        │       ▼                                      │
        │    [Reshape]       contract around best(s)   │
        │       │                                      │
        │       ▼                                      │
        │    [Termination]   if stable enough → stop   │
        │                                              │
        └──────────────────────────────────────────────┘
                             ▼
                  best (SO) / Pareto front (MO)
```

Each box in the diagram corresponds to a section of the paper:

| Box           | Section in the paper                          |
|---------------|-----------------------------------------------|
| Sampling      | §4.2 Random sampling                          |
| Repair        | §4.4 Affine repair operator                   |
| Feasibility   | §4.3 Feasibility filtering                    |
| Selection (SO)| §4.7 Objective normalization and selection    |
| Selection (MO)| §6 Multi-objective optimization               |
| Reshape       | §4.8 Domain reshaping                         |
| Termination   | §5.2 (SO), §6.3 (MO)                          |

---

## How the worked examples use IDC

Each `examples/<name>/main.cpp` follows the same scaffolded recipe:

1. **Load the trained NN.** A pre-trained OpenNN JSON model checked into the
   repo at `examples/<name>/nn/<name>.json` (the architecture comes from a
   Growing Neurons selection sweep upstream).
2. **Declare the variable conditions and constraints.** Bounds, formula
   constraints, and objectives are specified through the OpenNN
   `ResponseOptimization` API.
3. **Run IDC.** Either `perform_optimization()` (SO) or
   `perform_multi_objective_optimization()` (MO).
4. **Write the result CSV.** Recorded inputs + outputs, with the
   IDC-recommended configuration (SO) or the Pareto front (MO).

The output CSV matches the headline number in the corresponding paper table.

---

## Where the datasets come from

`data/` is a curated subset of the `benchmark_datasets` workspace used
by the authors during development (kept in the authors' working tree,
not redistributed here). Each example folder either:

- includes the curated dataset directly (small enough — UCI Concrete,
  the MOEED13 coefficient tables), or
- includes a download script (`fetch_data.sh`) that pulls from the
  upstream source (Olympus tasks, larger datasets).

The §7.2 BBOB analytical validation needs no dataset — it is evaluated
directly from the COCO / canonical analytical functions in
`benchmarks/bbob/`.

---

## Reproducing the paper

See [reproducing.md](reproducing.md) for the exact end-to-end recipe.
