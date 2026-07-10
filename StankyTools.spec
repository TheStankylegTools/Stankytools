# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules
from pathlib import Path

project_root = Path.cwd()

datas = [
    ("stanky_market/assets/themes", "stanky_market/assets/themes"),
    ("stanky_market/assets/icons", "stanky_market/assets/icons"),
    ("data/deep_desert_map.png", "data"),
    ("data/hagga_basin_map.png", "data"),
]

catalog_db = project_root / "assets" / "catalog" / "catalog.sqlite3"
if catalog_db.exists():
    datas.append((str(catalog_db), "assets/catalog"))

hiddenimports = collect_submodules("PySide6")

a = Analysis(
    ["main.py"],
    pathex=[],
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
