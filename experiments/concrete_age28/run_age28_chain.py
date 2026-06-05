"""
run_age28_chain.py — Companion-repo experiment: rerun the concrete MO
holdout chain using surrogates trained ONLY on the age=28 subset of the
UCI Concrete dataset (425 rows, age column constant). Tests whether
removing cross-age training samples eliminates the surrogate-hallucination
signature observed on the age-mixed full-data variant.

Strategy: temporarily swap NN files at the canonical `concrete_uci_mo`
path (where the IDC binary and pymoo runner look) with the age28
surrogates, run IDC + pymoo per surrogate seed, then restore the parent
NN.

Outputs (all under this folder's results/ subdir):
  age28_concrete_uci_mo_{idc,pymoo}_holdout_seed{0..4}.csv (+ _fronts.csv)
  age28_concrete_uci_mo_{idc,pymoo}_full.csv (full-data baseline)
"""
from __future__ import annotations
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Author-workspace only. Committed results/age28_*.csv are the reproducible
# artifacts (holdout_too_small.md); set these env vars to re-run from scratch.
REPO    = Path(os.environ.get("IDC_BENCHMARK", "path/to/IDC_benchmark"))
DATA    = Path(os.environ.get("BENCHMARK_DATASETS", "path/to/benchmark_datasets"))
HERE    = Path(__file__).parent
RESULTS = HERE / "results"
RESULTS.mkdir(exist_ok=True)

# Canonical paths where the IDC binary + pymoo expect the NN.
PARENT_NN_DIR     = DATA / "mo_realdata" / "C_materials_doe" / "concrete_uci_mo" / "nn"
PARENT_NN_JSON    = PARENT_NN_DIR / "concrete_uci_nn.json"
PARENT_NN_BIN     = PARENT_NN_DIR / "concrete_uci_nn.bin"
PARENT_NN_PY      = PARENT_NN_DIR / "concrete_uci_nn.py"

# age28-trained surrogates.
AGE28_NN_DIR      = DATA / "mo_realdata" / "C_materials_doe" / "concrete_uci_age28" / "nn"
AGE28_BASELINE_JSON = AGE28_NN_DIR / "concrete_uci_age28_nn.json"
AGE28_BASELINE_BIN  = AGE28_NN_DIR / "concrete_uci_age28_nn.bin"
AGE28_BASELINE_PY   = AGE28_NN_DIR / "concrete_uci_age28_nn.py"
AGE28_HOLDOUT_DIR  = AGE28_NN_DIR / "top05_holdout"

# Output collection dir (the IDC binary writes here, then we rename + move).
BRANCH_A = REPO / "results" / "branch_a"
PY       = REPO / ".venv" / "Scripts" / "python.exe"
IDC_EXE  = REPO / "build" / "bin" / "Release" / "run_idc_concrete_uci_mo.exe"
PYMOO    = REPO / "branch_a_same_surface" / "python" / "run_pymoo.py"


def install_nn(json_src: Path, bin_src: Path, py_src: Path | None) -> None:
    """Copy the age28 NN trio into the canonical concrete_uci_mo/nn path."""
    shutil.copy2(json_src, PARENT_NN_JSON)
    shutil.copy2(bin_src,  PARENT_NN_BIN)
    if py_src and py_src.exists():
        shutil.copy2(py_src, PARENT_NN_PY)


def backup_parent(tag: str) -> tuple[Path, Path, Path | None]:
    bj = PARENT_NN_JSON.with_suffix(f".json.age28_chain_{tag}_bak")
    bb = PARENT_NN_BIN.with_suffix(f".bin.age28_chain_{tag}_bak")
    bp = PARENT_NN_PY.with_suffix(f".py.age28_chain_{tag}_bak") if PARENT_NN_PY.exists() else None
    if not bj.exists():
        shutil.copy2(PARENT_NN_JSON, bj)
        shutil.copy2(PARENT_NN_BIN, bb)
        if bp:
            shutil.copy2(PARENT_NN_PY, bp)
    return bj, bb, bp


