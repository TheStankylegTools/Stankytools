# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

# GitHub Actions and local builds both run from the repository root.
project_root = Path.cwd().resolve()


def include_if_exists(relative_source, destination):
    """Include a file or directory only when it exists in the checkout."""
    source = project_root / relative_source
    if source.exists():
        print(f"Including release data: {source}")
        return [(str(source), destination)]

    print(f"Skipping missing release data: {source}")
    return []


# Only package application-owned assets required at runtime.
# User-imported catalog images are deliberately excluded.
datas = []
datas += include_if_exists(
    "stanky_market/assets/themes",
    "stanky_market/assets/themes",
)
datas += include_if_exists(
    "data/deep_desert_map.png",
    "data",
)
datas += include_if_exists(
    "data/hagga_basin_map.png",
    "data",
)
datas += include_if_exists(
    "assets/catalog/catalog.sqlite3",
    "assets/catalog",
)

datas += include_if_exists(
    "stanky_market/assets/icons",
    "stanky_market/assets/icons",
)

hiddenimports = collect_submodules("PySide6")


a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tests"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="StankyTools",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="StankyTools",
)
