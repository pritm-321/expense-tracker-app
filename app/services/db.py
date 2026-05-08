from __future__ import annotations

import sqlite3
from pathlib import Path

try:
    from kivy.logger import Logger
except ImportError:
    import logging as _logging
    Logger = _logging.getLogger(__name__)  # type: ignore[assignment]


def _db_path() -> str:
    try:
        from kivy.app import App
        app = App.get_running_app()
        if app is not None:
            return app.user_data_dir + "/expenses.db"
    except Exception:
        pass
    return str(Path.home() / "expenses.db")


# Each entry is a complete SQL block for that schema version.
# NEVER edit an existing entry — append a new one for each schema change.
MIGRATIONS: list[str] = [
    # v0 → v1: initial schema
    """
    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY
    );

    CREATE TABLE IF NOT EXISTS categories (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        name  TEXT NOT NULL,
        kind  TEXT NOT NULL CHECK(kind IN ('income', 'expense')),
        icon  TEXT NOT NULL DEFAULT '',
        color TEXT NOT NULL DEFAULT '#607D8B'
    );

    CREATE TABLE IF NOT EXISTS transactions (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        type        TEXT    NOT NULL CHECK(type IN ('income', 'expense')),
        amount      INTEGER NOT NULL,
        category_id INTEGER NOT NULL REFERENCES categories(id),
        date        TEXT    NOT NULL,
        note        TEXT    NOT NULL DEFAULT '',
        created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
]

_DEFAULT_CATEGORIES: list[tuple[str, str, str, str]] = [
    ("Food",          "expense", "food",             "#FF5722"),
    ("Transport",     "expense", "car",              "#2196F3"),
    ("Bills",         "expense", "receipt",          "#9C27B0"),
    ("Shopping",      "expense", "cart",             "#E91E63"),
    ("Entertainment", "expense", "movie",            "#FF9800"),
    ("Health",        "expense", "heart-pulse",      "#4CAF50"),
    ("Other",         "expense", "dots-horizontal",  "#607D8B"),
    ("Salary",        "income",  "cash",             "#4CAF50"),
    ("Gift",          "income",  "gift",             "#E91E63"),
    ("Other",         "income",  "dots-horizontal",  "#607D8B"),
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _current_version(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
    ).fetchone()
    if row is None:
        return 0
    row = conn.execute("SELECT MAX(version) FROM schema_version").fetchone()
    return row[0] if row[0] is not None else 0


def init_db() -> None:
    conn = get_connection()
    try:
        version = _current_version(conn)
        pending = MIGRATIONS[version:]
        for i, sql in enumerate(pending, start=version + 1):
            Logger.info(f"ExpenseTracker: running DB migration to v{i}")
            conn.executescript(sql)
            conn.execute(
                "INSERT OR REPLACE INTO schema_version VALUES (?)", (i,)
            )
            conn.commit()

        _seed_default_categories(conn)
    finally:
        conn.close()


def _seed_default_categories(conn: sqlite3.Connection) -> None:
    count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    if count > 0:
        return
    Logger.info("ExpenseTracker: seeding default categories")
    conn.executemany(
        "INSERT INTO categories (name, kind, icon, color) VALUES (?, ?, ?, ?)",
        _DEFAULT_CATEGORIES,
    )
    conn.commit()
