from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd
import torch
from torch_geometric.loader import DataLoader

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.model import MolGNN
from utils.dataset import (
    DEFAULT_SPLIT_CSV,
    add_physics_features,
    load_qm9_dataset,
    load_split_table,
    split_from_table,
)


@torch.no_grad()
def predict_values(model, loader, device) -> tuple[list[float], list[float]]:
    model.eval()
    preds: list[float] = []
    truths: list[float] = []
    for batch in loader:
        batch = batch.to(device)
        pred = model(batch.x.float(), batch.edge_index, batch.batch).detach().cpu().tolist()
        true = batch.y[:, 0].detach().cpu().tolist()
        preds.extend(float(x) for x in pred)
        truths.extend(float(x) for x in true)
    return truths, preds


def load_model(checkpoint_path: str | Path, device: torch.device) -> tuple[dict, MolGNN]:
    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    model = MolGNN(
        input_dim=checkpoint["input_dim"],
        hidden_dim=checkpoint.get("hidden_dim", 128),
    ).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    return checkpoint, model


def main() -> None:
    parser = argparse.ArgumentParser(description="Export GNN predictions from the QM9 test split.")
    parser.add_argument("--base-checkpoint", default="outputs/models/gnn_base.pt")
    parser.add_argument("--physics-checkpoint", default="outputs/models/gnn_physics.pt")
    parser.add_argument("--data-root", default="data/qm9")
    parser.add_argument("--split-csv", default=DEFAULT_SPLIT_CSV)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--output", default="outputs/features/predictions.csv")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset = load_qm9_dataset(args.data_root)
    split_df = load_split_table(args.split_csv)
    split_data = split_from_table(dataset, split_df)
    print(
        "Random QM9 split: "
        f"test={len(split_data['test_set'])}"
    )
    test_set = split_data["test_set"]
    test_rows = split_data["test_rows"].copy().reset_index(drop=True)

    _, base_model = load_model(args.base_checkpoint, device)
    base_loader = DataLoader(test_set, batch_size=args.batch_size, shuffle=False)
    y_true, y_pred_base = predict_values(base_model, base_loader, device)

    _, physics_model = load_model(args.physics_checkpoint, device)
    physics_set = add_physics_features(test_set)
    physics_loader = DataLoader(physics_set, batch_size=args.batch_size, shuffle=False)
    y_true_physics, y_pred_physics = predict_values(physics_model, physics_loader, device)

    if len(y_true) != len(test_rows) or len(y_true_physics) != len(test_rows):
        raise ValueError("Prediction rows do not align with split_index test rows.")

    result_df = test_rows.loc[:, ["dataset_index", "mol_id", "split", "smiles", "dipole"]].copy()
    result_df = result_df.rename(columns={"dipole": "y_true_from_split"})
    result_df["y_true"] = y_true
    result_df["y_pred_base"] = y_pred_base
    result_df["y_pred_physics"] = y_pred_physics
    result_df["abs_err_base"] = (result_df["y_pred_base"] - result_df["y_true"]).abs()
    result_df["abs_err_physics"] = (result_df["y_pred_physics"] - result_df["y_true"]).abs()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(output, index=False, encoding="utf-8")

    print(f"Saved predictions to {output}")


if __name__ == "__main__":
    main()
