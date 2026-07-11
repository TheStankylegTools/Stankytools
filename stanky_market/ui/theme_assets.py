from __future__ import annotations

from pathlib import Path

from ..paths import asset_dir

PACKAGE_ASSET_ROOT = Path(__file__).resolve().parents[1] / "assets"
SHARED_ASSET_ROOT = asset_dir()
THEME_KEYS = {"dune", "atreides", "harkonnen", "spice", "spiced_up"}


def normalize_theme(theme: str | None) -> str:
    key = (theme or "dune").strip().lower()
    return key if key in THEME_KEYS else "dune"


def asset_path(*parts: str) -> Path:
    return SHARED_ASSET_ROOT.joinpath(*parts)


def package_asset_path(*parts: str) -> Path:
    return PACKAGE_ASSET_ROOT.joinpath(*parts)


def first_existing(*paths: Path) -> Path:
    for path in paths:
        if path.exists():
            return path
    return paths[0]


def mascot_path(theme: str | None) -> Path:
    key = normalize_theme(theme)
    return first_existing(
        package_asset_path("themes", key, "mascot.webp"),
        package_asset_path("themes", key, "mascot.png"),
        asset_path("images", f"{key}_mascot_logo.webp"),
        asset_path("images", f"{key}_mascot_logo.png"),
        asset_path("images", "stankytools_mascot_logo.webp"),
        asset_path("images", "stankytools_mascot_logo.png"),
    )


def banner_path(theme: str | None, page: str = "dashboard") -> Path:
    """Return the active theme banner.

    StankyTools uses one uniform banner per theme across the app so page
    switches and theme changes never resize or crop the artwork.
    """
    key = normalize_theme(theme)
    theme_base = package_asset_path("themes", key)
    return first_existing(
        theme_base / "banner.webp",
        theme_base / "banner.png",
        asset_path("backgrounds", f"{key}_theme_banner.webp"),
        asset_path("backgrounds", f"{key}_theme_banner.png"),
        asset_path("backgrounds", "dashboard_banner.webp"),
        asset_path("backgrounds", "dashboard_banner.png"),
    )


def nav_background_path(theme: str | None) -> Path:
    key = normalize_theme(theme)
    theme_base = package_asset_path("themes", key)
    candidates = [
        asset_path("backgrounds", f"{key}_nav_background.svg"),
        asset_path("backgrounds", f"{key}_nav_background.png"),
        asset_path("backgrounds", f"{key}_nav_background.webp"),
        theme_base / "nav_background.svg",
        theme_base / "nav_background.webp",
        theme_base / "nav_background.png",
        asset_path("backgrounds", f"{key}_sidebar_texture.webp"),
        asset_path("backgrounds", f"{key}_sidebar_texture.png"),
        asset_path("backgrounds", "sidebar_texture.webp"),
        asset_path("backgrounds", "sidebar_texture.png"),
        asset_path("ui", "sidebar_texture.webp"),
    ]
    return first_existing(*candidates)


def sidebar_background_path(theme: str | None) -> Path:
    key = normalize_theme(theme)
    theme_base = package_asset_path("themes", key)
    return first_existing(
        theme_base / "sidebar_bg.webp",
        theme_base / "sidebar_bg.png",
        asset_path("backgrounds", f"{key}_sidebar_bg.webp"),
        asset_path("backgrounds", f"{key}_sidebar_bg.png"),
        nav_background_path(theme),
    )


def page_background_path(theme: str | None) -> Path:
    key = normalize_theme(theme)
    theme_base = package_asset_path("themes", key)
    return first_existing(
        theme_base / "page_bg.webp",
        theme_base / "page_bg.png",
        asset_path("backgrounds", f"{key}_page_bg.webp"),
        asset_path("backgrounds", f"{key}_page_bg.png"),
        theme_base / "banner.webp",
        theme_base / "banner.png",
    )
