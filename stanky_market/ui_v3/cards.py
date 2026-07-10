from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Property, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QLabel, QVBoxLayout, QWidget

from .animations import AnimatedCounter
from .theme import theme_color_map, theme_manager


class BaseCard(QFrame):
    card_object_name = "BaseCard"

    def __init__(self, parent: QWidget | None = None, title: str = "", subtitle: str = ""):
        super().__init__(parent)
        self.setObjectName(self.card_object_name)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._hover_strength = 0.0
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(40)
        self._shadow.setOffset(0, 0)
        self.setGraphicsEffect(self._shadow)
        self._hover_animation = QPropertyAnimation(self, b"hoverStrength", self)
        self._hover_animation.setDuration(180)
        self._hover_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.layout_root = QVBoxLayout(self)
        self.layout_root.setContentsMargins(20, 20, 20, 20)
        self.layout_root.setSpacing(22)
        if title:
            self.title_label = QLabel(title)
            self.title_label.setObjectName("V3Title")
            self.layout_root.addWidget(self.title_label)
        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setObjectName("V3Muted")
            self.subtitle_label.setWordWrap(True)
            self.layout_root.addWidget(self.subtitle_label)
        theme_manager.theme_changed.connect(lambda *_: self.apply_theme())
        self.apply_theme()

    def get_hover_strength(self) -> float:
        return self._hover_strength

    def set_hover_strength(self, value: float) -> None:
        self._hover_strength = float(value)
        self._update_shadow()

    hoverStrength = Property(float, get_hover_strength, set_hover_strength)

    def apply_theme(self) -> None:
        self._update_shadow()
        self.style().unpolish(self)
        self.style().polish(self)

    def content_layout(self) -> QVBoxLayout:
        return self.layout_root

    def enterEvent(self, event):
        self._animate_hover(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_hover(0.0)
        super().leaveEvent(event)

    def _animate_hover(self, target: float) -> None:
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover_strength)
        self._hover_animation.setEndValue(target)
        self._hover_animation.start()

    def _update_shadow(self) -> None:
        colors = theme_color_map(theme_manager.theme_key)
        accent = QColor(colors["accent"])
        accent.setAlpha(38 + int(46 * self._hover_strength))
        self._shadow.setColor(accent)
        self._shadow.setBlurRadius(38 + int(8 * self._hover_strength))
        self._shadow.setOffset(0, 0)


class MetricCard(BaseCard):
    card_object_name = "MetricCard"

    def __init__(self, title: str = "", value: int | str = 0, suffix: str = "", subtitle: str = "", parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.label = QLabel(title)
        self.label.setObjectName("V3MetricLabel")
        self.value_label = QLabel("")
        self.value_label.setObjectName("V3MetricValue")
        self.suffix = suffix
        self._formatter: Callable[[int], str] = lambda number: f"{number:,}{self.suffix}"
        self.layout_root.addWidget(self.label)
        self.layout_root.addWidget(self.value_label)
        if subtitle:
            hint = QLabel(subtitle)
            hint.setObjectName("V3Muted")
            hint.setWordWrap(True)
            self.layout_root.addWidget(hint)
        self.counter = AnimatedCounter(parent=self)
        self.counter.value_changed.connect(lambda number: self.value_label.setText(self._formatter(number)))
        self.set_value(value, animate=False)

    def set_value(self, value: int | str, animate: bool = True) -> None:
        try:
            numeric = int(str(value).replace(",", "").strip())
            if animate:
                self.counter.animate_to(numeric, start=0, duration=700)
            else:
                self.counter.set_value(numeric)
        except Exception:
            self.value_label.setText(str(value))


class DashboardCard(BaseCard):
    card_object_name = "DashboardCard"


class GuildCard(BaseCard):
    card_object_name = "GuildCard"


class EventCard(BaseCard):
    card_object_name = "EventCard"

    def __init__(self, parent: QWidget | None = None, title: str = "", subtitle: str = "", status: str = ""):
        super().__init__(parent=parent, title=title, subtitle=subtitle)
        self.status = status
        if status:
            badge = QLabel(status)
            badge.setObjectName("V3Kicker")
            self.layout_root.insertWidget(0, badge)


class CatalogCard(BaseCard):
    card_object_name = "CatalogCard"


class StatisticsCard(BaseCard):
    card_object_name = "StatisticsCard"


class ToolCard(BaseCard):
    card_object_name = "ToolCard"
