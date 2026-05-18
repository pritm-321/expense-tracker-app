from __future__ import annotations

import datetime
from typing import Optional

from app.models.transaction import Transaction
from app.models.category import Category
from app.models.budget import Budget
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
    tx_type: Optional[str] = None,
    category_id: Optional[int] = None,
    note_query: Optional[str] = None,
) -> list[Transaction]:
    clauses: list[str] = []
    params: list[object] = []

    if month is not None:
        clauses.append("date LIKE ?")
        params.append(f"{month.strftime('%Y-%m')}%")
    if tx_type is not None:
        clauses.append("type = ?")
        params.append(tx_type)
    if category_id is not None:
        clauses.append("category_id = ?")
        params.append(category_id)
    if note_query:
        clauses.append("note LIKE ?")
        params.append(f"%{note_query}%")

    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"SELECT * FROM transactions{where} ORDER BY date DESC"

    conn = get_connection()
    try:
        rows = conn.execute(sql, params).fetchall()
        return [_row_to_transaction(r) for r in rows]
    finally:
        conn.close()


def update_transaction(tx: Transaction) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE transactions SET type=?, amount=?, category_id=?, date=?, note=? WHERE id=?",
            (tx.type, tx.amount, tx.category_id, tx.date.isoformat(), tx.note, tx.id),
        )
        conn.commit()
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


def set_budget(category_id: int, amount: int) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO budgets (category_id, amount, period) VALUES (?, ?, 'monthly')",
            (category_id, amount),
        )
        conn.commit()
    finally:
        conn.close()


def get_budgets() -> list[Budget]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM budgets").fetchall()
        return [
            Budget(
                category_id=r["category_id"],
                amount=r["amount"],
                period=r["period"],
            )
            for r in rows
        ]
    finally:
        conn.close()


def delete_budget(category_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM budgets WHERE category_id = ?", (category_id,))
        conn.commit()
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
