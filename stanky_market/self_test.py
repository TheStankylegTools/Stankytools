from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import updater
from .paths import app_root, asset_dir, bundled_root, data_dir
from .release_config import PUBLIC_RELEASE_REPOSITORY, PUBLIC_RELEASES_URL


def _record(checks: list[dict[str, Any]], name: str, ok: bool, detail: str = "") -> None:
    checks.append({"name": name, "ok": bool(ok), "detail": str(detail)})


def _catalog_count(catalog_db: Path) -> int:
    uri = catalog_db.resolve().as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    try:
        tables = [
            str(row[0])
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            ).fetchall()
        ]
        if "companion_items" in tables:
            row = conn.execute("SELECT COUNT(*) FROM companion_items").fetchone()
            return int(row[0] if row else 0)
        for table in tables:
            if not table.replace("_", "").isalnum():
                continue
            row = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()
            count = int(row[0] if row else 0)
            if count > 0:
                return count
        return 0
    finally:
        conn.close()


def run_self_test(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run StankyTools packaged runtime self-test.")
    parser.add_argument("--self-test", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--self-test-marker", default="", help="Optional JSON marker path to write on success or failure.")
    args, _unknown = parser.parse_known_args(argv)

    checks: list[dict[str, Any]] = []
    ok = True
    error = ""

    try:
        from PySide6 import QtCore, QtGui, QtWidgets  # noqa: F401

        _record(checks, "pyside6_import", True, QtCore.qVersion())

        root = app_root()
        bundled = bundled_root()
        assets = asset_dir()
        user_data = data_dir()
        _record(checks, "app_root", root.exists(), root)
        _record(checks, "bundled_root", bundled.exists(), bundled)
        _record(checks, "asset_dir", assets.exists(), assets)
        _record(checks, "data_dir", user_data.exists(), user_data)

        catalog_db = assets / "catalog" / "catalog.sqlite3"
        catalog_exists = catalog_db.exists() and catalog_db.stat().st_size > 1024
        _record(checks, "catalog_db_exists", catalog_exists, catalog_db)
        if catalog_exists:
            count = _catalog_count(catalog_db)
            _record(checks, "catalog_db_readable", count > 0, f"{count} catalog rows")
        else:
            _record(checks, "catalog_db_readable", False, "catalog database missing")

        from . import db
        from .app import MainWindow  # noqa: F401

        conn = db.connect()
        try:
            conn.execute("SELECT 1").fetchone()
            _record(checks, "user_db_open", True, db.DB_PATH)
        finally:
            conn.close()

        release_ok = PUBLIC_RELEASE_REPOSITORY == "TheStankylegTools/StankyTools-Releases"
        updater_ok = updater.GITHUB_OWNER == "TheStankylegTools" and updater.GITHUB_REPO == "StankyTools-Releases"
        _record(checks, "release_repository", release_ok, PUBLIC_RELEASE_REPOSITORY)
        _record(checks, "release_url", PUBLIC_RELEASES_URL.startswith("https://github.com/"), PUBLIC_RELEASES_URL)
        _record(checks, "updater_repository", updater_ok, f"{updater.GITHUB_OWNER}/{updater.GITHUB_REPO}")

        ok = all(item["ok"] for item in checks)
    except Exception as exc:
        ok = False
        error = "".join(traceback.format_exception_only(type(exc), exc)).strip()
        _record(checks, "unexpected_exception", False, error)

    result = {
        "ok": ok,
        "version": updater.APP_VERSION,
        "python": sys.version.split()[0],
        "frozen": bool(getattr(sys, "frozen", False)),
        "executable": sys.executable,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error": error,
        "checks": checks,
    }

    if args.self_test_marker:
        marker = Path(args.self_test_marker)
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(json.dumps(result, indent=2))
    return 0 if ok else 1
