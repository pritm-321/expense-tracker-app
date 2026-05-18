from __future__ import annotations

import datetime
from decimal import Decimal
from pathlib import Path

import pytest


@pytest.fixture()
def seeded_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    db_file = tmp_path / "test.db"
    monkeypatch.setattr("app.services.db._db_path", lambda: str(db_file))
    from app.services.db import init_db
    init_db()
    return db_file


def test_monthly_totals_empty(seeded_db: Path) -> None:
    from app.services.analytics import monthly_totals
    totals = monthly_totals(datetime.date(2026, 5, 1))
    assert totals["income"] == Decimal(0)
    assert totals["expense"] == Decimal(0)
    assert totals["net"] == Decimal(0)


def test_monthly_totals_with_data(seeded_db: Path) -> None:
    from app.services.repository import add_transaction, get_categories
    from app.models.transaction import Transaction
    from app.services.analytics import monthly_totals

    cats = {c.kind: c for c in get_categories()}
    income_cat = cats["income"]
    expense_cat = cats["expense"]

    add_transaction(Transaction(None, "income", 50000, income_cat.id, datetime.date(2026, 5, 10), ""))
    add_transaction(Transaction(None, "expense", 20000, expense_cat.id, datetime.date(2026, 5, 15), "lunch"))

    totals = monthly_totals(datetime.date(2026, 5, 1))
    assert totals["income"] == Decimal(50000)
    assert totals["expense"] == Decimal(20000)
    assert totals["net"] == Decimal(30000)


def test_monthly_totals_ignores_other_months(seeded_db: Path) -> None:
    from app.services.repository import add_transaction, get_categories
    from app.models.transaction import Transaction
    from app.services.analytics import monthly_totals

    cat = next(c for c in get_categories() if c.kind == "expense")
    add_transaction(Transaction(None, "expense", 10000, cat.id, datetime.date(2026, 4, 1), ""))

    totals = monthly_totals(datetime.date(2026, 5, 1))
    assert totals["expense"] == Decimal(0)


def test_category_breakdown(seeded_db: Path) -> None:
    from app.services.repository import add_transaction, get_categories
    from app.models.transaction import Transaction
    from app.services.analytics import category_breakdown

    cat = next(c for c in get_categories() if c.kind == "expense")
    add_transaction(Transaction(None, "expense", 10000, cat.id, datetime.date(2026, 5, 1), ""))
    add_transaction(Transaction(None, "expense", 5000, cat.id, datetime.date(2026, 5, 9), ""))

    rows = category_breakdown(datetime.date(2026, 5, 1))
    assert len(rows) == 1
    assert rows[0]["category_id"] == cat.id
    assert rows[0]["total"] == Decimal(15000)


def test_budget_status_over_and_under(seeded_db: Path) -> None:
    from app.services.repository import add_transaction, get_categories, set_budget
    from app.models.transaction import Transaction
    from app.services.analytics import budget_status

    cat = next(c for c in get_categories() if c.kind == "expense")
    set_budget(cat.id, 10000)
    add_transaction(Transaction(None, "expense", 15000, cat.id, datetime.date(2026, 5, 3), ""))

    rows = budget_status(datetime.date(2026, 5, 1))
    assert len(rows) == 1
    r = rows[0]
    assert r["budgeted"] == Decimal(10000)
    assert r["spent"] == Decimal(15000)
    assert r["remaining"] == Decimal(-5000)
    assert r["over"] is True


def test_budget_status_no_budget(seeded_db: Path) -> None:
    from app.services.analytics import budget_status

    assert budget_status(datetime.date(2026, 5, 1)) == []
