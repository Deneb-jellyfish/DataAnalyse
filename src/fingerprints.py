from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem
from sklearn.model_selection import train_test_split


def load_qm9_skip_sdf_indices(path: Path) -> set[int]:
    skip: set[int] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or not line[0].isdigit():
            continue
        skip.add(int(line.split()[0]) - 1)
    return skip


def mol_to_morgan_bits(
    mol: Chem.Mol | None,
    n_bits: int = 2048,
    radius: int = 2,
) -> np.ndarray:
    if mol is None:
        return np.zeros(n_bits, dtype=np.uint8)

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
    skip_path = raw_dir / "uncharacterized.txt"

    label_df = pd.read_csv(csv_path)
    y_all = label_df["mu"].to_numpy(dtype=np.float32)
    mol_id_all = label_df["mol_id"].astype(str).to_list()
    skip_sdf = load_qm9_skip_sdf_indices(skip_path)

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

    split_order = np.full(len(all_indices), -1, dtype=np.int64)
    split_order[train_idx] = np.arange(len(train_idx))
    split_order[test_idx] = np.arange(len(test_idx))

    split_df = pd.DataFrame(
        {
            "dataset_index": all_indices.astype(int),
            "index": all_indices.astype(int),
            "source_index": valid_indices.astype(int),
            "mol_id": mol_id_all,
            "split": np.where(np.isin(all_indices, train_idx), "train", "test"),
            "split_order": split_order.astype(int),
            "smiles": smiles_all,
            "dipole": y_all,
        }
    )
    split_df.to_csv(feature_dir / "split_index.csv", index=False)

    notes = [
        "# Feature Export Notes",
        "",
        "- Morgan fingerprint: radius=2, n_bits=2048.",
        "- Fingerprints are read from `data/qm9/raw/gdb9.sdf` with `sanitize=False` and the QM9 `uncharacterized.txt` skip list, matching the PyG QM9 filtered dataset.",
        "- Split: train/test = 8:2, random_state=42.",
        "- `split_index.csv` provides dataset_index/index/source_index/mol_id/split/split_order/smiles/dipole alignment fields.",
        "- `dataset_index` matches the PyG QM9 dataset index used by the GNN scripts.",
        "- `split_order` matches the row order inside `X_train.npy` or `X_test.npy` for each split.",
        "",
    ]
    (report_dir / "feature_notes.md").write_text("\n".join(notes), encoding="utf-8")

    print("fingerprint export complete")
    print(f"valid molecules: {len(valid_indices)}")
    print(f"train: {len(train_idx)}")
    print(f"test: {len(test_idx)}")
    print(f"saved features to: {feature_dir}")


if __name__ == "__main__":
    main()
