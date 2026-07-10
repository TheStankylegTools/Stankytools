from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Property, Qt
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QLabel, QVBoxLayout, QHBoxLayout, QWidget

from ..theme_manager import theme_color_map


class BaseCard(QFrame):
    def __init__(self, parent: QWidget | None = None, theme_key: str | None = None, object_name: str = "BaseCard"):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._theme_key = theme_key
        self._hover_strength = 0.0
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(40)
        self._shadow.setOffset(0, 0)
        self.setGraphicsEffect(self._shadow)
        self._hover_anim = QPropertyAnimation(self, b"hoverStrength", self)
        self._hover_anim.setDuration(170)
        self._hover_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.apply_theme(theme_key)

    def make_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(22)
        return layout

    def apply_theme(self, theme_key: str | None = None) -> None:
        if theme_key is not None:
            self._theme_key = theme_key
        self._update_shadow()

    def getHoverStrength(self) -> float:
        return self._hover_strength

    def setHoverStrength(self, value: float) -> None:
        self._hover_strength = float(value)
        self._update_shadow()

    hoverStrength = Property(float, getHoverStrength, setHoverStrength)

    def enterEvent(self, event):
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._hover_strength)
        self._hover_anim.setEndValue(1.0)
        self._hover_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._hover_strength)
        self._hover_anim.setEndValue(0.0)
        self._hover_anim.start()
        super().leaveEvent(event)

    def _update_shadow(self) -> None:
        colors = theme_color_map(self._theme_key)
        accent = QColor(colors["accent"])
        accent.setAlpha(42 + int(44 * self._hover_strength))
        self._shadow.setColor(accent)
        self._shadow.setBlurRadius(40 + int(12 * self._hover_strength))
        self._shadow.setOffset(0, 0)


class MetricCard(BaseCard):
    def __init__(self, title: str = "", value: str = "", hint: str = "", parent: QWidget | None = None):
        super().__init__(parent, object_name="MetricCard")
        layout = self.make_layout()
        self.title = QLabel(title)
        self.title.setObjectName("CardTitle")
        self.value = QLabel(value)
        self.value.setObjectName("CardValue")
        layout.addWidget(self.title)
        layout.addWidget(self.value)
        if hint:
            self.hint = QLabel(hint)
            self.hint.setObjectName("CardHint")
            self.hint.setWordWrap(True)
            layout.addWidget(self.hint)


class StatisticsCard(MetricCard):
    def __init__(self, title: str = "", value: str = "", hint: str = "", parent: QWidget | None = None):
        super().__init__(title, value, hint, parent)
        self.setObjectName("StatisticsCard")


class CatalogCard(BaseCard):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent, object_name="CatalogCard")


class GuildCard(BaseCard):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent, object_name="GuildCard")


class EventCard(BaseCard):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent, object_name="EventCard")


class NotificationCard(BaseCard):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent, object_name="NotificationCard")


class InputCard(BaseCard):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent, object_name="InputCard")


class CommandCard(BaseCard):
    def __init__(self, title: str = "", subtitle: str = "", content: QWidget | None = None, parent: QWidget | None = None):
        super().__init__(parent, object_name="CommandCard")
        layout = self.make_layout()
        if title:
            label = QLabel(title.upper())
            label.setObjectName("SectionTitle")
            layout.addWidget(label)
        if subtitle:
            sub = QLabel(subtitle)
            sub.setObjectName("MicroLabel")
            sub.setWordWrap(True)
            layout.addWidget(sub)
        if content is not None:
            layout.addWidget(content, 1)


class StatusPill(QFrame):
    def __init__(self, label: str, value: str, tone: str = "gold", parent: QWidget | None = None, icon_path: str | None = None):
        super().__init__(parent)
        self.setObjectName("MiniStatus")
        row = QHBoxLayout(self)
        row.setContentsMargins(10, 7, 10, 7)
        row.setSpacing(8)
        if icon_path:
            icon = QLabel()
            pix = QPixmap(icon_path)
            if not pix.isNull():
                wide_badge = pix.width() > pix.height() * 1.8
                target_w = 210 if wide_badge else 32
                target_h = 64 if wide_badge else 32
                icon.setPixmap(pix.scaled(target_w, target_h, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                icon.setFixedSize(target_w + 6, target_h + 6)
                icon.setAlignment(Qt.AlignCenter)
                row.addWidget(icon)
            else:
                name = QLabel(label.upper())
                name.setObjectName("MicroLabel")
                row.addWidget(name)
        else:
            name = QLabel(label.upper())
            name.setObjectName("MicroLabel")
            row.addWidget(name)
        val = QLabel(value)
        self.value = val
        val.setObjectName("VersionPill" if tone == "gold" else "MicroLabel")
        val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row.addStretch()
        row.addWidget(val)
