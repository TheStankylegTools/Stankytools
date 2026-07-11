from __future__ import annotations

import json
import time
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QSize, QRectF, QThread, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QImage, QPixmap
from PySide6.QtWidgets import (
    QFileDialog, QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QComboBox,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QCheckBox,
    QInputDialog,
    QTabWidget,
    QProgressBar,
    QSplitter,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
)

from . import store


def _card(title: str, body: str = "", min_h: int = 110) -> QFrame:
    frame = QFrame()
    frame.setObjectName("CommandCard")
    frame.setMinimumHeight(min_h)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 14, 16, 14)
    layout.setSpacing(7)
    t = QLabel(title.upper())
    t.setObjectName("CardTitle")
    layout.addWidget(t)
    if body:
        b = QLabel(body)
        b.setObjectName("CardHint")
        b.setWordWrap(True)
        layout.addWidget(b)
    layout.addStretch(1)
    return frame


def _scroll_content(parent_layout: QVBoxLayout) -> tuple[QScrollArea, QWidget, QVBoxLayout]:
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    inner = QWidget()
    inner_layout = QVBoxLayout(inner)
    inner_layout.setContentsMargins(0, 0, 0, 0)
    inner_layout.setSpacing(12)
    scroll.setWidget(inner)
    parent_layout.addWidget(scroll, 1)
    return scroll, inner, inner_layout




class CompanionImportWorker(QThread):
    progress = Signal(str)
    finished_ok = Signal(dict)
    failed = Signal(str)

    def __init__(self, mode: str, url: str = "", max_pages: int = 40, parent=None):
        super().__init__(parent)
        self.mode = mode
        self.url = url
        self.max_pages = max_pages
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def is_cancelled(self):
        return self._cancelled

    def run(self):
        try:
            if self.mode == "catalog":
                result = store.import_catalog_from_exports(progress=self.progress.emit, reset=True)
            elif self.mode == "recipe_url":
                result = store.import_recipe_url_auto(self.url, progress=self.progress.emit)
            elif self.mode == "recipes_web":
                result = store.import_recipes_from_best_web_sources(progress=self.progress.emit, max_pages=self.max_pages, stop_check=self.is_cancelled)
            else:
                raise ValueError(f"Unknown import mode: {self.mode}")
            self.finished_ok.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))


