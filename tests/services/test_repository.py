from __future__ import annotations

import datetime
from pathlib import Path

import pytest


@pytest.fixture()
def seeded_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    db_file = tmp_path / "test.db"
    monkeypatch.setattr("app.services.db._db_path", lambda: str(db_file))
    from app.services.db import init_db

    init_db()
    return db_file


def test_add_update_delete_transaction(seeded_db: Path) -> None:
    from app.models.transaction import Transaction
    from app.services.repository import (
        add_transaction,
        delete_transaction,
        get_categories,
        get_transactions,
        update_transaction,
    )

    cat = next(c for c in get_categories() if c.kind == "expense")
    tx_id = add_transaction(
        Transaction(None, "expense", 10000, cat.id, datetime.date(2026, 5, 4), "tea")
    )

    txs = get_transactions(month=datetime.date(2026, 5, 1))
    assert len(txs) == 1
    assert txs[0].amount == 10000

    update_transaction(
        Transaction(tx_id, "expense", 25000, cat.id, datetime.date(2026, 5, 4), "lunch")
    )
    txs = get_transactions(month=datetime.date(2026, 5, 1))
    assert txs[0].amount == 25000
    assert txs[0].note == "lunch"

    delete_transaction(tx_id)
    assert get_transactions(month=datetime.date(2026, 5, 1)) == []


def test_get_transactions_filters(seeded_db: Path) -> None:
    from app.models.transaction import Transaction
    from app.services.repository import add_transaction, get_categories, get_transactions

    cats = {c.kind: c for c in get_categories()}
    inc, exp = cats["income"], cats["expense"]
    add_transaction(Transaction(None, "income", 50000, inc.id, datetime.date(2026, 5, 2), "pay"))
    add_transaction(Transaction(None, "expense", 8000, exp.id, datetime.date(2026, 5, 3), "bus fare"))

    assert len(get_transactions(tx_type="income")) == 1
    assert len(get_transactions(category_id=exp.id)) == 1
    assert len(get_transactions(note_query="fare")) == 1
    assert get_transactions(note_query="zzz") == []


def test_budget_crud(seeded_db: Path) -> None:
    from app.services.repository import (
        delete_budget,
        get_budgets,
        get_categories,
        set_budget,
    )

    cat = next(c for c in get_categories() if c.kind == "expense")
    set_budget(cat.id, 500000)
    budgets = get_budgets()
    assert len(budgets) == 1
    assert budgets[0].category_id == cat.id
    assert budgets[0].amount == 500000

    set_budget(cat.id, 700000)  # upsert
    assert get_budgets()[0].amount == 700000

    delete_budget(cat.id)
    assert get_budgets() == []
