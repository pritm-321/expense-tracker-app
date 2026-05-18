from __future__ import annotations

from decimal import Decimal

from app.services.settings import get_setting

DEFAULT_CURRENCY_SYMBOL = "₹"


def currency_symbol() -> str:
    return get_setting("currency_symbol", DEFAULT_CURRENCY_SYMBOL) or DEFAULT_CURRENCY_SYMBOL


def format_money(minor_units: int | Decimal) -> str:
    """Format integer minor units (paise) as a currency string for display only."""
    major = Decimal(minor_units) / 100
    return f"{currency_symbol()}{major:,.2f}"
