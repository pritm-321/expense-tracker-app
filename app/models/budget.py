from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Budget:
    category_id: int
    amount: int  # minor units (paise), monthly limit
    period: str = "monthly"
