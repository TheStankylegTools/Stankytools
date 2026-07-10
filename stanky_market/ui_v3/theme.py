from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QWidget


@dataclass(frozen=True)
class Theme:
    key: str
    name: str
    background: str
    panel: str
    secondary: str
    accent: str
    text: str = "#F5F3ED"
    muted: str = "#B9B4AA"


THEMES: dict[str, Theme] = {
    "green": Theme("green", "Green", "#101610", "#1A2218", "#202920", "#89FF45"),
    "gold": Theme("gold", "Gold", "#17130D", "#241D12", "#2D2415", "#FFCB45"),
    "purple": Theme("purple", "Purple", "#140F1B", "#22172D", "#2B1D39", "#D26CFF"),
    "red": Theme("red", "Red", "#190D0D", "#261414", "#301818", "#FF5555"),
}

LEGACY_ALIASES = {
    "dune": "gold",
    "atreides": "green",
    "spice": "purple",
    "harkonnen": "red",
}


def normalize_theme_key(theme_key: str | None) -> str:
    key = (theme_key or "gold").strip().lower()
    key = LEGACY_ALIASES.get(key, key)
    return key if key in THEMES else "gold"


def theme_for(theme_key: str | None) -> Theme:
    return THEMES[normalize_theme_key(theme_key)]


def rgba(hex_color: str, opacity: float) -> str:
    color = QColor(hex_color)
    alpha = max(0, min(255, round(opacity * 255)))
    return f"rgba({color.red()},{color.green()},{color.blue()},{alpha})"


def mix(first: str, second: str, ratio: float) -> str:
    a = QColor(first)
    b = QColor(second)
    ratio = max(0.0, min(1.0, ratio))
    inv = 1.0 - ratio
    return "#{:02X}{:02X}{:02X}".format(
        round(a.red() * inv + b.red() * ratio),
        round(a.green() * inv + b.green() * ratio),
        round(a.blue() * inv + b.blue() * ratio),
    )


def theme_color_map(theme_key: str | None) -> dict[str, str]:
    theme = theme_for(theme_key)
    return {
        "key": theme.key,
        "name": theme.name,
        "background": theme.background,
        "panel": theme.panel,
        "secondary": theme.secondary,
        "accent": theme.accent,
        "text": theme.text,
        "muted": theme.muted,
        "panel_hover": mix(theme.panel, theme.accent, 0.08),
        "secondary_hover": mix(theme.secondary, theme.accent, 0.12),
        "accent_hover": mix(theme.accent, "#FFFFFF", 0.14),
        "accent_pressed": mix(theme.accent, "#000000", 0.14),
        "background_glow": rgba(theme.accent, 0.10),
        "card_glow": rgba(theme.accent, 0.20),
        "card_glow_hover": rgba(theme.accent, 0.34),
        "accent_faint": rgba(theme.accent, 0.12),
        "accent_soft": rgba(theme.accent, 0.45),
        "input_bg": mix(theme.background, theme.secondary, 0.66),
        "primary_text": "#11130D" if theme.key in {"green", "gold"} else "#FFF8FF",
        "success": "#89FF45",
        "warning": "#FFCB45",
        "error": "#FF5555",
        "info": theme.accent,
    }


