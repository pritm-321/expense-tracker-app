from __future__ import annotations

import datetime
from typing import Optional

from app.models.transaction import Transaction
from app.models.category import Category
from app.services.db import get_connection


def add_transaction(tx: Transaction) -> int:
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO transactions (type, amount, category_id, date, note) VALUES (?,?,?,?,?)",
            (tx.type, tx.amount, tx.category_id, tx.date.isoformat(), tx.note),
        )
        conn.commit()
        return cur.lastrowid  # type: ignore[return-value]
    finally:
        conn.close()


def get_transactions(
    month: Optional[datetime.date] = None,
) -> list[Transaction]:
    conn = get_connection()
    try:
        if month is not None:
            prefix = month.strftime("%Y-%m")
            rows = conn.execute(
                "SELECT * FROM transactions WHERE date LIKE ? ORDER BY date DESC",
                (f"{prefix}%",),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM transactions ORDER BY date DESC"
            ).fetchall()
        return [_row_to_transaction(r) for r in rows]
    finally:
        conn.close()


def delete_transaction(tx_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
        conn.commit()
    finally:
        conn.close()


def get_categories(kind: Optional[str] = None) -> list[Category]:
    conn = get_connection()
    try:
        if kind is not None:
            rows = conn.execute(
                "SELECT * FROM categories WHERE kind = ?", (kind,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM categories").fetchall()
        return [_row_to_category(r) for r in rows]
    finally:
        conn.close()


def _row_to_transaction(row: object) -> Transaction:
    return Transaction(
        id=row["id"],  # type: ignore[index]
        type=row["type"],  # type: ignore[index]
        amount=row["amount"],  # type: ignore[index]
        category_id=row["category_id"],  # type: ignore[index]
        date=datetime.date.fromisoformat(row["date"]),  # type: ignore[index]
        note=row["note"],  # type: ignore[index]
        created_at=datetime.datetime.fromisoformat(row["created_at"]),  # type: ignore[index]
    )


def _row_to_category(row: object) -> Category:
    return Category(
        id=row["id"],  # type: ignore[index]
        name=row["name"],  # type: ignore[index]
        kind=row["kind"],  # type: ignore[index]
        icon=row["icon"],  # type: ignore[index]
        color=row["color"],  # type: ignore[index]
    )
