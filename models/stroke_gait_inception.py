"""Architecture for the released three-channel stroke-gait research prototype."""

from __future__ import annotations

import torch
from torch import nn


class InceptionBlock(nn.Module):
    """One residual multi-kernel temporal block used by the release candidate."""

    def __init__(self, in_channels: int, out_channels: int = 16) -> None:
        super().__init__()
        bottleneck_channels = min(32, in_channels)
        # Attribute names deliberately match the released checkpoint.
        self.b = nn.Conv1d(in_channels, bottleneck_channels, 1, bias=False)
        self.br = nn.ModuleList(
            [
                nn.Conv1d(bottleneck_channels, out_channels, 7, padding=3, bias=False),
                nn.Conv1d(bottleneck_channels, out_channels, 15, padding=7, bias=False),
                nn.Conv1d(bottleneck_channels, out_channels, 25, padding=12, bias=False),
            ]
        )
        self.pool = nn.Conv1d(in_channels, out_channels, 1, bias=False)
        self.bn = nn.BatchNorm1d(out_channels * 4)
        self.res = (
            nn.Conv1d(in_channels, out_channels * 4, 1, bias=False)
            if in_channels != out_channels * 4
            else nn.Identity()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        bottleneck = self.b(x)
        branches = [branch(bottleneck) for branch in self.br]
        pooled = nn.functional.max_pool1d(x, 3, stride=1, padding=1)
        branches.append(self.pool(pooled))
        return nn.functional.gelu(self.bn(torch.cat(branches, dim=1)) + self.res(x))


class StrokeGaitInception(nn.Module):
    """Binary logit model for a `(batch, 3, 500)` LB/LF/RF magnitude tensor."""

    def __init__(self) -> None:
        super().__init__()
        # Attribute names deliberately match the released checkpoint.
        self.f = nn.Sequential(
            InceptionBlock(3),
            nn.MaxPool1d(2),
            InceptionBlock(64),
            nn.AdaptiveAvgPool1d(1),
        )
        self.c = nn.Sequential(nn.Flatten(), nn.Dropout(0.30), nn.Linear(64, 1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.c(self.f(x)).squeeze(1)
