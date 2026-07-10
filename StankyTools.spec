# -*- mode: python ; coding: utf-8 -*-
"""Lean PyInstaller spec for StankyTools.

The old spec used collect_all('PySide6'), which pulls in far more Qt files than
this app needs and can make the portable ZIP hundreds of MB larger. Let
PyInstaller's PySide6 hooks collect the required Qt runtime, then explicitly keep
only the app assets needed by the UI. WebEngine, QML/Quick, and PDF are excluded to keep releases smaller.
"""
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

project = Path.cwd()

def _has_webp_twin(path: Path) -> bool:
    return path.suffix.lower() == ".png" and path.with_suffix(".webp").exists()


def _add_tree(source: Path, dest: str, *, skip_png_twins: bool = False) -> None:
    if not source.exists():
        return
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(source)
        if any(part in {"exports", "__pycache__"} for part in rel.parts):
            continue
        if path.suffix.lower() in {".pyc", ".pyo", ".log", ".tmp", ".bak"}:
            continue
        if skip_png_twins and _has_webp_twin(path):
            continue
        datas.append((str(path), str(Path(dest) / rel.parent)))


datas = []
# Keep releases lean: ship only runtime assets, not generated exports or duplicate
# PNG source copies when matching WebP assets are present.
_add_tree(project / "assets" / "catalog", "assets/catalog")
_add_tree(project / "assets" / "icons", "assets/icons", skip_png_twins=True)
_add_tree(project / "assets" / "ui", "assets/ui", skip_png_twins=True)
_add_tree(project / "stanky_market" / "assets" / "themes", "stanky_market/assets/themes", skip_png_twins=True)

hiddenimports = [
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtNetwork",
    "PySide6.QtSvg",
    "PySide6.QtSvgWidgets",
]
hiddenimports += collect_submodules("tzdata")

excludes = [
    # Development/test stacks that PyInstaller sometimes discovers indirectly.
    "pytest", "unittest", "doctest", "pdb", "pydoc", "tkinter",
    "IPython", "jupyter", "notebook", "matplotlib", "numpy", "pandas",
    "scipy", "setuptools.tests", "pip", "wheel",
    # Unused Qt modules for this app.
    "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtQuickWidgets", "PySide6.QtQuickControls2",
    "PySide6.QtDesigner", "PySide6.QtTest", "PySide6.Qt3DCore",
    "PySide6.QtBluetooth", "PySide6.QtCharts", "PySide6.QtDataVisualization",
    "PySide6.QtLocation", "PySide6.QtNfc",
    "PySide6.QtPdf", "PySide6.QtPdfWidgets", "PySide6.QtPositioning", "PySide6.QtQuick3D",
    "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets",
    "PySide6.QtSensors", "PySide6.QtSerialPort", "PySide6.QtSql",
    "PySide6.QtTextToSpeech", "PySide6.QtUiTools",
    "PySide6.QtWebChannel", "PySide6.QtWebSockets",
    "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets",
    "PySide6.QtWebEngineQuick", "PySide6.QtWebEngineCore",
    "PySide6.QtPdfWidgets",
]

a = Analysis(
    ["main.py"],
    pathex=[str(project)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=2,
)

# PyInstaller's Qt hooks can still collect large optional runtimes through plugin
# metadata. This app uses widget-based Qt, SVG rendering, networking, and SQLite;
# it does not use QML/Quick/PDF/WebEngine/Multimedia/OpenGL scenes in release builds.
_DROP_BINARY_TOKENS = (
    "opengl32sw.dll",
    "qt6quick",
    "qt6qml",
    "qt6qmlmodels",
    "qt6pdf",
    "qt6opengl",
    "qt6multimedia",
    "qt6webengine",
)
a.binaries = [item for item in a.binaries if not any(token in item[0].lower() for token in _DROP_BINARY_TOKENS)]
a.datas = [item for item in a.datas if not any(token in item[0].lower() for token in ("qml", "quick", "pdf"))]
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="StankyTools",
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=True,
    upx=True,
    upx_exclude=["Qt6Core.dll", "Qt6Gui.dll", "Qt6Widgets.dll"],
    name="StankyTools",
)
