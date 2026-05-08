from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Category:
    id: int | None
    name: str
    kind: str  # 'income' | 'expense'
    icon: str
    color: str
