from __future__ import annotations

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.logger import Logger

from app.screens.home import HomeScreen
from app.screens.add_transaction import AddTransactionScreen
from app.screens.history import HistoryScreen
from app.screens.categories import CategoriesScreen
from app.screens.login import LoginScreen
from app.services.db import init_db


class ExpenseTrackerApp(MDApp):
    def build(self) -> ScreenManager:
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"

        Logger.info("ExpenseTracker: initializing database")
        init_db()

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AddTransactionScreen(name="add_transaction"))
        sm.add_widget(HistoryScreen(name="history"))
        sm.add_widget(CategoriesScreen(name="categories"))
        return sm


if __name__ == "__main__":
    ExpenseTrackerApp().run()
