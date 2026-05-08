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