def restore(bj: Path, bb: Path, bp: Path | None) -> None:
    shutil.copy2(bj, PARENT_NN_JSON)
    shutil.copy2(bb, PARENT_NN_BIN)
    if bp and bp.exists():
        shutil.copy2(bp, PARENT_NN_PY)


def move_outputs(suffix: str) -> None:
    for stem in ("concrete_uci_mo_idc",     "concrete_uci_mo_idc_fronts",
                 "concrete_uci_mo_pymoo",   "concrete_uci_mo_pymoo_fronts"):
        src = BRANCH_A / f"{stem}.csv"
        if src.exists():
            dst = RESULTS / f"age28_{stem}_{suffix}.csv"
            shutil.move(str(src), str(dst))
            print(f"  [out] {src.name} -> {dst.name}")


def run_idc_pymoo(label: str) -> None:
    print(f"  [{label}] running IDC ({IDC_EXE.name})")
    rc = subprocess.run([str(IDC_EXE)], capture_output=True, text=True, cwd=str(REPO))
    log = RESULTS / f"_log_idc_{label}.txt"
    log.write_text(rc.stdout + rc.stderr, encoding="utf-8")
    print(f"  [{label}] IDC rc={rc.returncode}")

    env = os.environ.copy()
    # pymoo reads via nn_loader which discovers nn/<problem>_nn.py. With NN
    # files swapped at the canonical path, pymoo will pick up the age28 NN
    # automatically — no OPENNN_NN_OVERRIDE needed for the full-data step.
    # For the holdout step we explicitly override to the seed's .py.
    print(f"  [{label}] running pymoo")
    rc = subprocess.run(
        [str(PY), str(PYMOO),
         "--problem", "concrete_uci_mo", "--algo", "all",
         "--seeds", "21", "--budget", "40000"],
        capture_output=True, text=True, cwd=str(REPO), env=env)
    log = RESULTS / f"_log_pymoo_{label}.txt"
    log.write_text(rc.stdout + rc.stderr, encoding="utf-8")
    print(f"  [{label}] pymoo rc={rc.returncode}")


def main() -> None:
    if not IDC_EXE.exists():
        print(f"[ERROR] {IDC_EXE} missing"); sys.exit(1)
    if not AGE28_BASELINE_JSON.exists():
        print(f"[ERROR] {AGE28_BASELINE_JSON} missing — train age28 baseline first"); sys.exit(1)

    bj, bb, bp = backup_parent("init")
    try:
        # ----- Full-data age28 baseline ------------------------------------
        print("\n=== age28 FULL-DATA baseline ===")
        install_nn(AGE28_BASELINE_JSON, AGE28_BASELINE_BIN,
                   AGE28_BASELINE_PY if AGE28_BASELINE_PY.exists() else None)
        run_idc_pymoo("full")
        move_outputs("full")

        # ----- Holdout chain -----------------------------------------------
        if AGE28_HOLDOUT_DIR.exists():
            for s in range(5):
                seed_dir = AGE28_HOLDOUT_DIR / f"seed_{s}"
                if not (seed_dir / "neural_network.json").exists():
                    print(f"[skip] seed_{s}: no surrogate")
                    continue
                print(f"\n=== age28 holdout seed_{s} ===")
                install_nn(seed_dir / "neural_network.json",
                           seed_dir / "neural_network.bin",
                           seed_dir / "neural_network.py" if (seed_dir / "neural_network.py").exists() else None)
                run_idc_pymoo(f"holdout_seed{s}")
                move_outputs(f"holdout_seed{s}")
        else:
            print(f"[skip] holdout dir {AGE28_HOLDOUT_DIR} missing")
    finally:
        restore(bj, bb, bp)
        print("\n[restore] parent NN restored")


if __name__ == "__main__":
    main()
