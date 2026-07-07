from __future__ import annotations

"""Integrated Dune Awakening data engine for StankyTools.

The Gizmo3030/Dune-Awakening-API project exposes ``items_data.json`` through
FastAPI. For StankyTools users, requiring a separate API server is poor UX, so
this module consumes the same data directly and also supports a running local
API during development.

Import order:
1. Running local API: http://127.0.0.1:8000/api/v1/items
2. Local cloned API repo beside/inside StankyTools: Dune-Awakening-API/items_data.json
3. Raw GitHub items_data.json from Gizmo3030/Dune-Awakening-API
4. Cached JSON from the last successful import
"""

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable

from . import db
from .paths import data_dir, resource_path

LOCAL_API_URLS = [
    "http://127.0.0.1:8000/api/v1/items",
    "http://localhost:8000/api/v1/items",
]
RAW_ITEMS_URLS = [
    "https://raw.githubusercontent.com/Gizmo3030/Dune-Awakening-API/main/items_data.json",
    "https://raw.githubusercontent.com/Gizmo3030/Dune-Awakening-API/master/items_data.json",
]
USER_AGENT = "StankyTools/1.0 DuneDataEngine"
CACHE_FILE = "dune_awakening_items_data.json"
DETAILS_FILE = "dune_catalog_details.json"
REPORT_FILE = "dune_data_engine_report.json"

CATEGORY_MAP = {
    "weapon": "Weapons",
    "weapons": "Weapons",
    "garment": "Garments",
    "garments": "Garments",
    "armor": "Garments",
    "building": "Utility",
    "buildings": "Utility",
    "vehicle": "Vehicles",
    "vehicles": "Vehicles",
    "resource": "Raw Resources",
    "resources": "Raw Resources",
    "raw resource": "Raw Resources",
    "raw resources": "Raw Resources",
    "refined resource": "Refined Resources",
    "refined resources": "Refined Resources",
    "component": "Components",
    "components": "Components",
    "fuel": "Fuel",
    "utility": "Utility",
    "utilities": "Utility",
    "augment": "Augmentations",
    "augmentation": "Augmentations",
    "augmentations": "Augmentations",
}


def _engine_dir() -> Path:
    folder = data_dir() / "api_cache"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _cache_path() -> Path:
    return _engine_dir() / CACHE_FILE


def _details_path() -> Path:
    return _engine_dir() / DETAILS_FILE


def _report_path() -> Path:
    return _engine_dir() / REPORT_FILE


def _fetch_json(url: str, timeout: int = 12) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        payload = response.read()
    return json.loads(payload.decode("utf-8"))


def _project_roots() -> list[Path]:
    roots: list[Path] = []
    for candidate in [
        lambda: Path.cwd(),
        lambda: resource_path("."),
        lambda: Path(__file__).resolve().parents[1],
        lambda: Path(__file__).resolve().parents[2],
        lambda: data_dir(),
    ]:
        try:
            roots.append(candidate())
        except Exception:
            pass
    unique: list[Path] = []
    for r in roots:
        try:
            r = r.resolve()
        except Exception:
            pass
        if r not in unique:
            unique.append(r)
    return unique


def _local_items_paths() -> list[Path]:
    candidates: list[Path] = []
    for root in _project_roots():
        candidates.extend([
            root / "items_data.json",
            root / "data" / "items_data.json",
            root / "Dune-Awakening-API" / "items_data.json",
            root.parent / "Dune-Awakening-API" / "items_data.json",
            root / "assets" / "items_data.json",
        ])
    unique: list[Path] = []
    for c in candidates:
        try:
            c = c.resolve()
        except Exception:
            pass
        if c not in unique:
            unique.append(c)
    return unique


