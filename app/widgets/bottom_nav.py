from __future__ import annotations

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout

Builder.load_string("""
<BottomNavBar>:
    size_hint_y: None
    height: "56dp"
    md_bg_color: 0.97, 0.97, 0.97, 1

    MDIconButton:
        icon: "home" if root.active_tab == "home" else "home-outline"
        theme_icon_color: "Custom"
        icon_color: app.theme_cls.primary_color if root.active_tab == "home" else (0.5, 0.5, 0.5, 1)
        pos_hint: {"center_y": 0.5}
        on_release: root.switch_to("home")

    MDIconButton:
        icon: "history"
        theme_icon_color: "Custom"
        icon_color: app.theme_cls.primary_color if root.active_tab == "history" else (0.5, 0.5, 0.5, 1)
        pos_hint: {"center_y": 0.5}
        on_release: root.switch_to("history")

    MDIconButton:
        icon: "shape" if root.active_tab == "categories" else "shape-outline"
        theme_icon_color: "Custom"
        icon_color: app.theme_cls.primary_color if root.active_tab == "categories" else (0.5, 0.5, 0.5, 1)
        pos_hint: {"center_y": 0.5}
        on_release: root.switch_to("categories")
""")


class BottomNavBar(MDBoxLayout):
    active_tab = StringProperty("home")

    def switch_to(self, screen_name: str) -> None:
        App.get_running_app().root.current = screen_name
