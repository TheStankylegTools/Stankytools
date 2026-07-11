from __future__ import annotations


def _theme(
    name: str,
    accent: str,
    glow: str,
    accent_soft: str,
    bg: str,
    panel: str,
    panel_hover: str,
    secondary: str,
    *,
    accent_secondary: str | None = None,
    accent_tertiary: str | None = None,
    text: str = "#ECECEC",
    muted: str = "#A7A09A",
    danger: str = "#FF5555",
    danger_soft: str = "rgba(255,85,85,0.20)",
    success: str = "#89FF45",
    success_soft: str = "rgba(137,255,69,0.18)",
    warning: str = "#FFCB45",
    warning_soft: str = "rgba(255,203,69,0.18)",
) -> dict[str, str]:
    accent_secondary = accent_secondary or accent
    accent_tertiary = accent_tertiary or accent
    return {
        "name": name,
        "accent": accent,
        "accent_secondary": accent_secondary,
        "accent_tertiary": accent_tertiary,
        "glow": glow,
        "accent_soft": accent_soft,
        "accent_muted": glow,
        "accent_faint": glow,
        "border": accent_soft,
        "hover": glow,
        "panel": panel,
        "panel_hover": panel_hover,
        "panel_selected": panel_hover,
        "secondary": secondary,
        "sidebar_background": secondary,
        "background": bg,
        "background_secondary": secondary,
        "bg": bg,
        "root_bg": bg,
        "text": text,
        "text_primary": text,
        "text_secondary": muted,
        "muted": muted,
        "danger": danger,
        "danger_soft": danger_soft,
        "success": success,
        "success_soft": success_soft,
        "warning": warning,
        "warning_soft": warning_soft,
        "info": accent_secondary,
    }


THEMES = {
    "dune": _theme(
        "Dune Gold",
        "#FFCB45",
        "rgba(255,203,69,0.18)",
        "rgba(255,203,69,0.58)",
        "#17130D",
        "#241D12",
        "#2D2415",
        "#1D170F",
    ),
    "atreides": _theme(
        "Atreides Green",
        "#89FF45",
        "rgba(137,255,69,0.18)",
        "rgba(137,255,69,0.58)",
        "#101610",
        "#1A2218",
        "#202920",
        "#151D14",
    ),
    "spice": _theme(
        "Spice Purple",
        "#D26CFF",
        "rgba(210,108,255,0.18)",
        "rgba(210,108,255,0.58)",
        "#140F1B",
        "#22172D",
        "#2B1D39",
        "#1B1225",
    ),
    "harkonnen": _theme(
        "Harkonnen Red",
        "#FF5555",
        "rgba(255,85,85,0.18)",
        "rgba(255,85,85,0.58)",
        "#190D0D",
        "#261414",
        "#301818",
        "#211010",
    ),
    "spiced_up": _theme(
        "Spiced Up",
        "#FF00D6",
        "rgba(255,0,214,0.52)",
        "rgba(255,0,214,0.86)",
        "#05000C",
        "rgba(48,0,78,0.88)",
        "rgba(95,0,142,0.94)",
        "#130022",
        accent_secondary="#00F6FF",
        accent_tertiary="#B7FF00",
        text="#FFFFFF",
        muted="#F2D7FF",
        danger="#FF174F",
        danger_soft="rgba(255,23,79,0.36)",
        success="#00FF80",
        success_soft="rgba(0,255,128,0.34)",
        warning="#FFEA00",
        warning_soft="rgba(255,234,0,0.34)",
    ),
}


ALIASES = {
    "gold": "dune",
    "green": "atreides",
    "purple": "spice",
    "red": "harkonnen",
    "spiced": "spiced_up",
    "spiced up": "spiced_up",
}


def normalize_theme_key(theme_key: str | None) -> str:
    key = (theme_key or "dune").strip().lower()
    key = ALIASES.get(key, key)
    return key if key in THEMES else "dune"


def theme_colors(theme_key: str | None) -> dict[str, str]:
    return THEMES[normalize_theme_key(theme_key)]
