from __future__ import annotations

import datetime
from decimal import Decimal

from app.services.db import get_connection


def monthly_totals(month: datetime.date) -> dict[str, Decimal]:
    """Returns {'income': Decimal, 'expense': Decimal, 'net': Decimal} for given month."""
    prefix = month.strftime("%Y-%m")
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT type, SUM(amount) FROM transactions WHERE date LIKE ? GROUP BY type",
            (f"{prefix}%",),
        ).fetchall()
    finally:
        conn.close()

    totals: dict[str, Decimal] = {"income": Decimal(0), "expense": Decimal(0)}
    for row in rows:
        totals[row[0]] = Decimal(row[1] or 0)
    totals["net"] = totals["income"] - totals["expense"]
    return totals


def category_breakdown(month: datetime.date) -> list[dict[str, object]]:
    """Returns list of {category_id, name, kind, total} for given month, sorted by total desc."""
    prefix = month.strftime("%Y-%m")
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT c.id, c.name, c.kind, SUM(t.amount) AS total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.date LIKE ?
            GROUP BY c.id
            ORDER BY total DESC
            """,
            (f"{prefix}%",),
        ).fetchall()
    finally:
        conn.close()

    return [
        {
            "category_id": r["id"],
            "name": r["name"],
            "kind": r["kind"],
            "total": Decimal(r["total"] or 0),
        }
        for r in rows
    ]


def budget_status(month: datetime.date) -> list[dict[str, object]]:
    """Per budgeted category for the month: budgeted, spent, remaining, pct."""
    prefix = month.strftime("%Y-%m")
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT c.id, c.name, b.amount AS budgeted,
                   COALESCE(SUM(t.amount), 0) AS spent
            FROM budgets b
            JOIN categories c ON c.id = b.category_id
            LEFT JOIN transactions t
                ON t.category_id = c.id
                AND t.type = 'expense'
                AND t.date LIKE ?
            GROUP BY c.id
            ORDER BY c.name
            """,
            (f"{prefix}%",),
        ).fetchall()
    finally:
        conn.close()

    result: list[dict[str, object]] = []
    for r in rows:
        budgeted = Decimal(r["budgeted"])
        spent = Decimal(r["spent"] or 0)
        pct = float(spent / budgeted * 100) if budgeted else 0.0
        result.append(
            {
                "category_id": r["id"],
                "name": r["name"],
                "budgeted": budgeted,
                "spent": spent,
                "remaining": budgeted - spent,
                "pct": pct,
                "over": spent > budgeted,
            }
        )
    return result
