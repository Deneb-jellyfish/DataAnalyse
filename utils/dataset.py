from __future__ import annotations

from pathlib import Path

import pandas as pd
import torch
from torch_geometric.datasets import QM9


TARGET_INDEX = 0  # dipole moment mu
DEFAULT_SPLIT_CSV = "outputs/features/split_index.csv"
ELECTRONEGATIVITY = {
    1: 2.20,
    6: 2.55,
    7: 3.04,
    8: 3.44,
    9: 3.98,
}
ATOMIC_MASS = {
    1: 1.008,
    6: 12.011,
    7: 14.007,
    8: 15.999,
    9: 18.998,
}
COVALENT_RADIUS = {
    1: 0.31,
    6: 0.76,
    7: 0.71,
    8: 0.66,
    9: 0.57,
}
VALENCE_ELECTRONS = {
    1: 1.0,
    6: 4.0,
    7: 5.0,
    8: 6.0,
    9: 7.0,
}


def load_qm9_dataset(root: str | Path) -> QM9:
    return QM9(root=str(root))


def load_split_table(path: str | Path) -> pd.DataFrame:
    split_path = Path(path)
    if not split_path.exists():
        raise FileNotFoundError(
            f"Split file not found: {split_path}. Run `python src/fingerprints.py` first."
        )
    df = pd.read_csv(split_path)
    required = {"dataset_index", "mol_id", "split", "smiles", "dipole"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Split file missing columns: {sorted(missing)}")
    return df


def split_from_table(dataset: QM9, split_df: pd.DataFrame) -> dict[str, list]:
    train_rows = split_df[split_df["split"] == "train"].reset_index(drop=True)
    test_rows = split_df[split_df["split"] == "test"].reset_index(drop=True)

    train_idx = train_rows["dataset_index"].astype(int).tolist()
    test_idx = test_rows["dataset_index"].astype(int).tolist()

    train_set = [dataset[i].clone() for i in train_idx]
    test_set = [dataset[i].clone() for i in test_idx]

    return {
        "train_idx": train_idx,
        "test_idx": test_idx,
        "train_rows": train_rows,
        "test_rows": test_rows,
        "train_set": train_set,
        "test_set": test_set,
    }


def build_physics_features_from_graph(data) -> torch.Tensor:
    z = data.z.to(torch.long).view(-1)
    num_atoms = int(z.numel())

    electronegativity = torch.tensor(
        [ELECTRONEGATIVITY.get(int(v.item()), 0.0) for v in z],
        dtype=torch.float32,
    )
    atomic_mass = torch.tensor(
        [ATOMIC_MASS.get(int(v.item()), 0.0) for v in z],
        dtype=torch.float32,
    )
    covalent_radius = torch.tensor(
        [COVALENT_RADIUS.get(int(v.item()), 0.0) for v in z],
        dtype=torch.float32,
    )
    valence_electrons = torch.tensor(
        [VALENCE_ELECTRONS.get(int(v.item()), 0.0) for v in z],
        dtype=torch.float32,
    )
    hetero_atom = ((z == 7) | (z == 8) | (z == 9)).to(torch.float32)

    degree = torch.zeros(num_atoms, dtype=torch.float32)
    bond_polarity_sum = torch.zeros(num_atoms, dtype=torch.float32)
    bond_polarity_abs_sum = torch.zeros(num_atoms, dtype=torch.float32)
    row, col = data.edge_index
    for src, dst in zip(row.tolist(), col.tolist()):
        diff = electronegativity[src] - electronegativity[dst]
        degree[src] += 1.0
        bond_polarity_sum[src] += diff
        bond_polarity_abs_sum[src] += diff.abs()

    pos = data.pos.to(torch.float32)
    centered_pos = pos - pos.mean(dim=0, keepdim=True)
    distance_to_center = torch.linalg.vector_norm(centered_pos, dim=1)
    normalized_atom_count = torch.full((num_atoms,), float(num_atoms) / 29.0)

    return torch.stack(
        [
            electronegativity,
            atomic_mass / 20.0,
            covalent_radius,
            valence_electrons / 8.0,
            hetero_atom,
            degree / 4.0,
            bond_polarity_sum,
            bond_polarity_abs_sum,
            distance_to_center,
            normalized_atom_count,
        ],
        dim=-1,
    )


def add_physics_features(dataset_items: list) -> list:
    augmented = []
    for data in dataset_items:
        item = data.clone()
        extra = build_physics_features_from_graph(item)
        item.x = torch.cat([item.x.float(), extra], dim=-1)
        augmented.append(item)
    return augmented
