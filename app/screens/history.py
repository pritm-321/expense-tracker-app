from __future__ import annotations

import datetime
from pathlib import Path

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen

from app.services import repository
from app.widgets.bottom_nav import BottomNavBar  # noqa: F401
from app.widgets.transaction_card import TransactionCard

Builder.load_file(str(Path(__file__).parent.parent.parent / "assets" / "history.kv"))


class HistoryScreen(MDScreen):
    month_label = StringProperty("")

    def on_enter(self) -> None:
        self._month = datetime.date.today().replace(day=1)
        self._dialog: MDDialog | None = None
        self._refresh()

    def prev_month(self) -> None:
        first = self._month
        self._month = (first - datetime.timedelta(days=1)).replace(day=1)
        self._refresh()

    def next_month(self) -> None:
        first = self._month
        # advance to first day of next month
        if first.month == 12:
            self._month = first.replace(year=first.year + 1, month=1)
        else:
            self._month = first.replace(month=first.month + 1)
        self._refresh()

    def _refresh(self) -> None:
        self.month_label = self._month.strftime("%B %Y")
        self._load_transactions()

    def _load_transactions(self) -> None:
        container = self.ids.transaction_list
        container.clear_widgets()

        txs = repository.get_transactions(month=self._month)

        if not txs:
            self.ids.empty_label.text = "No transactions this month."
            return

        self.ids.empty_label.text = ""
        cat_map = {c.id: c for c in repository.get_categories()}

        for tx in txs:
            card = TransactionCard(
                transaction=tx,
                category=cat_map.get(tx.category_id),
            )
            card.size_hint_x = 1

            delete_btn = MDIconButton(
                icon="trash-can-outline",
                size_hint=(None, None),
                size=("40dp", "68dp"),
                theme_icon_color="Custom",
                icon_color=(0.83, 0.18, 0.18, 1),
            )
            tx_ref = tx
            delete_btn.bind(on_release=lambda *_, t=tx_ref: self._confirm_delete(t))

            row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height="68dp",
                spacing="4dp",
            )
            row.add_widget(card)
            row.add_widget(delete_btn)
            container.add_widget(row)

    def _confirm_delete(self, tx: object) -> None:
        from decimal import Decimal
        amount = Decimal(tx.amount) / 100  # type: ignore[attr-defined]
        text = f"Delete ₹{amount:,.2f} {tx.type} transaction?"  # type: ignore[attr-defined]

        def _do_delete(*_: object) -> None:
            if self._dialog:
                self._dialog.dismiss()
            repository.delete_transaction(tx.id)  # type: ignore[attr-defined]
            Logger.info("History: deleted transaction id=%s", tx.id)  # type: ignore[attr-defined]
            self._load_transactions()

        self._dialog = MDDialog(
            title="Delete transaction?",
            text=text,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda *_: self._dialog.dismiss() if self._dialog else None,
                ),
                MDFlatButton(
                    text="DELETE",
                    theme_text_color="Custom",
                    text_color=(0.83, 0.18, 0.18, 1),
                    on_release=_do_delete,
                ),
            ],
        )
        self._dialog.open()
