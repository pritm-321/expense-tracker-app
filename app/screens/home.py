from __future__ import annotations

import datetime
from pathlib import Path

from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen

from app.services import analytics, repository
from app.utils.format import format_money
from app.widgets.bottom_nav import BottomNavBar  # noqa: F401 — registers KV rule

Builder.load_file(str(Path(__file__).parent.parent.parent / "assets" / "home.kv"))

_RECENT_LIMIT = 10


class HomeScreen(MDScreen):
    month_label = StringProperty("")

    def on_enter(self) -> None:
        today = datetime.date.today()
        self.month_label = today.strftime("%B %Y")
        self._refresh(today)

    def _refresh(self, month: datetime.date) -> None:
        self._load_summary(month)
        self._load_recent(month)

    def _load_summary(self, month: datetime.date) -> None:
        totals = analytics.monthly_totals(month)
        self.ids.income_amount.text = format_money(totals["income"])
        self.ids.expense_amount.text = format_money(totals["expense"])

        net = totals["net"]
        self.ids.net_amount.text = format_money(net)
        self.ids.net_amount.theme_text_color = "Custom"
        self.ids.net_amount.text_color = (
            (0.18, 0.65, 0.18, 1) if net >= 0 else (0.83, 0.18, 0.18, 1)
        )

    def _load_recent(self, month: datetime.date) -> None:
        from app.widgets.transaction_card import TransactionCard

        container = self.ids.transaction_list
        container.clear_widgets()

        txs = repository.get_transactions(month=month)[:_RECENT_LIMIT]
        if not txs:
            container.add_widget(
                MDLabel(
                    text="No transactions this month.",
                    halign="center",
                    theme_text_color="Hint",
                    size_hint_y=None,
                    height="48dp",
                )
            )
            return

        cat_map = {c.id: c for c in repository.get_categories()}
        for tx in txs:
            container.add_widget(
                TransactionCard(
                    transaction=tx,
                    category=cat_map.get(tx.category_id),
                )
            )

    def go_to_add(self) -> None:
        self.manager.current = "add_transaction"
