from __future__ import annotations

import torch
from torch import nn
from torch_geometric.nn import GCNConv, global_mean_pool


class MolGNN(nn.Module):
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 128,
        num_layers: int = 3,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        if num_layers < 2:
            raise ValueError("num_layers must be at least 2")

        convs = [GCNConv(input_dim, hidden_dim)]
        convs.extend(GCNConv(hidden_dim, hidden_dim) for _ in range(num_layers - 1))
        self.convs = nn.ModuleList(convs)

        self.dropout = nn.Dropout(dropout)
        self.regressor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor, batch: torch.Tensor) -> torch.Tensor:
        for conv in self.convs:
            x = torch.relu(conv(x, edge_index))
        pooled = global_mean_pool(x, batch)
        pooled = self.dropout(pooled)
        return self.regressor(pooled).squeeze(-1)
