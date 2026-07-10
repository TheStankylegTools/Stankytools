from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPoint, QParallelAnimationGroup, QPropertyAnimation, QTimer, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QLabel, QVBoxLayout, QWidget

from .theme import theme_color_map, theme_manager


class NotificationToast(QWidget):
    def __init__(self, parent: QWidget | None, title: str, message: str = "", kind: str = "info", timeout_ms: int = 3200):
        super().__init__(parent)
        self.kind = (kind or "info").lower()
        self.timeout_ms = timeout_ms
        self.setObjectName("NotificationToast")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.ToolTip)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.opacity = QGraphicsOpacityEffect(self)
        self.opacity.setOpacity(0.0)
        self.setGraphicsEffect(self.opacity)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(42)
        self.shadow.setOffset(0, 0)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 16, 20, 16)
        self.layout.setSpacing(6)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("V3Title")
        self.message_label = QLabel(message)
        self.message_label.setObjectName("V3Muted")
        self.message_label.setWordWrap(True)
        self.layout.addWidget(self.title_label)
        if message:
            self.layout.addWidget(self.message_label)
        self.setMinimumWidth(320)
        self.setMaximumWidth(420)
        theme_manager.theme_changed.connect(lambda *_: self.apply_theme())
        self.apply_theme()

    def apply_theme(self) -> None:
        colors = theme_color_map(theme_manager.theme_key)
        accent = colors.get(self.kind, colors["accent"])
        shadow_color = QColor(accent)
        shadow_color.setAlpha(72)
        self.shadow.setColor(shadow_color)
        self.setStyleSheet(f"""
        QWidget#NotificationToast {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {colors['panel']}, stop:1 {colors['secondary']});
            border-left: 4px solid {accent};
            border-radius: 18px;
        }}
        QLabel#V3Title {{ color: {colors['text']}; font-size: 15px; font-weight: 900; background: transparent; }}
        QLabel#V3Muted {{ color: {colors['muted']}; font-size: 12px; background: transparent; }}
        """)

    def show_near_parent(self) -> None:
        self.adjustSize()
        parent = self.parentWidget()
        if parent is not None:
            geo = parent.geometry()
            end = parent.mapToGlobal(QPoint(geo.width() - self.width() - 28, geo.height() - self.height() - 28))
        else:
            end = QPoint(1200, 760)
        start = QPoint(end.x() + 34, end.y())
        self.move(start)
        self.show()
        self._animate(start, end, 0.0, 1.0, 220)
        QTimer.singleShot(self.timeout_ms, self.dismiss)

    def dismiss(self) -> None:
        end = QPoint(self.x() + 34, self.y())
        self._animate(self.pos(), end, self.opacity.opacity(), 0.0, 240, close_when_done=True)

    def _animate(self, start: QPoint, end: QPoint, opacity_start: float, opacity_end: float, duration: int, close_when_done: bool = False) -> None:
        self.anim_group = QParallelAnimationGroup(self)
        pos_anim = QPropertyAnimation(self, b"pos", self)
        pos_anim.setStartValue(start)
        pos_anim.setEndValue(end)
        pos_anim.setDuration(duration)
        pos_anim.setEasingCurve(QEasingCurve.OutCubic)
        fade_anim = QPropertyAnimation(self.opacity, b"opacity", self)
        fade_anim.setStartValue(opacity_start)
        fade_anim.setEndValue(opacity_end)
        fade_anim.setDuration(duration)
        fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim_group.addAnimation(pos_anim)
        self.anim_group.addAnimation(fade_anim)
        if close_when_done:
            self.anim_group.finished.connect(self.close)
        self.anim_group.start()
