# Constraints — COCO `bbob-biobj-mixint` (§7.2)

The §7.2 analytical validation has no dataset and no user-defined formula
constraints; its feasible set is defined entirely by the COCO suite. Two
structural constraints apply to every problem in the suite.

## 1. Box bounds

Every coordinate is bounded:

```
x_i ∈ [-5, 5],   i = 1 … n
```

where `n ∈ {5, 10, 20, 40, 80, 160}` is the dimension cohort
(§7.2 setup). IDC's initial domain is exactly this box.

## 2. Integrality of the integer block

The suite splits each vector into a continuous block and an integer block,

```
x = (u, v),   u ∈ ℝ^{n_c}  (continuous),   v ∈ ℤ^{n_d}  (integer),
```

with `n_d / (n_c + n_d) ≈ 0.2` in the suite default (about one coordinate
in five is integer-valued). The integer coordinates are additionally
restricted to a per-coordinate finite range fixed by the COCO instance.

IDC handles the integer block by categorical/integer block elimination
(§3 of the paper); pymoo handles it through its mixed-variable operators.

## Worked cell (paper §7.2)

The representative cell formalized in the paper is the bi-objective pair
built from BBOB SO function f18 (Schaffer's F7, ill-conditioned, condition
number 10³) — see `run_bbob_stress.py::f18_schaffer_f7_illcond` for the
scalar building block. The bi-objective pair stacks two such functions
with different shifts/rotations, as defined by the COCO `bbob-biobj-mixint`
construction.

## Other suites

The other four COCO suites reachable via `run_bbob_suites.py --suite ...`
differ in their structural constraints:

| Suite | Box bounds | Integrality | Explicit constraints |
|-------|-----------|-------------|----------------------|
| `bbob` | yes | none | none |
| `bbob-mixint` | yes | integer block | none |
| `bbob-constrained` | yes | none | explicit inequality constraints (COCO-defined) |
| `bbob-biobj` | yes | none | none |
| `bbob-biobj-mixint` | yes | integer block | none |

These are reported only in the companion repository; §7.2 shows
`bbob-biobj-mixint`.
