from __future__ import annotations

from pathlib import Path

from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen

from app.services.settings import get_setting, set_setting
from app.utils.format import DEFAULT_CURRENCY_SYMBOL
from app.widgets.bottom_nav import BottomNavBar  # noqa: F401 — registers KV rule

Builder.load_file(str(Path(__file__).parent.parent.parent / "assets" / "settings.kv"))

_CURRENCIES: list[tuple[str, str]] = [
    ("₹  Indian Rupee", "₹"),
    ("$  US Dollar", "$"),
    ("€  Euro", "€"),
    ("£  Pound Sterling", "£"),
    ("¥  Yen", "¥"),
]


class SettingsScreen(MDScreen):
    def on_enter(self) -> None:
        symbol = get_setting("currency_symbol", DEFAULT_CURRENCY_SYMBOL)
        self.ids.currency_field.text = symbol or DEFAULT_CURRENCY_SYMBOL
        self._apply_theme_label()

    def open_currency_menu(self) -> None:
        items = [
            {
                "text": label,
                "viewclass": "OneLineListItem",
                "on_release": lambda s=sym: self._select_currency(s),
            }
            for label, sym in _CURRENCIES
        ]
        self._menu = MDDropdownMenu(
            caller=self.ids.currency_field,
            items=items,
            width_mult=4,
        )
        self._menu.open()

    def _select_currency(self, symbol: str) -> None:
        set_setting("currency_symbol", symbol)
        self.ids.currency_field.text = symbol
        self._menu.dismiss()
        Logger.info("Settings: currency_symbol=%s", symbol)

    def toggle_theme(self) -> None:
        app = App.get_running_app()
        new_style = "Dark" if app.theme_cls.theme_style == "Light" else "Light"
        app.theme_cls.theme_style = new_style
        set_setting("theme", new_style)
        self._apply_theme_label()
        Logger.info("Settings: theme=%s", new_style)

    def _apply_theme_label(self) -> None:
        style = App.get_running_app().theme_cls.theme_style
        self.ids.theme_btn.text = f"Theme: {style}"
