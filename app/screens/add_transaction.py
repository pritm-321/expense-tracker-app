from __future__ import annotations

import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from kivy.lang import Builder
from kivy.logger import Logger
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.screen import MDScreen

from app.models.transaction import Transaction
from app.services import repository

Builder.load_file(str(Path(__file__).parent.parent.parent / "assets" / "add_transaction.kv"))

_ACTIVE_COLOR = (0.13, 0.59, 0.95, 1)
_INACTIVE_COLOR = (0.8, 0.8, 0.8, 1)


class AddTransactionScreen(MDScreen):
    def on_enter(self) -> None:
        self._tx_type = "expense"
        self._category_id: int | None = None
        self._categories: list = []
        self._selected_date = datetime.date.today()

        self.ids.amount_field.text = ""
        self.ids.category_field.text = ""
        self.ids.note_field.text = ""
        self.ids.date_field.text = self._selected_date.isoformat()

        self._apply_type_buttons()
        self._reload_categories()

    def set_type(self, tx_type: str) -> None:
        self._tx_type = tx_type
        self._category_id = None
        self.ids.category_field.text = ""
        self._apply_type_buttons()
        self._reload_categories()

    def _apply_type_buttons(self) -> None:
        if self._tx_type == "expense":
            self.ids.btn_expense.md_bg_color = self.theme_cls.primary_color
            self.ids.btn_income.md_bg_color = _INACTIVE_COLOR
        else:
            self.ids.btn_income.md_bg_color = self.theme_cls.primary_color
            self.ids.btn_expense.md_bg_color = _INACTIVE_COLOR

    def _reload_categories(self) -> None:
        self._categories = repository.get_categories(kind=self._tx_type)

    def open_category_menu(self) -> None:
        if not self._categories:
            self._reload_categories()

        items = [
            {
                "text": cat.name,
                "viewclass": "OneLineListItem",
                "on_release": lambda c=cat: self._select_category(c),
            }
            for cat in self._categories
        ]
        self._menu = MDDropdownMenu(
            caller=self.ids.category_field,
            items=items,
            width_mult=4,
        )
        self._menu.open()

    def _select_category(self, cat: object) -> None:
        self._category_id = cat.id  # type: ignore[attr-defined]
        self.ids.category_field.text = cat.name  # type: ignore[attr-defined]
        self._menu.dismiss()

    def open_date_picker(self) -> None:
        picker = MDDatePicker(
            year=self._selected_date.year,
            month=self._selected_date.month,
            day=self._selected_date.day,
        )
        picker.bind(on_save=self._on_date_save, on_cancel=lambda *_: picker.dismiss())
        picker.open()

    def _on_date_save(self, instance: object, value: datetime.date, *args: object) -> None:
        self._selected_date = value
        self.ids.date_field.text = value.isoformat()

    def save(self) -> None:
        amount_text = self.ids.amount_field.text.strip()
        if not amount_text:
            Logger.warning("AddTransaction: amount empty")
            self.ids.amount_field.error = True
            return

        try:
            rupees = Decimal(amount_text)
        except InvalidOperation:
            Logger.warning("AddTransaction: invalid amount %s", amount_text)
            self.ids.amount_field.error = True
            return

        if rupees <= 0:
            self.ids.amount_field.error = True
            return

        if self._category_id is None:
            Logger.warning("AddTransaction: no category selected")
            self.ids.category_field.error = True
            return

        paise = int(rupees * 100)
        tx = Transaction(
            id=None,
            type=self._tx_type,
            amount=paise,
            category_id=self._category_id,
            date=self._selected_date,
            note=self.ids.note_field.text.strip(),
            created_at=None,
        )
        repository.add_transaction(tx)
        Logger.info("AddTransaction: saved %s ₹%s", self._tx_type, rupees)
        self.go_back()

    def go_back(self) -> None:
        self.manager.current = "home"
