from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path
from unittest import mock

import pytest


@pytest.fixture()
def tmp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    db_file = tmp_path / "test_expenses.db"
    monkeypatch.setattr(
        "app.services.db._db_path", lambda: str(db_file)
    )
    return db_file


def test_init_db_creates_tables(tmp_db: Path) -> None:
    from app.services.db import init_db

    init_db()

    conn = sqlite3.connect(str(tmp_db))
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    conn.close()

    assert "transactions" in tables
    assert "categories" in tables
    assert "schema_version" in tables
    assert "settings" in tables
    assert "budgets" in tables


def test_init_db_seeds_default_categories(tmp_db: Path) -> None:
    from app.services.db import init_db

    init_db()

    conn = sqlite3.connect(str(tmp_db))
    count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    conn.close()

    assert count == 10  # 7 expense + 3 income


def test_init_db_idempotent(tmp_db: Path) -> None:
    from app.services.db import init_db

    init_db()
    init_db()  # second call must not duplicate seeds or crash

    conn = sqlite3.connect(str(tmp_db))
    count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    conn.close()

    assert count == 10