def build_catalog_page(window) -> QWidget:
    page, layout = window._page_shell("Catalog", "Full Dune item catalog, item details, and crafting calculator.")
    page.setStyleSheet(page.styleSheet() + """
        QFrame#CatalogCompactRow {
            background: rgba(21, 18, 13, 0.72);
            border: 1px solid rgba(214, 174, 90, 0.16);
            border-radius: 8px;
        }
        QFrame#CatalogCompactRow:hover {
            background: rgba(214, 174, 90, 0.10);
            border: 1px solid rgba(214, 174, 90, 0.42);
        }
        QLabel#CatalogCompactName {
            font-size: 14px;
            font-weight: 800;
            color: #F1E3C2;
            letter-spacing: 0.2px;
        }
    """)

    tabs = QTabWidget()
    tabs.setObjectName("CommandTabs")
    layout.addWidget(tabs, 1)

    catalog_tab = QWidget()
    catalog_layout = QVBoxLayout(catalog_tab)
    catalog_layout.setContentsMargins(8, 8, 8, 8)
    catalog_layout.setSpacing(12)

    # Polished summary strip
    stats_row = QHBoxLayout()
    stats_row.setSpacing(10)
    stat_cards = {}
    for key, label in (("items", "Items"), ("recipes", "Recipes"), ("categories", "Categories"), ("images", "Images")):
        card = QFrame()
        card.setObjectName("CommandCard")
        card.setMinimumHeight(74)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 10, 14, 10)
        value = QLabel("-")
        value.setObjectName("HeroMetric")
        caption = QLabel(label.upper())
        caption.setObjectName("MutedText")
        card_layout.addWidget(value)
        card_layout.addWidget(caption)
        stats_row.addWidget(card)
        stat_cards[key] = value
    catalog_layout.addLayout(stats_row)

    controls = QHBoxLayout()
    controls.setSpacing(8)
    search = QLineEdit()
    search.setPlaceholderText("Search items, categories, materials, weapons, vehicles, buildings...")
    category = QComboBox()
    load_exports_btn = QPushButton("Reload Bundled Catalog")
    delete_imported_btn = QPushButton("Delete Imported Items")
    delete_imported_btn.setObjectName("DangerButton")
    controls.addWidget(search, 3)
    controls.addWidget(category, 1)
    controls.addWidget(load_exports_btn)
    controls.addWidget(delete_imported_btn)
    catalog_layout.addLayout(controls)

    notice = QLabel("Search for an item or choose a category. Results show names only. Images, stats, and requirements load in the details panel after double-click.")
    notice.setObjectName("MutedText")
    notice.setWordWrap(True)
    catalog_layout.addWidget(notice)

    import_status = QLabel("Ready")
    import_status.setObjectName("MutedText")
    import_progress = QProgressBar()
    import_progress.setRange(0, 0)
    import_progress.setVisible(False)
    catalog_layout.addWidget(import_status)
    catalog_layout.addWidget(import_progress)

    content_splitter = QSplitter(Qt.Horizontal)
    content_splitter.setObjectName("CatalogDetailSplitter")

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    catalog_inner = QWidget()
    list_layout = QGridLayout(catalog_inner)
    list_layout.setContentsMargins(0, 0, 0, 0)
    list_layout.setHorizontalSpacing(12)
    list_layout.setVerticalSpacing(12)
    scroll.setWidget(catalog_inner)

    detail_panel = QFrame()
    detail_panel.setObjectName("CommandCard")
    detail_panel.setMinimumWidth(330)
    detail_panel.setMaximumWidth(460)
    detail_layout = QVBoxLayout(detail_panel)
    detail_layout.setContentsMargins(16, 16, 16, 16)
    detail_layout.setSpacing(10)

    detail_title = QLabel("Select an Item")
    detail_title.setObjectName("SectionTitle")
    detail_title.setWordWrap(True)
    detail_meta = QLabel("Double-click a catalog result to view details and crafting requirements here.")
    detail_meta.setObjectName("MutedText")
    detail_meta.setWordWrap(True)
    detail_image = QLabel()
    detail_image.setFixedSize(96, 96)
    detail_image.setAlignment(Qt.AlignCenter)
    detail_image.setObjectName("CatalogIcon")
    detail_image.setText("◈")
    detail_requirements = QTextEdit()
    detail_requirements.setReadOnly(True)
    detail_requirements.setObjectName("TextPreview")
    detail_requirements.setPlaceholderText("Item details will appear here.")

    detail_layout.addWidget(detail_title)
    detail_layout.addWidget(detail_meta)
    detail_layout.addWidget(detail_image, 0, Qt.AlignLeft)
    detail_layout.addWidget(detail_requirements, 1)

    content_splitter.addWidget(scroll)
    content_splitter.addWidget(detail_panel)
    content_splitter.setSizes([780, 360])
    catalog_layout.addWidget(content_splitter, 1)

    def update_stats():
        stats = store.catalog_stats()
        for key, value in stat_cards.items():
            value.setText(f"{int(stats.get(key, 0)):,}")

    def refresh_categories():
        current = category.currentText() or "All"
        category.blockSignals(True)
        category.clear()
        category.addItem("All")
        for cat in store.item_categories():
            category.addItem(cat)
        idx = category.findText(current)
        category.setCurrentIndex(idx if idx >= 0 else 0)
        category.blockSignals(False)

    def requirement_lines(row):
        recipes = store.recipes_for_item(row["name"])
        if not recipes:
            return ["No crafting requirement data is available for this item yet."]
        lines = []
        for recipe in recipes:
            lines.append(f"{recipe['station'] or 'Unknown Station'}")
            lines.append(f"Output: {recipe['output_item']} x{recipe['output_qty']}")
            materials = store.recipe_materials(recipe["id"], int(recipe["output_qty"] or 1))
            if materials:
                lines.append("Requires:")
                for mat, amount in materials:
                    lines.append(f"  • {mat}: {amount:g}")
            lines.append("")
        return lines

    def open_item_detail(row):
        detail_title.setText(row["name"])
        meta_parts = [row["category"] or "Item"]
        if "subcategory" in row.keys() and row["subcategory"]:
            meta_parts.append(row["subcategory"])
        detail_meta.setText(
            " • ".join(meta_parts)
            + f"\nTier: {row['tier'] or '-'}    Rarity: {row['rarity'] or '-'}\nStack: {row['stack_size'] or '-'}    Volume: {row['volume'] or '-'}"
        )

        image_path = row["image_path"] if "image_path" in row.keys() else ""
        detail_image.clear()
        detail_image.setText("◈")
        if image_path:
            resolved = store.resolve_catalog_asset_path(image_path)
            pix = QPixmap(resolved)
            if not pix.isNull():
                detail_image.setPixmap(pix.scaled(88, 88, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        detail_image.setVisible(True)

        detail_text = [
            "DESCRIPTION",
            row["notes"] or "No description available.",
            "",
            "CRAFTING REQUIREMENTS",
            *requirement_lines(row),
        ]
        detail_requirements.setPlainText("\n".join(detail_text))

    def make_item_row(row):
        """Compact result row: name only.

        The catalog list is intentionally text-only for speed. Images, tier,
        stack size, rarity, description, and requirements appear only in the
        right-side details panel after double-click.
        """
        item = QFrame()
        item.setObjectName("CatalogCompactRow")
        item.setMinimumHeight(38)
        item.setCursor(Qt.PointingHandCursor)
        outer = QHBoxLayout(item)
        outer.setContentsMargins(12, 6, 12, 6)
        outer.setSpacing(8)

        name = QLabel(row["name"])
        name.setObjectName("CatalogCompactName")
        name.setWordWrap(False)
        outer.addWidget(name, 1)

        item.setToolTip("Double-click to show image, details, and crafting requirements in the side panel")
        item.mouseDoubleClickEvent = lambda event, r=row: open_item_detail(r)
        return item

    def clear_grid():
        while list_layout.count():
            item = list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    render_state = {"rows": [], "index": 0, "token": 0, "craftable": set()}
    render_timer = QTimer(page)
    render_timer.setInterval(1)

    def _render_next_batch():
        token = render_state.get("token", 0)
        rows = render_state.get("rows", [])
        start = int(render_state.get("index", 0))
        if start >= len(rows):
            render_timer.stop()
            import_status.setText(f"Showing {len(rows):,} catalog results. Double-click an item for image/details." if rows else "Ready")
            return
        batch_size = 120
        end = min(start + batch_size, len(rows))
        for index in range(start, end):
            if token != render_state.get("token", 0):
                return
            row = rows[index]
            list_layout.addWidget(make_item_row(row), index, 0)
        render_state["index"] = end
        list_layout.setRowStretch(len(rows) + 1, 1)
        import_status.setText(f"Loading catalog results... {end:,} / {len(rows):,}")

    render_timer.timeout.connect(_render_next_batch)

    refresh_debounce = QTimer(page)
    refresh_debounce.setSingleShot(True)
    refresh_debounce.setInterval(250)

    def refresh():
        render_state["token"] += 1
        render_timer.stop()
        clear_grid()
        update_stats()

        query = search.text().strip()
        selected_category = category.currentText() or "All"
        if not query and selected_category == "All":
            empty = _card(
                "Search or select a category",
                "Type an item name, material, weapon, vehicle, building, or choose a category above to show results.",
                150,
            )
            list_layout.addWidget(empty, 0, 0)
            import_status.setText("Catalog ready. Search or choose a category to display items.")
            return

        import_status.setText("Querying catalog...")
        rows = store.list_items(query, selected_category)
        if not rows:
            empty = _card("No matching items", "Try a different search term or category.", 140)
            list_layout.addWidget(empty, 0, 0)
            import_status.setText("No catalog items matched your search/filter.")
            return
        render_state["rows"] = rows
        render_state["craftable"] = store.craftable_item_names()
        render_state["index"] = 0
        import_status.setText(f"Preparing {len(rows):,} catalog items...")
        render_timer.start()

    def schedule_refresh(*_args):
        refresh_debounce.start()

    refresh_debounce.timeout.connect(refresh)

    def load_exports_catalog():
        answer = QMessageBox.question(
            page,
            "Load Exports Catalog",
            "Reload the optimized bundled catalog database? This runs in the background and replaces the current catalog.",
        )
        if answer != QMessageBox.Yes:
            return

        import_progress.setVisible(True)
        import_progress.setRange(0, 0)
        load_exports_btn.setEnabled(False)
        delete_imported_btn.setEnabled(False)
        import_status.setText("Starting bundled catalog reload...")

        worker = CompanionImportWorker("catalog", parent=page)
        page._catalog_import_worker = worker
        worker.progress.connect(lambda msg: import_status.setText(str(msg)))

        def done(stats):
            import_progress.setVisible(False)
            load_exports_btn.setEnabled(True)
            delete_imported_btn.setEnabled(True)
            import_status.setText(f"Loaded {stats.get('items', 0):,} items and {stats.get('recipes', 0):,} recipes.")
            window.notify("Catalog Loaded", f"{stats.get('items', 0):,} items • {stats.get('recipes', 0):,} recipes", "success")
            refresh_categories()
            refresh()
            craft_tab = tabs.widget(1)
            if hasattr(craft_tab, "refresh_companion_craft"):
                craft_tab.refresh_companion_craft()
            page._catalog_import_worker = None

        def fail(message):
            import_progress.setVisible(False)
            load_exports_btn.setEnabled(True)
            delete_imported_btn.setEnabled(True)
            import_status.setText("Catalog import failed.")
            QMessageBox.warning(page, "Catalog Import Failed", str(message))
            page._catalog_import_worker = None

        worker.finished_ok.connect(done)
        worker.failed.connect(fail)
        worker.start()

    def delete_imported_items():
        answer = QMessageBox.question(
            page,
            "Delete Imported Items",
            "Delete all imported catalog items and recipe data so you can start fresh?",
        )
        if answer != QMessageBox.Yes:
            return
        stats = store.clear_imported_catalog_items(include_recipes=True)
        import_status.setText(f"Deleted {stats.get('items', 0):,} items and {stats.get('recipes', 0):,} recipes.")
        refresh_categories()
        refresh()
        craft_tab = tabs.widget(1)
        if hasattr(craft_tab, "refresh_companion_craft"):
            craft_tab.refresh_companion_craft()
        window.notify("Catalog Cleared", "Imported catalog and recipe data deleted.", "success")

    search.textChanged.connect(schedule_refresh)
    category.currentTextChanged.connect(schedule_refresh)
    load_exports_btn.clicked.connect(load_exports_catalog)
    delete_imported_btn.clicked.connect(delete_imported_items)

    refresh_categories()
    refresh()
    catalog_tab.refresh_companion_catalog = refresh

    craft_tab = _strip_embedded_banner(build_crafting_page(window))
    tabs.addTab(catalog_tab, "Catalog")
    tabs.addTab(craft_tab, "Craft")
    page.refresh_companion_catalog = refresh
    return page

def build_crafting_page(window) -> QWidget:
    page, layout = window._page_shell("Craft", "Crafting calculator, saved projects, and Discord material requests.")

    header = QLabel("Add crafted items, set quantities, and StankyTools will total the required materials. Import recipes one item at a time from a recipe page when data is missing.")
    header.setObjectName("MutedText")
    header.setWordWrap(True)
    layout.addWidget(header)

    target_row = QHBoxLayout()
    search = QLineEdit()
    search.setPlaceholderText("Type an item name to search recipes...")
    qty = QSpinBox()
    qty.setRange(1, 999999)
    qty.setValue(1)
    add_btn = QPushButton("Add to Calculator")
    target_row.addWidget(search, 1)
    target_row.addWidget(QLabel("Qty"))
    target_row.addWidget(qty)
    target_row.addWidget(add_btn)
    layout.addLayout(target_row)

    search_results = QListWidget()
    search_results.setObjectName("CatalogResultsList")
    search_results.setMinimumHeight(120)
    search_results.setMaximumHeight(190)
    search_results.setAlternatingRowColors(True)
    layout.addWidget(search_results)

    button_row = QHBoxLayout()
    copy_btn = QPushButton("Copy Discord Request")
    material_btn = QPushButton("View Material List")
    save_set_btn = QPushButton("Save Set")
    load_set_btn = QPushButton("Load Set")
    clear_btn = QPushButton("Clear")
    import_url_btn = QPushButton("Import Recipe URL")
    button_row.addWidget(copy_btn)
    button_row.addWidget(material_btn)
    button_row.addWidget(save_set_btn)
    button_row.addWidget(load_set_btn)
    button_row.addWidget(clear_btn)
    button_row.addStretch(1)
    button_row.addWidget(import_url_btn)
    layout.addLayout(button_row)

    import_status = QLabel("Ready — recipe imports are now on-demand so the app stays fast.")
    import_status.setObjectName("MutedText")
    import_progress = QProgressBar()
    import_progress.setRange(0, 0)
    import_progress.setVisible(False)
    layout.addWidget(import_status)
    layout.addWidget(import_progress)

    summary = QLabel("No crafting targets added yet.")
    summary.setObjectName("MutedText")
    summary.setWordWrap(True)
    layout.addWidget(summary)

    content = QHBoxLayout()
    content.setSpacing(12)
    layout.addLayout(content, 1)

    left_scroll = QScrollArea()
    left_scroll.setWidgetResizable(True)
    left_scroll.setFrameShape(QFrame.NoFrame)
    left_inner = QWidget()
    target_layout = QVBoxLayout(left_inner)
    target_layout.setContentsMargins(0, 0, 0, 0)
    target_layout.setSpacing(10)
    left_scroll.setWidget(left_inner)
    content.addWidget(left_scroll, 1)

    right_scroll = QScrollArea()
    right_scroll.setWidgetResizable(True)
    right_scroll.setFrameShape(QFrame.NoFrame)
    right_inner = QWidget()
    material_layout = QVBoxLayout(right_inner)
    material_layout.setContentsMargins(0, 0, 0, 0)
    material_layout.setSpacing(10)
    right_scroll.setWidget(right_inner)
    content.addWidget(right_scroll, 1)

    recipes: list = []
    targets: list[dict] = []

    def reload_recipe_choices():
        nonlocal recipes
        query = search.text().strip()
        recipes = store.craftable_recipes(query) if query else []
        search_results.clear()
        if not query:
            search_results.addItem("Start typing to search craftable items...")
            return
        if not recipes:
            search_results.addItem("No matching recipes found. Import a recipe URL if the item is missing.")
            return
        for recipe in recipes[:75]:
            station = recipe["station"] or "Unknown"
            out_qty = int(recipe["output_qty"] or 1)
            item = QListWidgetItem(f"{recipe['output_item']} x{out_qty}  •  {station}")
            item.setData(Qt.UserRole, int(recipe["id"]))
            search_results.addItem(item)
        if search_results.count():
            search_results.setCurrentRow(0)

    def clear_layout(box):
        while box.count():
            item = box.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def current_recipe_label(recipe_id: int) -> str:
        for recipe in store.craftable_recipes(""):
            if int(recipe["id"]) == int(recipe_id):
                return f"{recipe['output_item']}  •  {recipe['station'] or 'Unknown'}"
        return f"Recipe #{recipe_id}"

    def remove_target(index: int):
        if 0 <= index < len(targets):
            targets.pop(index)
            refresh_calculator()

    def change_target_qty(index: int, value: int):
        if 0 <= index < len(targets):
            targets[index]["qty"] = max(1, int(value))
            refresh_calculator()

    def refresh_calculator():
        clear_layout(target_layout)
        clear_layout(material_layout)
        outputs, materials = store.aggregate_recipe_materials(targets)
        if not outputs:
            summary.setText("No crafting targets added yet. Search for a craftable item, choose quantity, then click Add to Calculator.")
            target_layout.addWidget(_card("No crafting targets", "Add an item above to begin calculating."))
            material_layout.addWidget(_card("No materials yet", "Materials appear here once you add craftable items."))
            target_layout.addStretch(1)
            material_layout.addStretch(1)
            return
        summary.setText(f"{len(outputs)} crafting target(s) • {len(materials)} material type(s)")
        for index, output in enumerate(outputs):
            card = QFrame()
            card.setObjectName("CommandCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(14, 12, 14, 12)
            title = QLabel(output["output_item"].upper())
            title.setObjectName("CardTitle")
            body = QLabel(f"Station: {output['station']}\nRecipe: {output['name']}")
            body.setObjectName("CardHint")
            body.setWordWrap(True)
            row = QHBoxLayout()
            row.addWidget(QLabel("Qty"))
            spin = QSpinBox()
            spin.setRange(1, 999999)
            spin.setValue(int(output["qty"]))
            spin.valueChanged.connect(lambda value, i=index: change_target_qty(i, value))
            remove_btn = QPushButton("Remove")
            remove_btn.clicked.connect(lambda checked=False, i=index: remove_target(i))
            row.addWidget(spin)
            row.addWidget(remove_btn)
            row.addStretch(1)
            card_layout.addWidget(title)
            card_layout.addWidget(body)
            card_layout.addLayout(row)
            target_layout.addWidget(card)
        for material, amount in materials:
            material_layout.addWidget(_card(material, f"Total needed: {amount:g}"))
        target_layout.addStretch(1)
        material_layout.addStretch(1)

    def add_selected_recipe():
        item = search_results.currentItem()
        recipe_id = item.data(Qt.UserRole) if item is not None else None
        if recipe_id is None:
            QMessageBox.information(page, "No Recipe", "Search for an item and select a matching recipe first. Import a recipe URL if the item is missing.")
            return
        targets.append({"recipe_id": int(recipe_id), "qty": int(qty.value())})
        refresh_calculator()

    def discord_text() -> str:
        outputs, materials = store.aggregate_recipe_materials(targets)
        if not outputs:
            return ""
        lines = ["**StankyTools Crafting Request**", "", "Crafting Targets:"]
        for output in outputs:
            lines.append(f"- {output['output_item']} x{output['qty']} ({output['station']})")
        lines += ["", "Materials Needed:"]
        lines += [f"- {name}: {amount:g}" for name, amount in materials]
        return "\n".join(lines)

    def copy_discord():
        text = discord_text()
        if not text:
            QMessageBox.information(page, "Nothing to Copy", "Add at least one crafting target first.")
            return
        page.window().clipboard().setText(text)
        window.notify("Copied", "Crafting request copied for Discord.", "success")

    def show_material_list():
        QMessageBox.information(page, "Material List", discord_text() or "Add at least one crafting target first.")

    def save_set():
        if not targets:
            QMessageBox.information(page, "Save Set", "Add at least one crafting target first.")
            return
        name, ok = QInputDialog.getText(page, "Save Crafting Set", "Set name:")
        if not ok or not name.strip():
            return
        try:
            store.save_crafting_set(name.strip(), targets)
            window.notify("Crafting Set Saved", name.strip(), "success")
        except Exception as exc:
            QMessageBox.warning(page, "Save Failed", str(exc))

    def load_set():
        sets = store.list_crafting_sets()
        if not sets:
            QMessageBox.information(page, "Load Set", "No saved crafting sets yet.")
            return
        labels = [f"{row['name']}" for row in sets]
        choice, ok = QInputDialog.getItem(page, "Load Crafting Set", "Choose a saved set:", labels, 0, False)
        if not ok:
            return
        selected = sets[labels.index(choice)]
        targets.clear()
        targets.extend(store.load_crafting_set(int(selected["id"])))
        refresh_calculator()
        window.notify("Crafting Set Loaded", selected["name"], "success")

    def clear_targets():
        targets.clear()
        refresh_calculator()

    def set_import_busy(is_busy: bool, status: str = ""):
        import_progress.setVisible(is_busy)
        import_status.setText(status or ("Importing recipe..." if is_busy else "Ready"))
        import_url_btn.setEnabled(not is_busy)
        add_btn.setEnabled(not is_busy)

    def import_recipe_url():
        url, ok = QInputDialog.getText(page, "Import Recipe URL", "Paste an Awakening Wiki, Questlog, gaming.tools, or item recipe page URL:")
        if not ok or not url.strip():
            return
        set_import_busy(True, "Importing selected recipe page...")
        worker = CompanionImportWorker("recipe_url", url=url.strip(), max_pages=1, parent=page)
        page._recipe_import_worker = worker
        worker.progress.connect(import_status.setText)
        def done(stats):
            set_import_busy(False, f"Done. Imported {stats.get('recipes', 0)} recipe(s).")
            reload_recipe_choices()
            refresh_calculator()
            window.notify("Recipe Imported", f"Imported {stats.get('recipes', 0)} recipe(s).", "success")
        def fail(message):
            set_import_busy(False, "Recipe import failed")
            QMessageBox.warning(page, "Recipe Import Failed", f"Could not import recipe:\n{message}")
        worker.finished_ok.connect(done)
        worker.failed.connect(fail)
        worker.start()

    search.textChanged.connect(reload_recipe_choices)
    search_results.itemDoubleClicked.connect(lambda item: add_selected_recipe())
    add_btn.clicked.connect(add_selected_recipe)
    copy_btn.clicked.connect(copy_discord)
    material_btn.clicked.connect(show_material_list)
    save_set_btn.clicked.connect(save_set)
    load_set_btn.clicked.connect(load_set)
    clear_btn.clicked.connect(clear_targets)
    import_url_btn.clicked.connect(import_recipe_url)

    reload_recipe_choices()
    refresh_calculator()
    return page


class BlueprintGrid(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(430)
        self.setMouseTracking(True)
        self.tool = "foundation"
        self.cells: dict[tuple[int, int], str] = {}
        self.grid_size = 26

    def set_tool(self, tool: str):
        self.tool = tool

    def mousePressEvent(self, event):
        x = int(event.position().x() // self.grid_size)
        y = int(event.position().y() // self.grid_size)
        key = (x, y)
        if self.tool == "erase" or event.button() == Qt.RightButton:
            self.cells.pop(key, None)
        else:
            self.cells[key] = self.tool
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(18, 15, 12))
        pen = QPen(QColor(92, 76, 48), 1)
        painter.setPen(pen)
        for x in range(0, self.width(), self.grid_size):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), self.grid_size):
            painter.drawLine(0, y, self.width(), y)
        colors = {
            "foundation": QColor(166, 135, 74),
            "wall": QColor(118, 104, 86),
            "door": QColor(80, 150, 90),
            "stairs": QColor(130, 95, 170),
            "station": QColor(210, 150, 60),
            "storage": QColor(70, 120, 180),
            "power": QColor(220, 190, 80),
            "note": QColor(190, 80, 70),
        }
        for (x, y), tool in self.cells.items():
            rect = QRectF(x * self.grid_size + 2, y * self.grid_size + 2, self.grid_size - 4, self.grid_size - 4)
            painter.fillRect(rect, QBrush(colors.get(tool, QColor(140, 140, 140))))
            painter.setPen(QPen(QColor(10, 8, 5), 1))
            painter.drawRect(rect)

    def to_json(self) -> str:
        return json.dumps({"cells": [{"x": x, "y": y, "tool": t} for (x, y), t in self.cells.items()]})

    def export_png(self, path: str):
        image = QImage(self.size(), QImage.Format_ARGB32)
        self.render(image)
        image.save(path)


def build_blueprints_page(window) -> QWidget:
    store.seed_samples()
    page, layout = window._page_shell("Blueprints", "Blueprint library from the blueprint market concept.")

    top = QHBoxLayout()
    search = QLineEdit()
    search.setPlaceholderText("Search blueprints by name, base type, tags, or notes...")
    import_btn = QPushButton("Import Blueprints from Web")
    top.addWidget(search, 2)
    top.addWidget(import_btn)
    layout.addLayout(top)

    notice = QLabel("The old 2D build planner has been removed. This page is now a blueprint browser/library. It is ready for blueprint-market style web imports, favorites, tags, previews, and material notes.")
    notice.setObjectName("MutedText")
    notice.setWordWrap(True)
    layout.addWidget(notice)

    _, _, bp_layout = _scroll_content(layout)

    def open_blueprint(row):
        lines = [row["name"], "", f"Type: {row['base_type'] or '-'}", f"Players: {row['players_recommended'] or '-'}", f"Tags: {row['tags'] or '-'}", "", "Power Notes:", row["power_notes"] or "-", "", "Material Notes:", row["material_notes"] or "-"]
        QMessageBox.information(page, "Blueprint Details", "\n".join(lines))

    def make_blueprint_card(row):
        body = f"{row['base_type'] or '-'}  •  Players: {row['players_recommended'] or '-'}\nTags: {row['tags'] or '-'}\n{row['material_notes'] or ''}\nDouble-click for details."
        card = _card(row["name"], body, 135)
        card.setToolTip("Double-click to view blueprint details")
        card.mouseDoubleClickEvent = lambda event, r=row: open_blueprint(r)
        return card

    def refresh_blueprints():
        while bp_layout.count():
            item = bp_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        rows = store.list_blueprints(search.text())
        if not rows:
            bp_layout.addWidget(_card("No blueprints", "Import blueprints from web."))
        for row in rows:
            bp_layout.addWidget(make_blueprint_card(row))
        bp_layout.addStretch(1)

    def import_blueprints():
        try:
            stats = store.import_blueprints_from_web(progress=lambda msg: window.notify("Blueprint Import", msg, "info"))
            refresh_blueprints()
            window.notify("Blueprints Imported", f"Imported {stats.get('blueprints', 0)} blueprint records. Errors: {stats.get('errors', 0)}", "success")
        except Exception as exc:
            QMessageBox.warning(page, "Blueprint Import Failed", f"Could not import blueprints from web:\n{exc}")

    def load_samples():
        store.seed_samples(force=True)
        refresh_blueprints()
        window.notify("Sample Blueprints Ready", "Sample blueprints have been loaded.", "success")

    search.textChanged.connect(refresh_blueprints)
    import_btn.clicked.connect(import_blueprints)
    refresh_blueprints()
    return page


def build_building_page(window) -> QWidget:
    return build_blueprints_page(window)

def build_timers_page(window) -> QWidget:
    """Build one unified timer console with five lab timers and Sandstorm."""
    page, layout = window._page_shell(
        "Timers",
        "Track five laboratories and the next sandstorm from one console.",
    )

    timer_console = QFrame()
    timer_console.setObjectName("UnifiedTimerConsole")
    console_layout = QVBoxLayout(timer_console)
    console_layout.setContentsMargins(24, 22, 24, 24)
    console_layout.setSpacing(16)

    console_header = QHBoxLayout()
    title = QLabel("TIMER CONSOLE")
    title.setObjectName("SectionTitle")
    subtitle = QLabel("Five labs and one sandstorm timer")
    subtitle.setObjectName("MutedText")
    console_header.addWidget(title)
    console_header.addStretch(1)
    console_header.addWidget(subtitle)
    console_layout.addLayout(console_header)

    divider = QFrame()
    divider.setFrameShape(QFrame.HLine)
    divider.setObjectName("TimerDivider")
    console_layout.addWidget(divider)

    rows_container = QWidget()
    rows_layout = QVBoxLayout(rows_container)
    rows_layout.setContentsMargins(0, 0, 0, 0)
    rows_layout.setSpacing(10)
    console_layout.addWidget(rows_container)

    active: dict[str, float] = {}
    now = time.time()
    for persisted_key in ["lab_1", "lab_2", "lab_3", "lab_4", "lab_5", "sandstorm"]:
        try:
            persisted_end = float(store.get_setting(f"timer_{persisted_key}_end", "0") or 0)
        except Exception:
            persisted_end = 0
        if persisted_end > now:
            active[persisted_key] = persisted_end
    status_labels: dict[str, QLabel] = {}
    duration_inputs: dict[str, QSpinBox] = {}
    name_inputs: dict[str, QLineEdit] = {}

    def fmt(seconds: int) -> str:
        seconds = max(0, int(seconds))
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def saved_minutes(key: str, default: int) -> int:
        try:
            return max(
                1,
                min(
                    1440,
                    int(store.get_setting(f"timer_{key}_minutes", str(default)) or default),
                ),
            )
        except Exception:
            return default

    def saved_name(key: str, default: str) -> str:
        value = store.get_setting(f"timer_{key}_name", default)
        return str(value or default)

    def save_timer(key: str) -> None:
        duration = duration_inputs.get(key)
        name = name_inputs.get(key)
        if duration is not None:
            store.set_setting(f"timer_{key}_minutes", str(duration.value()))
        if name is not None:
            fallback = "Sandstorm" if key == "sandstorm" else f"Laboratory {key.split('_')[-1]}"
            store.set_setting(
                f"timer_{key}_name",
                name.text().strip() or fallback,
            )

    def start_timer(key: str) -> None:
        duration = duration_inputs.get(key)
        if duration is None:
            return
        save_timer(key)
        seconds = int(duration.value()) * 60
        active[key] = time.time() + seconds
        store.set_setting(f"timer_{key}_end", str(active[key]))
        status = status_labels.get(key)
        if status is not None:
            try:
                status.setText(fmt(seconds))
                status.setProperty("running", True)
                status.style().unpolish(status)
                status.style().polish(status)
            except RuntimeError:
                status_labels.pop(key, None)

        name = name_inputs.get(key)
        timer_name = name.text().strip() if name is not None else "Timer"
        refresh_dashboard = getattr(window, "_refresh_dashboard_active_timers", None)
        if callable(refresh_dashboard):
            refresh_dashboard()
        window.notify(
            "Timer Started",
            f"{timer_name or 'Timer'} is now running.",
            "success",
        )

    def reset_timer(key: str) -> None:
        active.pop(key, None)
        store.set_setting(f"timer_{key}_end", "0")
        status = status_labels.get(key)
        refresh_dashboard = getattr(window, "_refresh_dashboard_active_timers", None)
        if callable(refresh_dashboard):
            refresh_dashboard()
        if status is not None:
            try:
                status.setText("Ready")
                status.setProperty("running", False)
                status.style().unpolish(status)
                status.style().polish(status)
            except RuntimeError:
                status_labels.pop(key, None)

    def add_timer_row(
        key: str,
        default_name: str,
        default_minutes: int,
        *,
        sandstorm: bool = False,
    ) -> None:
        row = QFrame()
        row.setObjectName("SandstormTimerRow" if sandstorm else "LabTimerRow")
        row.setProperty("timerType", "sandstorm" if sandstorm else "lab")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(16, 12, 16, 12)
        row_layout.setSpacing(12)

        name = QLineEdit(saved_name(key, default_name))
        name.setObjectName("TimerNameInput")
        name.setMaxLength(40)
        name.setMinimumWidth(190)
        name.editingFinished.connect(lambda k=key: save_timer(k))

        duration = QSpinBox()
        duration.setObjectName("TimerDurationInput")
        duration.setRange(1, 1440)
        duration.setSuffix(" min")
        duration.setValue(saved_minutes(key, default_minutes))
        duration.setMinimumWidth(112)
        duration.valueChanged.connect(lambda value, k=key: save_timer(k))

        status = QLabel("Ready")
        status.setObjectName("TimerRowStatus")
        status.setAlignment(Qt.AlignCenter)
        status.setMinimumWidth(112)
        status.setProperty("running", False)

        start_button = QPushButton("Start")
        start_button.setObjectName("PrimaryButton")
        start_button.setMinimumWidth(90)
        reset_button = QPushButton("Reset")
        reset_button.setMinimumWidth(90)

        start_button.clicked.connect(lambda checked=False, k=key: start_timer(k))
        reset_button.clicked.connect(lambda checked=False, k=key: reset_timer(k))

        row_layout.addWidget(name, 1)
        row_layout.addWidget(duration)
        row_layout.addWidget(status)
        row_layout.addWidget(start_button)
        row_layout.addWidget(reset_button)

        rows_layout.addWidget(row)
        name_inputs[key] = name
        duration_inputs[key] = duration
        status_labels[key] = status

    for slot in range(1, 6):
        add_timer_row(
            f"lab_{slot}",
            f"Laboratory {slot}",
            45,
        )

    add_timer_row(
        "sandstorm",
        "Sandstorm",
        30,
        sandstorm=True,
    )

    rows_layout.addStretch(1)
    layout.addWidget(timer_console, 1)

    for active_key, active_end in active.items():
        active_label = status_labels.get(active_key)
        if active_label is not None:
            active_label.setText(fmt(int(active_end - time.time())))
            active_label.setProperty("running", True)
            active_label.style().unpolish(active_label)
            active_label.style().polish(active_label)

    def tick() -> None:
        now = time.time()
        for key, end_time in list(active.items()):
            remaining = int(end_time - now)
            label = status_labels.get(key)
            if label is not None:
                try:
                    label.setText(fmt(remaining))
                except RuntimeError:
                    status_labels.pop(key, None)

            if remaining <= 0:
                active.pop(key, None)
                store.set_setting(f"timer_{key}_end", "0")
                if label is not None:
                    try:
                        label.setText("Ready")
                        label.setProperty("running", False)
                        label.style().unpolish(label)
                        label.style().polish(label)
                    except RuntimeError:
                        status_labels.pop(key, None)

                name = name_inputs.get(key)
                timer_name = name.text().strip() if name is not None else "Timer"
                window.notify(
                    "Timer Complete",
                    f"{timer_name or 'Timer'} is ready.",
                    "info",
                )

    timer = QTimer(page)
    timer.setInterval(1000)
    timer.timeout.connect(tick)
    timer.start()

    page._companion_timer = timer
    page._timer_active = active
    page._timer_status_labels = status_labels
    page._timer_duration_inputs = duration_inputs
    page._timer_name_inputs = name_inputs
    return page



def _strip_embedded_banner(tab_page: QWidget) -> QWidget:
    """Remove the page-shell hero/banner when a full page is embedded inside Game Manager tabs."""
    lay = tab_page.layout()
    if lay and lay.count():
        first = lay.itemAt(0).widget()
        if first is not None and first.__class__.__name__ == "HeroFrame":
            item = lay.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(10)
    return tab_page

def _action_card(title: str, body: str, buttons: list[QPushButton], min_h: int = 145) -> QFrame:
    frame = _card(title, body, min_h)
    row = QHBoxLayout()
    row.setSpacing(8)
    row.addStretch(1)
    for btn in buttons:
        row.addWidget(btn)
    frame.layout().addLayout(row)
    return frame

def build_game_manager_page(window) -> QWidget:
    page, layout = window._page_shell("Game Manager", "Set your Dune Awakening game/config folder.")

    card = QFrame()
    card.setObjectName("CommandCard")
    card_layout = QVBoxLayout(card)
    card_layout.setContentsMargins(16, 14, 16, 14)
    card_layout.setSpacing(10)

    title = QLabel("CONFIG FOLDER")
    title.setObjectName("CardTitle")
    card_layout.addWidget(title)

    game_path = QLineEdit(store.get_setting("game_folder", "") or store.detect_dune_game_folder())
    game_path.setPlaceholderText("Dune Awakening game folder or config folder")
    browse = QPushButton("Browse")
    auto_detect = QPushButton("Auto Detect")
    save = QPushButton("Save Path")
    open_btn = QPushButton("Open Folder")

    row = QHBoxLayout()
    row.addWidget(game_path, 1)
    row.addWidget(browse)
    row.addWidget(auto_detect)
    row.addWidget(save)
    row.addWidget(open_btn)
    card_layout.addLayout(row)

    layout.addWidget(card)

    tweaks_card = QFrame()
    tweaks_card.setObjectName("CommandCard")
    tweaks_layout = QVBoxLayout(tweaks_card)
    tweaks_layout.setContentsMargins(16, 14, 16, 14)
    tweaks_layout.setSpacing(10)
    tweaks_title = QLabel("ENGINE TWEAKS")
    tweaks_title.setObjectName("CardTitle")
    tweaks_layout.addWidget(tweaks_title)
    tweaks_hint = QLabel("Select only the tweaks you want. StankyTools creates a backup before editing Engine.ini.")
    tweaks_hint.setObjectName("MutedText")
    tweaks_hint.setWordWrap(True)
    tweaks_layout.addWidget(tweaks_hint)

    tweak_checks = {}
    tweak_grid = QGridLayout()
    tweak_grid.setHorizontalSpacing(16)
    tweak_grid.setVerticalSpacing(8)
    row_index = 0
    for i, (key, data) in enumerate(store.ENGINE_TWEAKS.items()):
        label = data[0] if isinstance(data, tuple) else str(key)
        chk = QCheckBox(label)
        chk.setObjectName("ThemeCheck")
        tweak_checks[key] = chk
        tweak_grid.addWidget(chk, i // 2, i % 2)
        row_index = max(row_index, i // 2)
    start_col = len(store.ENGINE_TWEAKS) % 2
    row_index = len(store.ENGINE_TWEAKS) // 2
    for j, (key, data) in enumerate(getattr(store, "LAUNCH_TWEAKS", {}).items()):
        label = data[0] if isinstance(data, tuple) else str(key)
        chk = QCheckBox(label)
        chk.setObjectName("ThemeCheck")
        chk.setToolTip("Copies the recommended Steam launch option: -nostartupscreen")
        tweak_checks[key] = chk
        n = len(store.ENGINE_TWEAKS) + j
        tweak_grid.addWidget(chk, n // 2, n % 2)
    tweaks_layout.addLayout(tweak_grid)

    tweak_status = QLabel("Select tweaks, then apply them to your selected config folder.")
    tweak_status.setObjectName("MutedText")
    tweaks_layout.addWidget(tweak_status)

    tweak_buttons = QHBoxLayout()
    apply_tweaks_btn = QPushButton("Apply Selected Tweaks")
    apply_tweaks_btn.setObjectName("PrimaryButton")
    remove_tweaks_btn = QPushButton("Remove StankyTools Tweaks")
    remove_tweaks_btn.setObjectName("PrimaryButton")
    tweak_buttons.addWidget(apply_tweaks_btn)
    tweak_buttons.addWidget(remove_tweaks_btn)
    tweak_buttons.addStretch(1)
    tweaks_layout.addLayout(tweak_buttons)
    layout.addWidget(tweaks_card)
    layout.addStretch(1)

    def auto_detect_path():
        detected = store.detect_dune_game_folder()
        if detected:
            game_path.setText(detected)
            store.set_setting("game_folder", detected)
            window.notify("Game Folder Detected", detected, "success")
        else:
            QMessageBox.information(page, "Auto Detect", "Dune Awakening was not found automatically. Please browse to the game or config folder.")

    def browse_path():
        path = QFileDialog.getExistingDirectory(page, "Select Dune Awakening or Config Folder", game_path.text() or str(Path.home()))
        if path:
            game_path.setText(path)

    def save_path():
        store.set_setting("game_folder", game_path.text().strip())
        window.notify("Game Folder Saved", game_path.text().strip() or "Path cleared.", "success")

    def open_folder():
        import os
        path = game_path.text().strip()
        if not path:
            QMessageBox.information(page, "Open Folder", "Set a game/config folder first.")
            return
        os.startfile(path) if hasattr(os, "startfile") else None

    def selected_tweaks():
        return [key for key, chk in tweak_checks.items() if chk.isChecked()]

    def apply_selected_tweaks():
        path = game_path.text().strip()
        if not path:
            QMessageBox.information(page, "Engine Tweaks", "Set a game/config folder first.")
            return
        try:
            result = store.apply_engine_tweaks(path, selected_tweaks())
            launch_options = result.get("launch_options", []) or []
            if launch_options:
                QApplication.clipboard().setText(" ".join(launch_options))
            message = "Applied: " + ", ".join(result.get("tweaks", []))
            if launch_options:
                message += " | Launch option copied: " + " ".join(launch_options)
            tweak_status.setText(message)
            window.notify("Tweaks Applied", f"Applied {result.get('count', 0)} tweak(s).", "success")
        except Exception as exc:
            QMessageBox.warning(page, "Tweaks Failed", str(exc))

    def remove_stankytools_tweaks():
        path = game_path.text().strip()
        if not path:
            QMessageBox.information(page, "Engine Tweaks", "Set a game/config folder first.")
            return
        try:
            result = store.clear_engine_tweaks(path)
            tweak_status.setText(f"Removed {result.get('removed', 0)} StankyTools tweak block(s).")
            window.notify("Tweaks Removed", "StankyTools tweak blocks removed.", "success")
        except Exception as exc:
            QMessageBox.warning(page, "Remove Failed", str(exc))

    browse.clicked.connect(browse_path)
    auto_detect.clicked.connect(auto_detect_path)
    save.clicked.connect(save_path)
    open_btn.clicked.connect(open_folder)
    apply_tweaks_btn.clicked.connect(apply_selected_tweaks)
    remove_tweaks_btn.clicked.connect(remove_stankytools_tweaks)
    return page
