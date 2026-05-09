from __future__ import annotations

from pathlib import Path

from kivy.lang import Builder
from kivy.logger import Logger
from kivymd.uix.screen import MDScreen

from app.services import auth

Builder.load_file(str(Path(__file__).parent.parent.parent / "assets" / "login.kv"))

_PIN_LENGTH = 4
_DOT_FILLED = "circle"
_DOT_EMPTY = "circle-outline"

# Modes
_VERIFY = "verify"
_SETUP_ENTER = "setup_enter"
_SETUP_CONFIRM = "setup_confirm"


class LoginScreen(MDScreen):
    def on_enter(self) -> None:
        self._buffer = ""
        self._first_pin = ""
        self._mode = _SETUP_ENTER if not auth.is_pin_set() else _VERIFY
        self._apply_mode_label()
        self._update_dots()

    def append_digit(self, digit: str) -> None:
        if len(self._buffer) >= _PIN_LENGTH:
            return
        self._buffer += digit
        self._update_dots()
        self.ids.error_label.text = ""
        if len(self._buffer) == _PIN_LENGTH:
            self._submit()

    def backspace(self) -> None:
        self._buffer = self._buffer[:-1]
        self._update_dots()
        self.ids.error_label.text = ""

    def _submit(self) -> None:
        if self._mode == _VERIFY:
            self._do_verify()
        elif self._mode == _SETUP_ENTER:
            self._do_setup_enter()
        else:
            self._do_setup_confirm()

    def _do_verify(self) -> None:
        if auth.verify_pin(self._buffer):
            Logger.info("Login: PIN verified, entering app")
            self.manager.current = "home"
        else:
            Logger.warning("Login: wrong PIN attempt")
            self.ids.error_label.text = "Wrong PIN. Try again."
            self._buffer = ""
            self._update_dots()

    def _do_setup_enter(self) -> None:
        self._first_pin = self._buffer
        self._buffer = ""
        self._mode = _SETUP_CONFIRM
        self._apply_mode_label()
        self._update_dots()

    def _do_setup_confirm(self) -> None:
        if self._buffer == self._first_pin:
            auth.set_pin(self._buffer)
            Logger.info("Login: PIN set, entering app")
            self.manager.current = "home"
        else:
            self.ids.error_label.text = "PINs don't match. Start over."
            self._first_pin = ""
            self._buffer = ""
            self._mode = _SETUP_ENTER
            self._apply_mode_label()
            self._update_dots()

    def _apply_mode_label(self) -> None:
        labels = {
            _VERIFY: "Enter your PIN",
            _SETUP_ENTER: "Set a new PIN",
            _SETUP_CONFIRM: "Confirm your PIN",
        }
        self.ids.mode_label.text = labels[self._mode]

    def _update_dots(self) -> None:
        filled = len(self._buffer)
        for i in range(_PIN_LENGTH):
            self.ids[f"dot_{i}"].icon = _DOT_FILLED if i < filled else _DOT_EMPTY
