from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor


@dataclass(frozen=True)
class Theme:
    key: str
    name: str
    accent: str
    background: str
    panel: str
    secondary: str

    @property
    def text(self) -> str:
        return "#F5F3ED"

    @property
    def muted(self) -> str:
        return "#B9B4AA"


THEMES: dict[str, Theme] = {
    "green": Theme("green", "Green", "#89ff45", "#101610", "#1A2218", "#202920"),
    "gold": Theme("gold", "Gold", "#ffcb45", "#17130d", "#241d12", "#2d2415"),
    "purple": Theme("purple", "Purple", "#d26cff", "#140f1b", "#22172d", "#2b1d39"),
    "red": Theme("red", "Red", "#ff5555", "#190d0d", "#261414", "#301818"),
    "spiced_up": Theme("spiced_up", "Spiced Up", "#FF00D6", "#05000C", "#30004E", "#130022"),
}

LEGACY_THEME_ALIASES = {
    "atreides": "green",
    "dune": "gold",
    "spice": "purple",
    "harkonnen": "red",
    "spiced": "spiced_up",
    "spiced up": "spiced_up",
}


def normalize_theme_key(theme_key: str | None) -> str:
    key = (theme_key or "gold").strip().lower()
    key = LEGACY_THEME_ALIASES.get(key, key)
    return key if key in THEMES else "gold"


def theme_for(theme_key: str | None) -> Theme:
    return THEMES[normalize_theme_key(theme_key)]


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    color = QColor(hex_color)
    return f"rgba({color.red()},{color.green()},{color.blue()},{max(0, min(255, int(alpha * 255)))})"


def mixed_hex(hex_color: str, other: str, ratio: float) -> str:
    a = QColor(hex_color)
    b = QColor(other)
    ratio = max(0.0, min(1.0, ratio))
    inv = 1.0 - ratio
    return "#{:02x}{:02x}{:02x}".format(
        int(a.red() * inv + b.red() * ratio),
        int(a.green() * inv + b.green() * ratio),
        int(a.blue() * inv + b.blue() * ratio),
    )


def theme_color_map(theme_key: str | None) -> dict[str, str]:
    theme = theme_for(theme_key)
    return {
        "name": theme.name,
        "accent": theme.accent,
        "background": theme.background,
        "bg": theme.background,
        "panel": theme.panel,
        "secondary": theme.secondary,
        "panel_hover": mixed_hex(theme.panel, theme.accent, 0.10),
        "text": theme.text,
        "muted": theme.muted,
        "glow": hex_to_rgba(theme.accent, 0.42 if theme.key == "spiced_up" else 0.18),
        "accent_soft": hex_to_rgba(theme.accent, 0.82 if theme.key == "spiced_up" else 0.48),
        "accent_faint": hex_to_rgba(theme.accent, 0.34 if theme.key == "spiced_up" else 0.14),
        "border": hex_to_rgba(theme.accent, 0.58 if theme.key == "spiced_up" else 0.24),
        "hover": hex_to_rgba(theme.accent, 0.44 if theme.key == "spiced_up" else 0.18),
        "shadow": hex_to_rgba(theme.accent, 0.55 if theme.key == "spiced_up" else 0.22),
        "shadow_strong": hex_to_rgba(theme.accent, 0.82 if theme.key == "spiced_up" else 0.38),
        "input": mixed_hex(theme.background, theme.panel, 0.52),
        "primary_text": "#11130d" if theme.key in {"green", "gold"} else "#fff8ff",
        "danger": "#ff5555",
        "warning": "#ffcb45",
        "success": "#89ff45",
        "info": theme.accent,
        "danger_soft": hex_to_rgba("#ff5555", 0.20),
        "success_soft": hex_to_rgba("#89ff45", 0.18),
        "warning_soft": hex_to_rgba("#ffcb45", 0.18),
        "accent_secondary": "#00F6FF" if theme.key == "spiced_up" else theme.accent,
        "accent_tertiary": "#B7FF00" if theme.key == "spiced_up" else theme.accent,
    }


