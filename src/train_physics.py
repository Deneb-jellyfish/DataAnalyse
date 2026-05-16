from __future__ import annotations

import argparse
import time
from pathlib import Path
import sys

import torch
from torch import nn
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
from utils.training import evaluate, seed_everything, train_epoch, write_history_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Train physics-augmented GNN with random 80/20 QM9 split.")
    parser.add_argument("--data-root", default="data/qm9")
    parser.add_argument("--split-csv", default=DEFAULT_SPLIT_CSV)
    parser.add_argument("--epochs", type=int, default=200)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--min-lr", type=float, default=1e-5)
    parser.add_argument(
        "--scheduler",
        choices=["none", "cosine"],
        default="cosine",
        help="Learning-rate schedule used across epochs.",
    )
    parser.add_argument("--weight-decay", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--save-path", default="outputs/models/gnn_physics.pt")
    parser.add_argument("--log-path", default="outputs/logs/train_gnn_physics_metrics.csv")
    args = parser.parse_args()

    seed_everything(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    dataset = load_qm9_dataset(args.data_root)
    split_df = load_split_table(args.split_csv)
    split_data = split_from_table(dataset, split_df)
    print(
        "Random QM9 split: "
        f"train={len(split_data['train_set'])}, test={len(split_data['test_set'])}"
    )
    train_set = add_physics_features(split_data["train_set"])
    test_set = add_physics_features(split_data["test_set"])

    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True)
    test_loader = DataLoader(test_set, batch_size=args.batch_size, shuffle=False)

    input_dim = train_set[0].x.size(-1)
    model = MolGNN(input_dim=input_dim, hidden_dim=args.hidden_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = None
    if args.scheduler == "cosine":
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=args.epochs,
            eta_min=args.min_lr,
        )
    criterion = nn.MSELoss()

    history: list[dict] = []
    best_test = float("inf")
    best_state = None

    for epoch in range(1, args.epochs + 1):
        start = time.perf_counter()
        train_mse = train_epoch(model, train_loader, optimizer, criterion, device)
        test_mse = evaluate(model, test_loader, criterion, device)
        epoch_seconds = time.perf_counter() - start
        history.append(
            {
                "epoch": epoch,
                "lr": optimizer.param_groups[0]["lr"],
                "train_mse": train_mse,
                "test_mse": test_mse,
                "epoch_seconds": epoch_seconds,
            }
        )
        print(
            f"Epoch {epoch:03d} | train_mse={train_mse:.6f} | "
            f"test_mse={test_mse:.6f} | "
            f"epoch_time={epoch_seconds:.2f}s"
        )

        if test_mse < best_test:
            best_test = test_mse
            best_state = {k: v.detach().cpu() for k, v in model.state_dict().items()}

        if scheduler is not None:
            scheduler.step()

    if best_state is None:
        raise RuntimeError("No checkpoint was produced during training.")

    save_path = Path(args.save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": best_state,
            "input_dim": input_dim,
            "hidden_dim": args.hidden_dim,
            "best_test_mse": best_test,
            "split_csv": args.split_csv,
            "seed": args.seed,
            "scheduler": args.scheduler,
            "lr": args.lr,
            "min_lr": args.min_lr,
            "model_name": "gnn_physics",
            "physics_features": [
                "electronegativity",
                "atomic_mass",
                "covalent_radius",
                "valence_electrons",
                "hetero_atom",
                "degree",
                "bond_polarity_sum",
                "bond_polarity_abs_sum",
                "distance_to_center",
                "normalized_atom_count",
            ],
        },
        save_path,
    )

    write_history_csv(history, args.log_path)

    print(f"Saved checkpoint to {save_path}")
    print(f"Saved training log to {args.log_path}")
    print(f"Best test_mse={best_test:.6f}")


if __name__ == "__main__":
    main()
