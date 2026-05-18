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


def test_get_setting_default(seeded_db: Path) -> None:
    from app.services.settings import get_setting

    assert get_setting("missing") is None
    assert get_setting("missing", "fallback") == "fallback"


def test_set_and_get_setting(seeded_db: Path) -> None:
    from app.services.settings import get_setting, set_setting

    set_setting("currency_symbol", "$")
    assert get_setting("currency_symbol") == "$"

    set_setting("currency_symbol", "€")  # upsert
    assert get_setting("currency_symbol") == "€"
