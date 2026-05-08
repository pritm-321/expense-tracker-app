from __future__ import annotations

import datetime
from dataclasses import dataclass


@dataclass
class Transaction:
    id: int | None
    type: str  # 'income' | 'expense'
    amount: int  # minor units (paise)
    category_id: int
    date: datetime.date
    note: str
    created_at: datetime.datetime | None = None
