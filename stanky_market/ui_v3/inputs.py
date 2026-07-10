from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QLineEdit


class RoundedSearchBox(QLineEdit):
    def __init__(self, placeholder: str = "Search", parent=None):
        super().__init__(parent)
        self.setObjectName("RoundedSearchBox")
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(42)
        self.setClearButtonEnabled(True)


class RoundedComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RoundedComboBox")
        self.setMinimumHeight(42)
