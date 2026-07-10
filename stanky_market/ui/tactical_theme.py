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
) -> dict[str, str]:
    return {
        "name": name,
        "accent": accent,
        "glow": glow,
        "accent_soft": accent_soft,
        "accent_faint": glow,
        "border": accent_soft,
        "hover": glow,
        "panel": panel,
        "panel_hover": panel_hover,
        "secondary": secondary,
        "bg": bg,
        "root_bg": bg,
        "text": "#ECECEC",
        "muted": "#A7A09A",
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
}


def theme_colors(theme_key: str | None) -> dict[str, str]:
    return THEMES.get((theme_key or "dune").strip().lower(), THEMES["dune"])
