from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QSizePolicy


class RoundedButton(QPushButton):
    def __init__(self, text: str = "", parent=None, primary: bool = False):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(42)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.set_primary(primary)

    def set_primary(self, primary: bool = True) -> None:
        self.setObjectName("RoundedPrimaryButton" if primary else "RoundedSecondaryButton")
        self.style().unpolish(self)
        self.style().polish(self)
