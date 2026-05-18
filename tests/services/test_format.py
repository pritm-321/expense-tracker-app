from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture()
def seeded_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    db_file = tmp_path / "test.db"
    monkeypatch.setattr("app.services.db._db_path", lambda: str(db_file))
    from app.services.db import init_db

    init_db()
    return db_file


def test_format_money_default_symbol(seeded_db: Path) -> None:
    from app.utils.format import format_money

    assert format_money(12550) == "₹125.50"
    assert format_money(0) == "₹0.00"
    assert format_money(100000000) == "₹1,000,000.00"


def test_format_money_honors_setting(seeded_db: Path) -> None:
    from app.services.settings import set_setting
    from app.utils.format import format_money

    set_setting("currency_symbol", "$")
    assert format_money(12550) == "$125.50"
