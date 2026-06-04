# Additional worked examples (broader catalog — not in the manuscript)

These examples are **not** part of the four §8 case studies shown in the
paper. They belong to the broader catalog of ~30 benchmark problems that
§8.1 of the manuscript refers to as

> "a broader catalog of ~30 additional benchmark problems (BBOB
> analytical suites, Olympus real-data tasks, classical engineering, and
> chemistry HTE entries) ... reported in the public companion repository."

They are kept here because they are useful, self-contained demonstrations
of IDC on real datasets with linear / simplex constraints, and because
they share the same build and run recipe as the headline examples. They
were headline examples in an earlier manuscript draft; the final §8 was
restructured around a validation block (BBOB bi-objective mixed-integer +
MOEED13) and a real-applications block (photo_pce10 + concrete_uci_mo),
so these two moved into the catalog.

| Folder              | Type      | Constraint        | Why it is here |
|---------------------|-----------|-------------------|----------------|
| `concrete_uci_so/`  | Real SO   | Linear mass-balance | Single-objective view of the UCI Concrete dataset used by §8.5; part of the broader SO sweep (`benchmarks/`, problem `concrete_uci`). |
| `oer_plates/`       | Real MO   | 6-simplex equality  | High-throughput OER-catalyst screen; an extra affine-repair showcase on a strict simplex. |

For the manuscript examples see [`../README.md`](../README.md). For the
full broader-catalog sweep (other Olympus tasks, other BBOB suites) see
[`../../benchmarks/README.md`](../../benchmarks/README.md), where the
runner scripts expose `--task` / `--suite` switches to select problems
that are not shown explicitly in the paper.
