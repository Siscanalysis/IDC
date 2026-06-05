# Sec. 3 — photo_wf3 (single-objective OPV photostability)

Minimize the measured photodegradation of a four-component organic-photovoltaic
(OPV) blend, where the decision variables are the four mass fractions
`mat_1..mat_4` and the surrogate predicts the normalized post-ageing
degradation (lower is better).

**Constraints (both affine on the inputs, repaired in one pass by IDC):**
- **Simplex:** `mat_1 + mat_2 + mat_3 + mat_4 = 1` (mass fractions sum to one).
- **Donor:acceptor window:** `0.4 ≤ mat_1 + mat_2 ≤ 0.6` — the total donor
  fraction (WF3 + P3HT). Minimizing degradation alone degenerates to a
  donor-free blend (not a working cell); this window keeps the optimum a
  realistic, percolating bulk-heterojunction (donor:acceptor ≈ 2:3 … 3:2).

Components: `mat_1`=WF3 (PBQ-QF wide-bandgap donor), `mat_2`=P3HT (donor),
`mat_3`=PCBM (fullerene acceptor), `mat_4`=oIDTBR (non-fullerene acceptor).

**Surrogate:** `nn/photo_wf3.json` — OpenNN `ApproximationNetwork`, 4→8→1,
R²≈0.78 (full) / 0.80 (test) over the 1040-mixture Olympus campaign.

**Data:** `data/photo_wf3.csv` — 1040 rows, no header; columns
`mat_1,mat_2,mat_3,mat_4,degradation`. Source: Olympus `photo_wf3` (Häse et al.
2021); blend campaign Langner et al. 2020.

## Run

```bash
./build/bin/sci2026_photo_wf3_so          # writes result.csv
python scripts/compare_outputs.py photo_wf3_so/
```

`result.csv` columns: `mat_1,mat_2,mat_3,mat_4,degradation` (the recommended
blend and its predicted degradation). With the compact 8-neuron surrogate, IDC
returns a feasible heterojunction inside the donor:acceptor window — total donor
(WF3 + P3HT) ≈ 0.60, acceptor ≈ 0.40 (D:A ≈ 3:2), photodegradation ≈ 0.067,
100% feasible — a realistic, usable blend rather than the degenerate donor-free
optimum that minimizing degradation alone would pick.

Configuration (in `main.cpp` / `problem.yaml`): 40 000 surrogate evaluations
(2000 candidates × 20 iterations), zoom 0.85, relative tolerance 1e-6, seed 0.