def controls_qss(theme_key: str | None) -> str:
    c = theme_color_map(theme_key)
    primary_hover = mixed_hex(c["accent"], "#ffffff", 0.16)
    primary_down = mixed_hex(c["accent"], "#000000", 0.16)
    secondary_hover = mixed_hex(c["secondary"], c["accent"], 0.16)
    input_focus = hex_to_rgba(c["accent"], 0.72)
    return f"""
    QWidget#Root {{
        background: qradialgradient(cx:0.20, cy:0.08, radius:1.15, fx:0.16, fy:0.04,
            stop:0 {c['accent_faint']}, stop:0.38 {c['background']}, stop:1 {mixed_hex(c['background'], c['secondary'], 0.36)});
    }}
    QMainWindow {{ background: {c['background']}; }}
    QFrame#Panel, QFrame#Card, QFrame#CommandCard, QFrame#PremiumStatCard, QFrame#NewsCard, QFrame#QuickActionCard,
    QFrame#BaseCard, QFrame#MetricCard, QFrame#StatisticsCard, QFrame#CatalogCard, QFrame#GuildCard, QFrame#EventCard,
    QFrame#NotificationCard, QFrame#InputCard {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {mixed_hex(c['panel'], c['accent'], 0.07)}, stop:1 {c['panel']});
        border: none;
        border-radius: 24px;
    }}
    QFrame#Panel:hover, QFrame#Card:hover, QFrame#CommandCard:hover, QFrame#PremiumStatCard:hover, QFrame#NewsCard:hover,
    QFrame#QuickActionCard:hover, QFrame#BaseCard:hover, QFrame#MetricCard:hover, QFrame#StatisticsCard:hover,
    QFrame#CatalogCard:hover, QFrame#GuildCard:hover, QFrame#EventCard:hover, QFrame#NotificationCard:hover,
    QFrame#InputCard:hover {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {mixed_hex(c['panel_hover'], c['accent'], 0.09)}, stop:1 {c['secondary']});
        border: none;
    }}
    QPushButton {{
        background: {c['secondary']};
        border: none;
        border-radius: 16px;
        padding: 10px 16px;
        color: {c['text']};
        font-weight: 850;
        min-height: 24px;
    }}
    QPushButton:hover {{ background: {secondary_hover}; border: none; }}
    QPushButton:pressed {{ background: {mixed_hex(c['secondary'], '#000000', 0.18)}; }}
    QPushButton:disabled {{ background: {mixed_hex(c['secondary'], '#000000', 0.20)}; color: {hex_to_rgba(c['muted'], 0.54)}; }}
    QPushButton#PrimaryButton, QPushButton#GoldButton {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {primary_hover}, stop:1 {c['accent']});
        color: {c['primary_text']};
        border: none;
        font-weight: 950;
    }}
    QPushButton#PrimaryButton:hover, QPushButton#GoldButton:hover {{ background: {primary_hover}; }}
    QPushButton#PrimaryButton:pressed, QPushButton#GoldButton:pressed {{ background: {primary_down}; }}
    QPushButton#DangerButton {{ background: {hex_to_rgba('#ff5555', 0.20)}; color: #FFDAD6; border: none; }}
    QLineEdit, QTextEdit, QSpinBox, QComboBox, QDateTimeEdit, QDateEdit {{
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {mixed_hex(c['input'], '#000000', 0.20)}, stop:1 {c['input']});
        border: 1px solid {hex_to_rgba(c['accent'], 0.18)};
        border-radius: 14px;
        padding: 9px 11px;
        color: {c['text']};
        selection-background-color: {hex_to_rgba(c['accent'], 0.48)};
    }}
    QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus, QDateTimeEdit:focus, QDateEdit:focus {{
        border: 1px solid {input_focus};
        background: {mixed_hex(c['input'], c['accent'], 0.05)};
    }}
    QComboBox::drop-down {{ border: none; width: 30px; }}
    QComboBox QAbstractItemView {{
        background: {c['panel']};
        color: {c['text']};
        border: none;
        border-radius: 14px;
        selection-background-color: {c['accent_faint']};
    }}
    QTabWidget::pane {{ border: none; border-radius: 18px; background: {hex_to_rgba(c['panel'], 0.60)}; }}
    QTabBar::tab {{
        background: {c['secondary']};
        color: {c['muted']};
        padding: 9px 15px;
        border: none;
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
    }}
    QTabBar::tab:selected {{ color: {c['text']}; background: {c['accent_faint']}; }}
    QTableWidget {{
        background: {hex_to_rgba(c['background'], 0.72)};
        alternate-background-color: {hex_to_rgba(c['secondary'], 0.45)};
        gridline-color: {hex_to_rgba(c['accent'], 0.10)};
        border: none;
        border-radius: 18px;
    }}
    QHeaderView::section {{ background: {c['secondary']}; color: {c['accent']}; padding: 10px; border: none; font-weight: 900; }}
    QTableWidget::item:selected {{ background: {c['accent_faint']}; color: #FFFFFF; }}
    QMenu {{ background: {c['panel']}; border: none; border-radius: 14px; padding: 6px; }}
    QMenu::item {{ padding: 9px 26px 9px 14px; color: {c['text']}; }}
    QMenu::item:selected {{ background: {c['hover']}; border-radius: 10px; }}
    QScrollBar:vertical {{ background: {hex_to_rgba(c['background'], 0.42)}; width: 12px; border-radius: 6px; }}
    QScrollBar::handle:vertical {{ background: {hex_to_rgba(c['accent'], 0.40)}; border-radius: 6px; min-height: 36px; }}
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

    def set_theme(self, theme_key: str | None) -> None:
        normalized = normalize_theme_key(theme_key)
        if normalized == self._theme_key:
            return
        self._theme_key = normalized
        self.theme_changed.emit(self._theme_key, self.colors)


theme_manager = ThemeManager()
