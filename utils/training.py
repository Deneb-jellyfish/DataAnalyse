from __future__ import annotations

import csv
import random
from pathlib import Path

import numpy as np
import torch


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)


def train_epoch(model, loader, optimizer, criterion, device) -> float:
    model.train()
    total_loss = 0.0
    total_graphs = 0

    for batch in loader:
        batch = batch.to(device)
        optimizer.zero_grad()
        pred = model(batch.x.float(), batch.edge_index, batch.batch)
        target = batch.y[:, 0].to(device).float()
        loss = criterion(pred, target)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * batch.num_graphs
        total_graphs += batch.num_graphs

    return total_loss / max(total_graphs, 1)


@torch.no_grad()
def evaluate(model, loader, criterion, device) -> float:
    model.eval()
    total_loss = 0.0
    total_graphs = 0

    for batch in loader:
        batch = batch.to(device)
        pred = model(batch.x.float(), batch.edge_index, batch.batch)
        target = batch.y[:, 0].to(device).float()
        loss = criterion(pred, target)

        total_loss += loss.item() * batch.num_graphs
        total_graphs += batch.num_graphs

    return total_loss / max(total_graphs, 1)


def write_history_csv(history: list[dict], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(history[0].keys()) if history else ["epoch"]
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(history)
