from __future__ import annotations

from PySide6.QtCore import QObject, Property, QPropertyAnimation, QEasingCurve, Signal


class AnimatedCounter(QObject):
    value_changed = Signal(int)
    finished = Signal()

    def __init__(self, start: int = 0, end: int = 0, duration: int = 700, parent: QObject | None = None):
        super().__init__(parent)
        self._value = int(start)
        self._animation = QPropertyAnimation(self, b"value", self)
        self._animation.setDuration(duration)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        self._animation.finished.connect(self.finished.emit)
        if start != end:
            self.animate_to(end, start=start, duration=duration)

    def get_value(self) -> int:
        return self._value

    def set_value(self, value: int) -> None:
        self._value = int(value)
        self.value_changed.emit(self._value)

    value = Property(int, get_value, set_value)

    def animate_to(self, end: int, start: int | None = None, duration: int = 700) -> None:
        self._animation.stop()
        if start is None:
            start = self._value
        self._animation.setDuration(duration)
        self._animation.setStartValue(int(start))
        self._animation.setEndValue(int(end))
        self._animation.start()
