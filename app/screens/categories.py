from __future__ import annotations

import datetime
from decimal import Decimal
from pathlib import Path

from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.screen import MDScreen

from app.services import analytics
from app.widgets.bottom_nav import BottomNavBar  # noqa: F401

Builder.load_file(str(Path(__file__).parent.parent.parent / "assets" / "categories.kv"))


def _fmt(paise: Decimal) -> str:
    return f"₹{paise / 100:,.2f}"


class CategoriesScreen(MDScreen):
    month_label = StringProperty("")

    def on_enter(self) -> None:
        self._month = datetime.date.today().replace(day=1)
        self._refresh()

    def prev_month(self) -> None:
        first = self._month
        self._month = (first - datetime.timedelta(days=1)).replace(day=1)
        self._refresh()

    def next_month(self) -> None:
        first = self._month
        if first.month == 12:
            self._month = first.replace(year=first.year + 1, month=1)
        else:
            self._month = first.replace(month=first.month + 1)
        self._refresh()

    def _refresh(self) -> None:
        self.month_label = self._month.strftime("%B %Y")
        breakdown = analytics.category_breakdown(self._month)

        expenses = [r for r in breakdown if r["kind"] == "expense"]
        incomes = [r for r in breakdown if r["kind"] == "income"]

        self._populate(self.ids.expense_list, self.ids.expense_empty, expenses, (0.83, 0.18, 0.18, 1))
        self._populate(self.ids.income_list, self.ids.income_empty, incomes, (0.18, 0.65, 0.18, 1))

    def _populate(
        self,
        container: MDBoxLayout,
        empty_label: MDLabel,
        rows: list[dict[str, object]],
        bar_color: tuple[float, float, float, float],
    ) -> None:
        container.clear_widgets()

        if not rows:
            empty_label.text = "No data this month."
            return

        empty_label.text = ""
        total = sum(r["total"] for r in rows)  # type: ignore[misc]

        for row in rows:
            pct = float(row["total"] / total * 100) if total else 0  # type: ignore[operator]
            container.add_widget(self._make_row(row, pct, bar_color))

    def _make_row(
        self,
        row: dict[str, object],
        pct: float,
        bar_color: tuple[float, float, float, float],
    ) -> MDBoxLayout:
        outer = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height="56dp",
            spacing="4dp",
        )

        header = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="20dp",
        )
        name_lbl = MDLabel(
            text=str(row["name"]),
            font_style="Body2",
            size_hint_x=1,
            adaptive_height=True,
        )
        amt_lbl = MDLabel(
            text=_fmt(row["total"]),  # type: ignore[arg-type]
            font_style="Body2",
            halign="right",
            size_hint_x=None,
            width="96dp",
            theme_text_color="Custom",
            text_color=bar_color,
            adaptive_height=True,
        )
        header.add_widget(name_lbl)
        header.add_widget(amt_lbl)

        bar = MDProgressBar(
            value=pct,
            size_hint_y=None,
            height="6dp",
        )
        bar.color = bar_color

        outer.add_widget(header)
        outer.add_widget(bar)
        return outer
