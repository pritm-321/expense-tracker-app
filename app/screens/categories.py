from __future__ import annotations

import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField

from app.services import analytics, repository
from app.utils.format import format_money
from app.widgets.bottom_nav import BottomNavBar  # noqa: F401

_OVER_COLOR = (0.83, 0.18, 0.18, 1)

Builder.load_file(str(Path(__file__).parent.parent.parent / "assets" / "categories.kv"))


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
        self._budgets = {b.category_id: b.amount for b in repository.get_budgets()}

        expenses = [r for r in breakdown if r["kind"] == "expense"]
        incomes = [r for r in breakdown if r["kind"] == "income"]

        self._populate(
            self.ids.expense_list, self.ids.expense_empty, expenses,
            (0.83, 0.18, 0.18, 1), budgetable=True,
        )
        self._populate(
            self.ids.income_list, self.ids.income_empty, incomes,
            (0.18, 0.65, 0.18, 1), budgetable=False,
        )

    def _populate(
        self,
        container: MDBoxLayout,
        empty_label: MDLabel,
        rows: list[dict[str, object]],
        bar_color: tuple[float, float, float, float],
        budgetable: bool,
    ) -> None:
        container.clear_widgets()

        if not rows:
            empty_label.text = "No data this month."
            return

        empty_label.text = ""
        total = sum(r["total"] for r in rows)  # type: ignore[misc]

        for row in rows:
            share = float(row["total"] / total * 100) if total else 0  # type: ignore[operator]
            container.add_widget(self._make_row(row, share, bar_color, budgetable))

    def _make_row(
        self,
        row: dict[str, object],
        share_pct: float,
        bar_color: tuple[float, float, float, float],
        budgetable: bool,
    ) -> MDBoxLayout:
        cat_id = int(row["category_id"])  # type: ignore[call-overload]
        spent = row["total"]
        budget = self._budgets.get(cat_id) if budgetable else None

        if budget:
            over = spent > budget  # type: ignore[operator]
            bar_value = min(float(spent / budget * 100), 100.0)  # type: ignore[operator]
            row_color = _OVER_COLOR if over else bar_color
            amount_text = f"{format_money(spent)} / {format_money(budget)}"  # type: ignore[arg-type]
        else:
            over = False
            bar_value = share_pct
            row_color = bar_color
            amount_text = format_money(spent)  # type: ignore[arg-type]

        outer = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height="56dp",
            spacing="4dp",
        )

        header = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="28dp",
        )
        name_lbl = MDLabel(
            text=str(row["name"]),
            font_style="Body2",
            size_hint_x=1,
            adaptive_height=True,
        )
        amt_lbl = MDLabel(
            text=amount_text,
            font_style="Body2",
            halign="right",
            size_hint_x=None,
            width="160dp",
            theme_text_color="Custom",
            text_color=row_color,
            adaptive_height=True,
        )
        header.add_widget(name_lbl)
        header.add_widget(amt_lbl)

        if budgetable:
            budget_btn = MDIconButton(
                icon="wallet-outline",
                size_hint=(None, None),
                size=("28dp", "28dp"),
                theme_icon_color="Custom",
                icon_color=(0.4, 0.4, 0.4, 1),
            )
            budget_btn.bind(
                on_release=lambda *_, c=cat_id, n=str(row["name"]): self._budget_dialog(c, n)
            )
            header.add_widget(budget_btn)

        bar = MDProgressBar(
            value=bar_value,
            size_hint_y=None,
            height="6dp",
        )
        bar.color = row_color

        outer.add_widget(header)
        outer.add_widget(bar)
        return outer

    def _budget_dialog(self, category_id: int, name: str) -> None:
        field = MDTextField(
            hint_text=f"Monthly budget for {name}",
            input_filter="float",
            text=(
                f"{Decimal(self._budgets[category_id]) / 100:.2f}"
                if category_id in self._budgets
                else ""
            ),
        )

        def _save(*_: object) -> None:
            raw = field.text.strip()
            try:
                rupees = Decimal(raw) if raw else Decimal(0)
            except InvalidOperation:
                field.error = True
                return
            if rupees <= 0:
                repository.delete_budget(category_id)
                Logger.info("Categories: cleared budget cat=%s", category_id)
            else:
                repository.set_budget(category_id, int(rupees * 100))
                Logger.info("Categories: set budget cat=%s", category_id)
            self._dialog.dismiss()
            self._refresh()

        self._dialog = MDDialog(
            title="Set budget",
            type="custom",
            content_cls=field,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda *_: self._dialog.dismiss(),
                ),
                MDFlatButton(
                    text="SAVE",
                    theme_text_color="Custom",
                    text_color=(0.13, 0.59, 0.95, 1),
                    on_release=_save,
                ),
            ],
        )
        self._dialog.open()
