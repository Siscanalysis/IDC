#!/usr/bin/env python3
"""
audit_surrogates.py — surrogate-quality audit (paper §7.5).

Renders the per-entry surrogate test-R^2 table behind the 'surrogate-side'
check in §7.5: a real-data headline must rest on a surrogate that actually
fits, so an IDC 'win' on a poorly-fit surrogate is treated as an artifact of
surrogate quality, not optimizer skill. Reads the committed
`extra_results/surrogate_audit.csv` (the R^2 values reported in the paper) and
prints the audit table, flagging each entry against the R^2 >= 0.70 good-fit
bar.

    python audit_surrogates.py

Self-contained: standard library only.
"""
from __future__ import annotations

import csv
from pathlib import Path

HERE = Path(__file__).parent
AUDIT = HERE / "extra_results" / "surrogate_audit.csv"
GOOD_FIT = 0.70


def main() -> int:
    if not AUDIT.exists():
        print(f"[FAIL] {AUDIT} missing")
        return 1
    rows = list(csv.DictReader(open(AUDIT, newline="")))
    w = max(len(r["entry"]) for r in rows) + 2
    print(f"{'entry':<{w}} {'§':>4} {'type':<10} {'target':<12} "
          f"{'test R^2':>9} {'status':<10} fit")
    print("-" * (w + 62))
    for r in rows:
        r2 = r["test_r2"].strip()
        if r2 == "":
            r2disp, fit = "  --  ", "n/a (analytical)"
        else:
            val = float(r2)
            r2disp = f"{val:.4f}"
            fit = "OK" if val >= GOOD_FIT else "BELOW BAR"
        print(f"{r['entry']:<{w}} {r['section']:>4} {r['type']:<10} "
              f"{r['surrogate_target']:<12} {r2disp:>9} {r['status']:<10} {fit}")
    print()
    print(f"Good-fit bar: test R^2 >= {GOOD_FIT}. Entries below it are not reported")
    print("as real-data headlines (e.g. the Jacobsson-2021 perovskite surrogate,")
    print("R^2 ~ 0.07, was discarded). UCI Concrete (R^2 ~ 0.79 on the age-28 slice)")
    print("is reported but calibrated against the measured data ceiling rather than")
    print("the held-out protocol.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
