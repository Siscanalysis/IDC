# Catalog example — UCI Concrete, single-objective (maximize strength)

**Not a manuscript example.** This is the single-objective view of the
UCI Concrete dataset. The paper's headline UCI Concrete case study is the
**multi-objective** reformulation in §7.5
([`../../concrete_uci_mo/`](../../concrete_uci_mo/)); the single-objective
variant is kept here as part of the broader SO catalog (it is problem
`concrete_uci` in the `benchmarks/` 21-seed sweep).

## Problem

Given a concrete mix (cement, blast-furnace slag, fly ash, water,
superplasticizer, coarse aggregate, fine aggregate, age), find the
combination of ingredient amounts that maximizes 28-day compressive
strength while satisfying physically realizable bounds and the
linear mass-balance constraint per unit volume of mix.

**Input dimension:** 8 (7 continuous ingredients + age in days).
**Output dimension:** 1 (compressive strength in MPa).
**Constraint type:** linear (mass balance per m³ of mix; per-ingredient
bounds derived from the training-data envelope).

## Dataset

UCI Machine Learning Repository: *Concrete Compressive Strength*
(Yeh 1998). 1030 measured concrete mixes covering a wide range of
ingredient ratios.

- Upstream: <https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength>
- In-tree copy: [`../../../data/concrete_uci/concrete_uci.csv`](../../../data/concrete_uci/concrete_uci.csv)
  (shared with the §7.5 MO example).
- Attribution + citation: [`../../../data/concrete_uci/SOURCE.md`](../../../data/concrete_uci/SOURCE.md).
- License: CC-BY 4.0

## Constraints

The same six engineering constraints as the §7.5 MO sibling (single
objective here — maximize strength), defined in
[`constraints.yaml`](constraints.yaml).

## Surrogate

A feed-forward neural network selected by the OpenNN Growing Neurons
procedure; the trained model JSON lives at `nn/concrete_uci.json`.

## Expected output

`result.csv` contains the IDC-recommended input vector and predicted
strength. Because this is a catalog example, the headline number is
reported only in the companion repository's `benchmarks/` sweep, not in a
paper table.

To reproduce:

```bash
cd build
cmake --build . --target concrete_uci_so
./bin/concrete_uci_so
```
