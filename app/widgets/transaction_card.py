from __future__ import annotations

from decimal import Decimal

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.card import MDCard

from app.models.transaction import Transaction
from app.models.category import Category

Builder.load_string("""
<TransactionCard>:
    orientation: 'horizontal'
    padding: "12dp"
    spacing: "12dp"
    size_hint_y: None
    height: "68dp"
    radius: [8]
    elevation: 1

    MDBoxLayout:
        orientation: 'vertical'
        spacing: "2dp"
        size_hint_x: 1
        pos_hint: {"center_y": 0.5}
        adaptive_height: True

        MDLabel:
            id: category_label
            text: ""
            font_style: "Body1"
            adaptive_height: True
            shorten: True
            shorten_from: "right"

        MDLabel:
            id: secondary_label
            text: ""
            font_style: "Caption"
            theme_text_color: "Hint"
            adaptive_height: True
            shorten: True
            shorten_from: "right"

    MDLabel:
        id: amount_label
        text: ""
        font_style: "Subtitle1"
        halign: "right"
        size_hint_x: None
        width: "96dp"
        theme_text_color: "Custom"
        text_color: 0, 0.5, 0, 1
        pos_hint: {"center_y": 0.5}
""")

_INCOME_COLOR = (0.18, 0.65, 0.18, 1)
_EXPENSE_COLOR = (0.83, 0.18, 0.18, 1)


class TransactionCard(MDCard):
    def __init__(
        self,
        transaction: Transaction,
        category: Category | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)
        amount = Decimal(transaction.amount) / 100
        sign = "+" if transaction.type == "income" else "-"
        self.ids.amount_label.text = f"{sign}₹{amount:,.2f}"
        self.ids.amount_label.text_color = (
            _INCOME_COLOR if transaction.type == "income" else _EXPENSE_COLOR
        )
        self.ids.category_label.text = (
            category.name if category else f"Category {transaction.category_id}"
        )
        secondary = transaction.note or transaction.date.strftime("%d %b %Y")
        if transaction.note:
            secondary = f"{transaction.date.strftime('%d %b')}  ·  {transaction.note}"
        self.ids.secondary_label.text = secondary
