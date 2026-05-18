from __future__ import annotations

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.logger import Logger

from app.screens.home import HomeScreen
from app.screens.add_transaction import AddTransactionScreen
from app.screens.history import HistoryScreen
from app.screens.categories import CategoriesScreen
from app.screens.login import LoginScreen
from app.screens.settings import SettingsScreen
from app.services.db import init_db
from app.services.settings import get_setting


class ExpenseTrackerApp(MDApp):
    def build(self) -> ScreenManager:
        self.theme_cls.primary_palette = "Teal"

        Logger.info("ExpenseTracker: initializing database")
        init_db()

        self.theme_cls.theme_style = get_setting("theme", "Light") or "Light"

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AddTransactionScreen(name="add_transaction"))
        sm.add_widget(HistoryScreen(name="history"))
        sm.add_widget(CategoriesScreen(name="categories"))
        sm.add_widget(SettingsScreen(name="settings"))
        return sm


if __name__ == "__main__":
    ExpenseTrackerApp().run()
