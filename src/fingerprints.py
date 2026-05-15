from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem
from sklearn.model_selection import train_test_split

_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
from qm9_raw_utils import load_qm9_skip_sdf_indices


def mol_to_morgan_bits(mol: Chem.Mol | None, n_bits: int = 2048, radius: int = 2) -> np.ndarray:
    if mol is None:
        return np.zeros(n_bits, dtype=np.uint8)

    # sanitize=False 与 PyG 对齐时，需先感知环系，否则 Morgan 会报 RingInfo not initialized
    mol.UpdatePropertyCache(strict=False)
    Chem.GetSSSR(mol)

    bit_vector = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
    arr = np.zeros((n_bits,), dtype=np.uint8)
    DataStructs.ConvertToNumpyArray(bit_vector, arr)
    return arr


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    feature_dir = repo_root / "outputs" / "features"
    report_dir = repo_root / "outputs" / "reports"
    feature_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    n_bits = 2048
    raw_dir = repo_root / "data" / "qm9" / "raw"
    sdf_path = raw_dir / "gdb9.sdf"
    csv_path = raw_dir / "gdb9.sdf.csv"

    label_df = pd.read_csv(csv_path)
    y_all = label_df["mu"].to_numpy(dtype=np.float32)
    mol_id_all = label_df["mol_id"].astype(str).to_list()

    skip_sdf = load_qm9_skip_sdf_indices(raw_dir / "uncharacterized.txt")

    # 与 PyG QM9 一致使用 sanitize=False，否则约 1403 条在 PyG 中存在但 strict sanitize 失败，条数会对不齐。
    RDLogger.DisableLog("rdApp.*")
    supplier = Chem.SDMolSupplier(str(sdf_path), removeHs=False, sanitize=False)
    x_rows = []
    smiles_all = []
    valid_indices = []

    for idx, mol in enumerate(supplier):
        if idx >= len(y_all):
            break
        if idx in skip_sdf:
            continue
        if mol is None:
            continue

        x_rows.append(mol_to_morgan_bits(mol, n_bits=n_bits, radius=2))
        smiles_all.append(Chem.MolToSmiles(mol, isomericSmiles=True))
        valid_indices.append(idx)

        if (idx + 1) % 20000 == 0:
            print(f"processed {idx + 1}/{len(y_all)}")

    valid_indices = np.asarray(valid_indices, dtype=np.int64)
    x_all = np.vstack(x_rows).astype(np.uint8)
    y_all = y_all[valid_indices]
    mol_id_all = [mol_id_all[i] for i in valid_indices]

    all_indices = np.arange(len(valid_indices), dtype=np.int64)
    train_idx, test_idx = train_test_split(
        all_indices,
        test_size=0.2,
        random_state=42,
        shuffle=True,
    )

    x_train = x_all[train_idx]
    x_test = x_all[test_idx]
    y_train = y_all[train_idx]
    y_test = y_all[test_idx]

    np.save(feature_dir / "X_train.npy", x_train)
    np.save(feature_dir / "X_test.npy", x_test)
    np.save(feature_dir / "y_train.npy", y_train)
    np.save(feature_dir / "y_test.npy", y_test)
    np.save(feature_dir / "X_all.npy", x_all)
    np.save(feature_dir / "y_all.npy", y_all)

    split_df = pd.DataFrame(
        {
            "index": all_indices.astype(int),
            "source_index": valid_indices.astype(int),
            "mol_id": mol_id_all,
            "split": np.where(np.isin(all_indices, train_idx), "train", "test"),
            "smiles": smiles_all,
            "dipole": y_all,
        }
    )
    split_df.to_csv(feature_dir / "split_index.csv", index=False)

    notes = [
        "# Feature Export Notes",
        "",
        "- Morgan fingerprint: radius=2, n_bits=2048。",
        "- 指纹来源: `data/qm9/raw/gdb9.sdf` + `uncharacterized.txt` 跳过列表，与 **PyG `QM9` 条数一致**（约 130,831）；SDF 读取使用 `sanitize=False`（与 PyG 一致）。",
        "- 数据切分: train/test = 8:2，random_state=42。",
        "- `split_index.csv` 提供 index/source_index/mol_id/split/smiles/dipole 对齐信息。",
        "- 聚类与随机森林建议使用 `X_all.npy` 或 `X_train.npy` 视任务而定。",
        "",
    ]
    (report_dir / "feature_notes.md").write_text("\n".join(notes), encoding="utf-8")

    print("fingerprint export complete")
    print(f"saved features to: {feature_dir}")


if __name__ == "__main__":
    main()
