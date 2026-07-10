from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
import zipfile
from pathlib import Path

DROP_DIRS = {
    ".git", ".github_disabled", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "__pycache__", "release_artifacts", "docs", "Dune-Awakening-API",
    "assets/exports", "data/images", "data/catalog_images", "data/dune.geno.ggitems",
}
DROP_GLOBS = [
    "*.pyc", "*.pyo", "*.log", "*.tmp", "*.bak", "README_SYNC_SPRINT_A*.md",
    "README_COMPANION_*.md", "README_PHASE*.md", "README_*FIX*.md",
    "README_CRAFTING_CALCULATOR_NEXT.md", "RELEASE_NOTES_v0.2.0.md",
    "data/dune_catalog.*", "data/geno_items.*", "data/full_analysis.json",
    "data/images.csv", "data/item_candidates.json", "data/json_payloads.json",
    "data/links.csv", "data/network_requests.csv", "data/scripts.csv",
    "data/catalog_import_report.json", "data/stanky_market.sqlite3", "data/guild_logo.png",
]


def remove_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    elif path.exists():
        path.unlink(missing_ok=True)


def clean_tree(root: Path) -> None:
    for rel in DROP_DIRS:
        remove_path(root / rel)
    for pattern in DROP_GLOBS:
        for path in root.glob(pattern):
            remove_path(path)
    for path in list(root.rglob("__pycache__")):
        remove_path(path)
    for pattern in ("*.pyc", "*.pyo", "*.log", "*.tmp", "*.bak"):
        for path in root.rglob(pattern):
            remove_path(path)


def vacuum_catalog(root: Path) -> None:
    db = root / "assets" / "catalog" / "catalog.sqlite3"
    if not db.exists():
        return
    conn = sqlite3.connect(db)
    try:
        conn.execute("VACUUM")
        conn.execute("PRAGMA optimize")
    finally:
        conn.close()


def zip_tree(root: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(root).as_posix())


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean and compress StankyTools release source tree.")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--zip", dest="zip_path", default="")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    clean_tree(root)
    vacuum_catalog(root)
    if args.zip_path:
        zip_tree(root, Path(args.zip_path).resolve())


if __name__ == "__main__":
    main()
