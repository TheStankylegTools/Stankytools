from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def app_root() -> Path:
    """Return the writable application folder.

    Development: project folder.
    Frozen one-folder EXE: folder next to StankyTools.exe.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def bundled_root() -> Path:
    """Return where PyInstaller placed bundled read-only resources.

    PyInstaller one-folder builds usually keep --add-data content under
    sys._MEIPASS (often dist/StankyTools/_internal). Source runs use app_root().
    """
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass).resolve()
        internal = app_root() / "_internal"
        if internal.exists():
            return internal
    return app_root()


def resource_path(*parts: str) -> Path:
    """Find a resource in the writable app folder first, then bundled assets."""
    local = app_root().joinpath(*parts)
    if local.exists():
        return local
    bundled = bundled_root().joinpath(*parts)
    if bundled.exists():
        return bundled
    return local


def asset_dir() -> Path:
    return resource_path("assets")


def bundled_data_dir() -> Path:
    return resource_path("data")


def data_dir() -> Path:
    """Return the data folder used by the app.

    In a frozen release, user-writable data should live next to the EXE.
    On first launch, copy bundled seed data there so maps/images/icons/databases
    are available outside PyInstaller's _internal folder.
    """
    target = app_root() / "data"
    if getattr(sys, "frozen", False):
        source = bundled_root() / "data"
        try:
            if source.exists():
                target.mkdir(parents=True, exist_ok=True)
                # Copy only missing files so user data/local caches survive updates.
                shutil.copytree(source, target, dirs_exist_ok=True)
        except Exception:
            # Never prevent launch because seed data could not be copied.
            pass
        return target
    return target


def logs_dir() -> Path:
    path = app_root() / "logs"
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return path