def main_content_qss(theme_key: str | None) -> str:
    c = theme_color_map(theme_key)
    return f"""
    QWidget#ContentShell, QWidget#MainContent, QWidget#DashboardPage, QWidget#CatalogPage, QWidget#GuildPage,
    QWidget#SettingsPage, QWidget#GameManagerPage {{
        background: qradialgradient(cx:0.14, cy:0.04, radius:1.18, fx:0.10, fy:0.02,
            stop:0 {c['background_glow']}, stop:0.40 {c['background']}, stop:1 {mix(c['background'], c['secondary'], 0.34)});
    }}
    QFrame#BaseCard, QFrame#MetricCard, QFrame#DashboardCard, QFrame#GuildCard, QFrame#EventCard,
    QFrame#CatalogCard, QFrame#StatisticsCard, QFrame#ToolCard, QFrame#NotificationToast {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {mix(c['panel'], c['accent'], 0.055)}, stop:1 {c['panel']});
        border: none;
        border-radius: 24px;
    }}
    QFrame#BaseCard:hover, QFrame#MetricCard:hover, QFrame#DashboardCard:hover, QFrame#GuildCard:hover,
    QFrame#EventCard:hover, QFrame#CatalogCard:hover, QFrame#StatisticsCard:hover, QFrame#ToolCard:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {mix(c['panel_hover'], c['accent'], 0.05)}, stop:1 {c['secondary']});
    }}
    QLabel#V3Title {{ color: {c['text']}; font-size: 20px; font-weight: 900; background: transparent; }}
    QLabel#V3Kicker {{ color: {c['accent']}; font-size: 12px; font-weight: 900; background: transparent; }}
    QLabel#V3Muted {{ color: {c['muted']}; font-size: 12px; font-weight: 650; background: transparent; }}
    QLabel#V3MetricValue {{ color: {c['text']}; font-size: 32px; font-weight: 950; background: transparent; }}
    QLabel#V3MetricLabel {{ color: {c['muted']}; font-size: 13px; font-weight: 800; background: transparent; }}
    QPushButton#RoundedButton, QPushButton#RoundedSecondaryButton {{
        background: {c['secondary']};
        color: {c['text']};
        border: none;
        border-radius: 16px;
        padding: 10px 16px;
        font-weight: 850;
        min-height: 24px;
    }}
    QPushButton#RoundedButton:hover, QPushButton#RoundedSecondaryButton:hover {{ background: {c['secondary_hover']}; }}
    QPushButton#RoundedButton:pressed, QPushButton#RoundedSecondaryButton:pressed {{ background: {mix(c['secondary'], '#000000', 0.16)}; }}
    QPushButton#RoundedPrimaryButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {c['accent_hover']}, stop:1 {c['accent']});
        color: {c['primary_text']};
        border: none;
        border-radius: 16px;
        padding: 10px 16px;
        font-weight: 950;
        min-height: 24px;
    }}
    QPushButton#RoundedPrimaryButton:hover {{ background: {c['accent_hover']}; }}
    QPushButton#RoundedPrimaryButton:pressed {{ background: {c['accent_pressed']}; }}
    QLineEdit#RoundedSearchBox, QLineEdit#RoundedInput, QTextEdit#RoundedTextEdit, QComboBox#RoundedComboBox {{
        background: {c['input_bg']};
        color: {c['text']};
        border: 1px solid {rgba(c['accent'], 0.16)};
        border-radius: 14px;
        padding: 9px 12px;
        selection-background-color: {rgba(c['accent'], 0.42)};
    }}
    QLineEdit#RoundedSearchBox:focus, QLineEdit#RoundedInput:focus, QTextEdit#RoundedTextEdit:focus, QComboBox#RoundedComboBox:focus {{
        border: 1px solid {rgba(c['accent'], 0.72)};
    }}
    QComboBox#RoundedComboBox::drop-down {{ border: none; width: 30px; }}
    QComboBox#RoundedComboBox QAbstractItemView {{
        background: {c['panel']};
        color: {c['text']};
        border: none;
        border-radius: 14px;
        selection-background-color: {c['accent_faint']};
    }}
    """


class ThemeManager(QObject):
    theme_changed = Signal(str, dict)

    def __init__(self, theme_key: str | None = None):
        super().__init__()
        self._theme_key = normalize_theme_key(theme_key)

    @property
    def theme_key(self) -> str:
        return self._theme_key

    @property
    def colors(self) -> dict[str, str]:
        return theme_color_map(self._theme_key)

    def set_theme(self, theme_key: str | None, root: QWidget | None = None) -> None:
        normalized = normalize_theme_key(theme_key)
        changed = normalized != self._theme_key
        self._theme_key = normalized
        if root is not None:
            root.setStyleSheet(main_content_qss(self._theme_key))
        app = QApplication.instance()
        if app is not None:
            app.setProperty("stanky_ui_v3_theme", self._theme_key)
        if changed:
            self.theme_changed.emit(self._theme_key, self.colors)


theme_manager = ThemeManager()
