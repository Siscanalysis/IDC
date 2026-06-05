"""
run_age28_full_data.py — Companion experiment v2.
Now that the age=28 baseline NN is actually trained (425 rows, age=28 only),
this script:
  1. Exports the age28 baseline to .py via export_nn_py.exe.
  2. Swaps the age28 NN trio (.json, .bin, .py) into the canonical
     concrete_uci_mo/nn/ path that the IDC binary and pymoo runner read.
  3. Runs IDC (21 seeds × 40k budget) + pymoo (NSGA-II / NSGA-III, 21 seeds
     × 40k budget) against the age=28 surrogate.
  4. Restores the parent NN.

Output goes to results/age28_fulldata_{idc,pymoo}.csv (+ _fronts.csv).
"""
from __future__ import annotations
import os, shutil, subprocess
from pathlib import Path

# Author-workspace only. Committed results/age28_*.csv are the reproducible
# artifacts; set these env vars to re-run from scratch.
REPO  = Path(os.environ.get("IDC_BENCHMARK", "path/to/IDC_benchmark"))
DATA  = Path(os.environ.get("BENCHMARK_DATASETS", "path/to/benchmark_datasets"))
HERE  = Path(__file__).parent
OUT   = HERE / "results"
OUT.mkdir(exist_ok=True)

EXPORT  = REPO / "build" / "bin" / "Release" / "export_nn_py.exe"
IDC_EXE = REPO / "build" / "bin" / "Release" / "run_idc_concrete_uci_mo.exe"
PY      = REPO / ".venv" / "Scripts" / "python.exe"
PYMOO   = REPO / "branch_a_same_surface" / "python" / "run_pymoo.py"
BRANCH_A = REPO / "results" / "branch_a"

PARENT_NN_DIR  = DATA / "mo_realdata" / "C_materials_doe" / "concrete_uci_mo" / "nn"
PARENT_NN_JSON = PARENT_NN_DIR / "concrete_uci_nn.json"
PARENT_NN_BIN  = PARENT_NN_DIR / "concrete_uci_nn.bin"
PARENT_NN_PY   = PARENT_NN_DIR / "concrete_uci_nn.py"

AGE28_NN_DIR   = DATA / "mo_realdata" / "C_materials_doe" / "concrete_uci_age28" / "nn"
AGE28_JSON     = AGE28_NN_DIR / "concrete_uci_age28_nn.json"
AGE28_BIN      = AGE28_NN_DIR / "concrete_uci_age28_nn.bin"
AGE28_PY       = AGE28_NN_DIR / "concrete_uci_age28_nn.py"


def export_age28_py() -> None:
    """export_nn_py <json_path> <py_out> <inputs_count> <hidden_csv> <targets_count>
    Architecture mirrors parent: 8 inputs → 52 hidden → 1 target."""
    if AGE28_PY.exists() and AGE28_PY.stat().st_mtime > AGE28_JSON.stat().st_mtime:
        print("[export] .py already up to date"); return
    cmd = [str(EXPORT), str(AGE28_JSON), str(AGE28_PY), "8", "52", "1"]
    print(f"[export] {' '.join(cmd)}")
    rc = subprocess.run(cmd, capture_output=True, text=True)
    (OUT / "_log_export_py.txt").write_text(rc.stdout + rc.stderr, encoding="utf-8")
    if rc.returncode != 0:
        raise RuntimeError(f"export_nn_py failed: rc={rc.returncode}")
    if not AGE28_PY.exists():
        raise RuntimeError("export_nn_py succeeded but .py not produced")
    print(f"[export] wrote {AGE28_PY}")


def backup_parent() -> tuple[Path, Path, Path | None]:
    bj = PARENT_NN_JSON.with_suffix(".json.age28_fulldata_bak")
    bb = PARENT_NN_BIN.with_suffix(".bin.age28_fulldata_bak")
    bp = PARENT_NN_PY.with_suffix(".py.age28_fulldata_bak") if PARENT_NN_PY.exists() else None
    if not bj.exists():
        shutil.copy2(PARENT_NN_JSON, bj)
        shutil.copy2(PARENT_NN_BIN, bb)
        if bp:
            shutil.copy2(PARENT_NN_PY, bp)
    return bj, bb, bp


def install_age28() -> None:
    shutil.copy2(AGE28_JSON, PARENT_NN_JSON)
    shutil.copy2(AGE28_BIN, PARENT_NN_BIN)
    shutil.copy2(AGE28_PY, PARENT_NN_PY)
    print("[swap] age28 NN installed at canonical path")


def restore(bj: Path, bb: Path, bp: Path | None) -> None:
    shutil.copy2(bj, PARENT_NN_JSON)
    shutil.copy2(bb, PARENT_NN_BIN)
    if bp and bp.exists():
        shutil.copy2(bp, PARENT_NN_PY)
    print("[restore] parent NN restored")


def move_outputs() -> None:
    for stem in ("concrete_uci_mo_idc",   "concrete_uci_mo_idc_fronts",
                 "concrete_uci_mo_pymoo", "concrete_uci_mo_pymoo_fronts"):
        src = BRANCH_A / f"{stem}.csv"
        if src.exists():
            dst = OUT / f"age28_fulldata_{stem.replace('concrete_uci_mo_','')}.csv"
            shutil.move(str(src), str(dst))
            print(f"[out] {src.name} -> {dst.name}")


def run_idc() -> None:
    print("[idc] running")
    rc = subprocess.run([str(IDC_EXE)], capture_output=True, text=True, cwd=str(REPO))
    (OUT / "_log_idc.txt").write_text(rc.stdout + rc.stderr, encoding="utf-8")
    print(f"[idc] rc={rc.returncode}")


def run_pymoo() -> None:
    print("[pymoo] running")
    rc = subprocess.run(
        [str(PY), str(PYMOO),
         "--problem", "concrete_uci_mo", "--algo", "all",
         "--seeds", "21", "--budget", "40000"],
        capture_output=True, text=True, cwd=str(REPO))
    (OUT / "_log_pymoo.txt").write_text(rc.stdout + rc.stderr, encoding="utf-8")
    print(f"[pymoo] rc={rc.returncode}")


def main() -> None:
    export_age28_py()
    bj, bb, bp = backup_parent()
    try:
        install_age28()
        run_idc()
        run_pymoo()
        move_outputs()
    finally:
        restore(bj, bb, bp)


if __name__ == "__main__":
    main()