def _load_json_file(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        raw = payload
    elif isinstance(payload, dict):
        raw = payload.get("items") or payload.get("data") or payload.get("results") or []
    else:
        raw = []
    return [dict(x) for x in raw if isinstance(x, dict) and str(x.get("name") or x.get("item_name") or "").strip()]


def _load_cache() -> list[dict[str, Any]]:
    path = _cache_path()
    if not path.exists():
        return []
    try:
        return _normalize_items(json.loads(path.read_text(encoding="utf-8")))
    except Exception:
        return []


def _save_cache(items: list[dict[str, Any]], source: str) -> None:
    _cache_path().write_text(
        json.dumps({"source": source, "updated_at": int(time.time()), "items": items}, indent=2),
        encoding="utf-8",
    )


def _write_report(source: str, imported: int = 0, skipped: int = 0, errors: list[str] | None = None) -> None:
    _report_path().write_text(json.dumps({
        "source": source,
        "imported": imported,
        "skipped": skipped,
        "errors": errors or [],
        "updated_at": int(time.time()),
    }, indent=2), encoding="utf-8")


def download_items(progress: Callable[[str], None] | None = None) -> tuple[list[dict[str, Any]], str]:
    """Return Dune item data without requiring a user-run FastAPI server."""
    progress = progress or (lambda _m: None)
    errors: list[str] = []

    # 1) Development convenience: if the user has the API running, consume it.
    for url in LOCAL_API_URLS:
        try:
            progress(f"Checking local Dune API at {url}...")
            items = _normalize_items(_fetch_json(url, timeout=3))
            if items:
                _save_cache(items, url)
                return items, url
            errors.append(f"{url}: no items returned")
        except Exception as exc:
            errors.append(f"{url}: {exc}")

    # 2) If the API repo is cloned beside StankyTools, read its data file directly.
    for path in _local_items_paths():
        try:
            if not path.exists():
                continue
            progress(f"Loading Dune item data from {path}...")
            items = _normalize_items(_load_json_file(path))
            if items:
                _save_cache(items, str(path))
                return items, str(path)
            errors.append(f"{path}: no items returned")
        except Exception as exc:
            errors.append(f"{path}: {exc}")

    # 3) Download raw GitHub JSON. This is the normal no-setup user path.
    for url in RAW_ITEMS_URLS:
        try:
            progress("Downloading Dune item database from GitHub...")
            items = _normalize_items(_fetch_json(url, timeout=20))
            if items:
                _save_cache(items, url)
                return items, url
            errors.append(f"{url}: no items returned")
        except Exception as exc:
            errors.append(f"{url}: {exc}")

    # 4) Offline fallback from a previous successful import.
    cached = _load_cache()
    if cached:
        progress("GitHub unavailable. Using cached Dune item database.")
        return cached, "local Dune data cache"

    _write_report("failed", errors=errors)
    raise RuntimeError("Could not load Dune item data. " + " | ".join(errors[-4:]))


def _pick(d: dict[str, Any], *keys: str, default: str = "") -> str:
    for key in keys:
        val = d.get(key)
        if val is not None and str(val).strip():
            return str(val).strip()
    return default


def _category(item: dict[str, Any]) -> str:
    raw = _pick(item, "category", "item_type", "type", "slot", default="Utility")
    key = raw.lower().replace("_", " ").replace("-", " ").strip()
    compact = key.replace(" ", "")
    for k, v in CATEGORY_MAP.items():
        if key == k or compact == k.replace(" ", "") or k in key:
            return v
    return db.normalize_category(raw)


def _subcategory(item: dict[str, Any]) -> str:
    return _pick(item, "subcategory", "sub_category", "tier", "rarity", default="")


def _source_url(item: dict[str, Any]) -> str:
    item_id = _pick(item, "id", "item_id", default="")
    name = _pick(item, "name", "item_name", "display_name", default="item")
    if item_id:
        return f"dune-data-engine://items/{urllib.parse.quote(str(item_id))}"
    return f"dune-data-engine://items/name/{urllib.parse.quote(name)}"


def _materials_text(item: dict[str, Any], key: str) -> str:
    mats = item.get(key) or []
    if not isinstance(mats, list) or not mats:
        return "None listed"
    parts = []
    for mat in mats:
        if not isinstance(mat, dict):
            continue
        item_name = str(mat.get("item_name") or mat.get("name") or "").strip()
        qty = mat.get("quantity", mat.get("qty", ""))
        if item_name:
            parts.append(f"{item_name} x{qty}" if str(qty).strip() else item_name)
    return "\n".join(parts) if parts else "None listed"


def _save_details(items: list[dict[str, Any]]) -> None:
    by_name: dict[str, Any] = {}
    by_id: dict[str, Any] = {}
    for item in items:
        name = _pick(item, "name", "item_name", "display_name")
        if name:
            by_name[name.lower()] = item
        item_id = _pick(item, "id", "item_id")
        if item_id:
            by_id[str(item_id)] = item
    _details_path().write_text(json.dumps({"by_name": by_name, "by_id": by_id}, indent=2), encoding="utf-8")


def _load_details() -> dict[str, Any]:
    try:
        path = _details_path()
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"by_name": {}, "by_id": {}}


