# Sec. 4 — yacht (bi-objective hull design)

At a **fixed cruising speed** (Froude = 0.2875, the dataset mean) trade off two
conflicting objectives:

- **minimize residuary resistance** (the NN output) — less drag, lower fuel use;
- **minimize the length/beam ratio L/B** (the `length_beam` input) — i.e.
  **maximize the beam**: a wider hull is roomier and more stable.

A wider hull (lower L/B) gains stability and interior volume but increases drag,
so the objectives genuinely conflict (on the surrogate, L/B and resistance
correlate ≈ −0.61) and IDC traces a dense Pareto front. The four remaining hull
coefficients are free within the Delft envelope; the L/B objective is a
passthrough on its input variable (no extra surrogate call).

**Surrogate:** `nn/yacht.json` — OpenNN `ApproximationNetwork`, 6→4→1,
R²≈0.995 (full) / 0.99 (test) — a compact Growing-Neurons network. Inputs (in
order): `long_pos_cob, prismatic_coef, length_displacement, beam_draught,
length_beam, froude`; output `resistance`.

**Data:** `data/yacht.csv` — 308 rows, header. Source: Delft Systematic Yacht
Hull Series; Ortigosa, López & García (2007); UCI ML Repository id 243.

## Run

```bash
./build/bin/sci2026_yacht_mo              # writes result.csv (the Pareto front)
python scripts/compare_outputs.py yacht_mo/
```

`result.csv` columns: `resistance,length_beam,x_long_pos_cob,…,x_froude` — one
row per non-dominated hull (the two objectives, then the full input vector).

With the compact 4-neuron surrogate, a single IDC run (seed 0) returns a dense
front of ~1200 non-dominated hulls spanning the full beam range (L/B ∈ [2.73,
3.64]) against residuary resistance ∈ [0.27, 1.91], with a clear knee around
L/B ≈ 3.06, resistance ≈ 1.4 — the recommended hull. The paper additionally
reports a normalized-hypervolume summary computed over a best-of-21-seeds front
(a separate aggregation step); the front shape and knee reproduce here from this
single deterministic seed.

Configuration (in `main.cpp` / `problem.yaml`): 40 000 surrogate evaluations
(2000 candidates × 20 iterations), zoom 0.85, relative tolerance 1e-6, seed 0.
