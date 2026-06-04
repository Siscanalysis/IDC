# Worked examples

The paper's §8 numerical study is organized into a **validation** block
and a **real-applications** block. The runnable artifacts are split the
same way: the two C++ neural-network case studies live here under
`examples/`; the analytical BBOB validation lives under
[`../benchmarks/bbob/`](../benchmarks/bbob/).

## In-paper examples (§8)

| § | Example | Block | Type | Constraint | Location | Status |
|---|---------|-------|------|------------|----------|--------|
| 8.2 | BBOB bi-objective mixed-integer | Validation | Analytical MO | mixed-integer | [`../benchmarks/bbob/`](../benchmarks/bbob/) | [scaffold] |
| 8.3 | MOEED13 economic-emission dispatch | Validation | Simulator MO | linear equality (power balance) | [`moeed13/`](moeed13/) | [scaffold] |
| 8.4 | photo_pce10 (OPV) | Real application | Real SO | simplex (ratio) | [`photo_pce10/`](photo_pce10/) | [scaffold] |
| 8.5 | concrete_uci_mo (UCI Concrete) | Real application | Real MO | linear mass-balance | [`concrete_uci_mo/`](concrete_uci_mo/) | [scaffold] |

- **Validation block** (§8.2 BBOB, §8.3 MOEED13): the objective surface
  is exact (analytical functions or a closed-form simulator), so there is
  no surrogate quality to confound the optimizer comparison.
- **Real-applications block** (§8.4 photo_pce10, §8.5 concrete_uci_mo):
  IDC is exposed to a fitted neural-network surrogate and reported under
  the top-5% held-out protocol of
  [`../docs/holdout_procedure.md`](../docs/holdout_procedure.md).

## Additional catalog examples (not in the manuscript)

`additional/` holds examples that are part of the broader ~30-problem
catalog §8.1 points to, but are not among the four headline §8 case
studies — see [`additional/README.md`](additional/README.md):

| Folder | Type | Constraint |
|--------|------|------------|
| `additional/concrete_uci_so/` | Real SO | linear mass-balance |
| `additional/oer_plates/`      | Real MO | 6-simplex equality |

Other catalog problems (other Olympus tasks, other BBOB suites) are not
shipped as standalone folders; they are reachable through the `--task` /
`--suite` switches of the `benchmarks/` runner scripts.

## Per-example folder layout

Each C++ example folder is independently buildable once populated:

```
<example>/
├── README.md             ← problem description, constraints, expected output
├── constraints.yaml      ← variable bounds + formula constraints (the file IDC loads)
├── main.cpp              ← entry point: load NN, load constraints.yaml, run IDC
├── CMakeLists.txt        ← target definition, links against opennn
├── nn/
│   └── <example>.json    ← trained surrogate (Growing Neurons selection)
└── expected_output.csv   ← reference output for the smoke test
```

The dataset for each example lives under the top-level
[`../data/<example>/`](../data/) (shipped in-tree where small, with a
`SOURCE.md` citation). The `constraints.yaml` matches the constraints
reported in the paper for that example.

The top-level `CMakeLists.txt` adds each C++ example via
`add_subdirectory(...)` once its folder is populated — see the
commented-out lines there. The implementations are deferred until §8 of
the paper has been finalized with the post-refactor numbers.
