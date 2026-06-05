# Worked examples

The paper's §7 numerical study is organized into a **validation** block
and a **real-applications** block. The runnable artifacts are split the
same way: the two C++ neural-network case studies live here under
`examples/`; the analytical BBOB validation lives under
[`../benchmarks/bbob/`](../benchmarks/bbob/).

## In-paper examples (§7)

| § | Example | Block | Type | Constraint | Location | Status |
|---|---------|-------|------|------------|----------|--------|
| 8.2 | BBOB bi-objective mixed-integer | Validation | Analytical MO | mixed-integer | [`../benchmarks/bbob/`](../benchmarks/bbob/) | Python runner |
| 8.3 | MOEED13 economic-emission dispatch | Validation | Simulator MO | linear equality (power balance, ±0.5 MW band) | [`moeed13/`](moeed13/) | buildable C++ |
| 8.4 | photo_pce10 (OPV) | Real application | Real SO | simplex equality (+ donor band) | [`photo_pce10/`](photo_pce10/) | buildable C++ |
| 8.5 | concrete_uci_mo (UCI Concrete) | Real application | Real MO | 6 affine inequalities | [`concrete_uci_mo/`](concrete_uci_mo/) | buildable C++ |

- **Validation block** (§7.2 BBOB, §7.3 MOEED13): the objective surface
  is exact (analytical functions or a closed-form simulator), so there is
  no surrogate quality to confound the optimizer comparison.
- **Real-applications block** (§7.4 photo_pce10, §7.5 concrete_uci_mo):
  IDC is exposed to a fitted neural-network surrogate. The SO case
  (photo_pce10) is reported under the top-5% held-out protocol; the MO
  case (concrete_uci_mo) instead uses an age-28 surrogate restriction,
  since the age-28 slice is too small for a further 5% removal. Both
  guard against surrogate memorization — see
  [`../docs/holdout_procedure.md`](../docs/holdout_procedure.md).

## Additional catalog examples (not in the manuscript)

`additional/` holds examples that are part of the broader ~30-problem
catalog §7.1 points to, but are not among the four headline §7 case
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
├── problem.yaml          ← inputs, objectives + the `constraints:` block the C++ driver loads
├── constraints.yaml      ← stand-alone constraint mirror (reference; not read by the C++ driver)
├── main.cpp              ← entry point: load NN, load problem.yaml, run IDC
├── CMakeLists.txt        ← target definition, links against opennn
├── nn/
│   └── <example>.json    ← trained surrogate (Growing Neurons selection)
└── expected_output.csv   ← reference output for the smoke test
```

The dataset for each example lives under the top-level
[`../data/<example>/`](../data/) (shipped in-tree where small, with a
`SOURCE.md` citation). The C++ driver loads `problem.yaml` and applies
its top-level `constraints:` block (via
[`common/yaml_constraints.h`](common/yaml_constraints.h)); that
constraint set matches the constraints reported in the paper for that
example.

The top-level `CMakeLists.txt` adds each C++ example via
`add_subdirectory(...)`. The OpenNN tag pinned for byte-reproducibility
is finalized once the paper is accepted.