def import_catalog(progress: Callable[[str], None] | None = None, clear_existing: bool = True) -> dict[str, Any]:
    progress = progress or (lambda _m: None)
    items, source = download_items(progress)
    if clear_existing:
        progress("Clearing local catalog before Dune data import...")
        db.clear_local_catalog(skip_seed=True)

    imported = 0
    skipped = 0
    for item in items:
        name = _pick(item, "name", "item_name", "display_name")
        if not name:
            skipped += 1
            continue
        category = _category(item)
        subcategory = _subcategory(item)
        item_type = _pick(item, "item_type", "type", default="Item")
        description = _pick(item, "description", default="")
        power = f"Power: -{_pick(item, 'power_consumption', default='0')} / +{_pick(item, 'power_generation', default='0')}"
        # Keep detail payload in source_url/details cache; catalog table remains simple.
        try:
            db.upsert_catalog_item(
                name=name,
                category=category,
                subcategory=subcategory,
                item_type=item_type,
                source_url=_source_url(item),
                image_path="",
            )
            imported += 1
        except Exception:
            skipped += 1

    _save_details(items)
    db.set_setting("catalog_imported_once", "1")
    db.set_setting("catalog_force_github_reimport", "")
    db.set_setting("catalog_source", source)
    db.set_setting("catalog_last_sync", str(int(time.time())))
    db.set_setting("dune_data_engine_enabled", "1")
    db.set_setting("dune_data_engine_item_count", str(imported))
    _write_report(source, imported=imported, skipped=skipped)
    progress(f"Dune Data Engine import complete: {imported} items from {source}.")
    return {"items": imported, "skipped": skipped, "source": source, "engine": "Dune Data Engine"}


def search_items(name: str) -> list[dict[str, Any]]:
    q = (name or "").strip().lower()
    if not q:
        return []
    items, _source = download_items()
    return [item for item in items if q in str(item.get("name", "")).lower()]


def get_item(item_id: int | str) -> dict[str, Any]:
    wanted = str(item_id)
    details = _load_details()
    if wanted in details.get("by_id", {}):
        return dict(details["by_id"][wanted])
    items, _source = download_items()
    for item in items:
        if str(item.get("id", "")) == wanted:
            return dict(item)
    raise KeyError(f"Item not found: {item_id}")


def get_item_by_name(name: str) -> dict[str, Any] | None:
    key = (name or "").strip().lower()
    if not key:
        return None
    details = _load_details()
    item = details.get("by_name", {}).get(key)
    if item:
        return dict(item)
    try:
        matches = search_items(name)
        for candidate in matches:
            if str(candidate.get("name", "")).strip().lower() == key:
                return dict(candidate)
    except Exception:
        pass
    return None


def format_item_detail(item: dict[str, Any]) -> str:
    if not item:
        return "No Dune Data Engine details found for this item."
    name = _pick(item, "name", "item_name", "display_name", default="Item")
    desc = _pick(item, "description", default="No description listed.")
    item_type = _pick(item, "item_type", "type", default="Item")
    power_consumption = _pick(item, "power_consumption", default="0")
    power_generation = _pick(item, "power_generation", default="0")
    craft = _materials_text(item, "crafting_materials")
    deep = _materials_text(item, "deep_desert_materials")
    return (
        f"{name}\n\n"
        f"Type: {item_type}\n"
        f"Power Consumption: {power_consumption}\n"
        f"Power Generation: {power_generation}\n\n"
        f"Description\n{desc}\n\n"
        f"Crafting Materials\n{craft}\n\n"
        f"Deep Desert Materials\n{deep}"
    )
