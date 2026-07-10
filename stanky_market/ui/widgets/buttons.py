from __future__ import annotations

from PySide6.QtWidgets import QPushButton


class StankButton(QPushButton):
    def __init__(self, text: str, parent=None, primary: bool = False):
        super().__init__(text, parent)
        self.setMinimumHeight(42)
        if primary:
            self.setObjectName("PrimaryButton")


class GoldButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("GoldButton")
        self.setMinimumHeight(42)
