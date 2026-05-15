"""比对 PyG QM9 条数与 raw SDF + uncharacterized 跳过规则后的 RDKit 可读条数。"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_SRC = _REPO / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from qm9_raw_utils import load_qm9_skip_sdf_indices  # noqa: E402
from rdkit import Chem, RDLogger  # noqa: E402
from torch_geometric.datasets import QM9  # noqa: E402


def main() -> None:
    raw = _REPO / "data" / "qm9" / "raw"
    sdf = raw / "gdb9.sdf"
    unch = raw / "uncharacterized.txt"
    skip = load_qm9_skip_sdf_indices(unch)
    print(f"uncharacterized.txt -> skip indices count: {len(skip)}")

    RDLogger.DisableLog("rdApp.*")
    supplier = Chem.SDMolSupplier(str(sdf), removeHs=False, sanitize=False)
    rdkit_ok = 0
    rdkit_none = 0
    for idx, mol in enumerate(supplier):
        if idx in skip:
            continue
        if mol is None:
            rdkit_none += 1
        else:
            rdkit_ok += 1

    dataset = QM9(root=str(_REPO / "data" / "qm9"))
    pyg_n = len(dataset)

    print(f"PyG QM9 len(dataset):           {pyg_n}")
    print(f"RDKit (skip + sanitize=False) ok:   {rdkit_ok}")
    print(f"RDKit (skip + sanitize=False) None: {rdkit_none}")
    match = pyg_n == rdkit_ok
    print(f"对齐 (PyG == RDKit_ok):         {match}")
    if not match:
        raise SystemExit(1)
    print("OK: 条数一致。")

    x_path = _REPO / "outputs" / "features" / "X_all.npy"
    split_path = _REPO / "outputs" / "features" / "split_index.csv"
    if x_path.is_file():
        import numpy as np
        import pandas as pd

        x_n = int(np.load(x_path).shape[0])
        split_n = len(pd.read_csv(split_path))
        print()
        print("--- 指纹导出文件（若已运行 fingerprints.py）---")
        print(f"X_all.npy 行数:        {x_n}")
        print(f"split_index.csv 行数:  {split_n}")
        file_match = x_n == split_n == pyg_n
        print(f"与 PyG 一致:           {file_match}")
        if not file_match:
            raise SystemExit(2)


if __name__ == "__main__":
    main()
