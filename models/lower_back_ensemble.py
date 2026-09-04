"""Self-contained architecture for the frozen lower-back ensemble."""

from __future__ import annotations

import torch
from torch import nn

try:
    from .stroke_gait_inception import InceptionBlock
except ImportError:  # Direct execution from the models directory.
    from stroke_gait_inception import InceptionBlock


class LowerBackDomainNet(nn.Module):
    """Compact Inception-style binary member for one lower-back channel."""

    def __init__(self) -> None:
        super().__init__()
        self.features = nn.Sequential(
            InceptionBlock(1),
            nn.MaxPool1d(2),
            InceptionBlock(64),
            nn.AdaptiveAvgPool1d(1),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.30),
            nn.Linear(64, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(x)).squeeze(1)
