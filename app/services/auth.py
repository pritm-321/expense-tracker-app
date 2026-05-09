from __future__ import annotations

import hashlib
import secrets

from app.services.db import get_connection

_KEY_HASH = "pin_hash"
_KEY_SALT = "pin_salt"


def is_pin_set() -> bool:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT value FROM settings WHERE key = ?", (_KEY_HASH,)
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def set_pin(pin: str) -> None:
    salt = secrets.token_hex(16)
    pin_hash = _hash(pin, salt)
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (_KEY_SALT, salt),
        )
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (_KEY_HASH, pin_hash),
        )
        conn.commit()
    finally:
        conn.close()


def verify_pin(pin: str) -> bool:
    conn = get_connection()
    try:
        salt_row = conn.execute(
            "SELECT value FROM settings WHERE key = ?", (_KEY_SALT,)
        ).fetchone()
        hash_row = conn.execute(
            "SELECT value FROM settings WHERE key = ?", (_KEY_HASH,)
        ).fetchone()
        if salt_row is None or hash_row is None:
            return False
        return secrets.compare_digest(_hash(pin, salt_row[0]), hash_row[0])
    finally:
        conn.close()


def _hash(pin: str, salt: str) -> str:
    return hashlib.sha256((salt + pin).encode()).hexdigest()
