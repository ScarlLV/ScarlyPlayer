# ui/library_page.py
import os
import time
from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QFileDialog, QMenu, QMessageBox, QLineEdit, QComboBox
)
from core.i18n import tr, translator
from core.settings import settings

VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v", ".flv", ".wmv", ".ts"}
NEW_THRESHOLD_SEC = 24 * 3600


class LibraryPage(QWidget):
    playRequested = Signal(str)
    playAllRequested = Signal(list)

    def __init__(self):
        super().__init__()
        self._items_data = {}
        self._load_data()
        self._build_ui()
        self._refresh()
        translator().languageChanged.connect(self.retranslate)
        self.setAcceptDrops(True)

    def _load_data(self):
        self._paths = []
        self._items_data = {}
        for item in settings().get_library():
            path = item.get("path")
            if path and Path(path).exists():
                self._paths.append(path)
                self._items_data[path] = item

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)
        self.setStyleSheet("background: transparent;")

        header = QHBoxLayout()
        self._title = QLabel(tr("library.title"))
        self._title.setStyleSheet("font-size:20px; font-weight:700; color:#F5F5F7;")
        header.addWidget(self._title)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Поиск...")
        self.search_bar.setStyleSheet(
            "background:rgba(31,31,38,240); border:1px solid #2A2A33; "
            "border-radius:8px; padding:6px; color:white;"
        )
        self.search_bar.textChanged.connect(self._filter_list)
        header.addWidget(self.search_bar, 1)
        root.addLayout(header)

        toolbar = QHBoxLayout()
        self.sort_combo = QComboBox()
        self.sort_combo.setStyleSheet("background:rgba(31,31,38,240); border-radius:8px; padding:4px; color:white;")
        self.sort_combo.addItems([tr("library.sort.date"), tr("library.sort.name")])
        self.sort_combo.currentIndexChanged.connect(self._refresh)
        toolbar.addWidget(self.sort_combo)

        self.filter_combo = QComboBox()
        self.filter_combo.setStyleSheet("background:rgba(31,31,38,240); border-radius:8px; padding:4px; color:white;")
        self.filter_combo.addItems([tr("library.filter.all"), tr("library.filter.recent"), tr("library.filter.tagged")])
        self.filter_combo.currentIndexChanged.connect(self._filter_list)
        toolbar.addWidget(self.filter_combo)

        self.btn_add = QPushButton(tr("library.add"))
        self.btn_add.setObjectName("CtrlBtn")
        self.btn_add.clicked.connect(self._add_files)
        toolbar.addWidget(self.btn_add)

        self.btn_play_all = QPushButton("▶ Играть всё")
        self.btn_play_all.setObjectName("CtrlBtn")
        self.btn_play_all.clicked.connect(self._play_all)
        toolbar.addWidget(self.btn_play_all)

        self.btn_clear = QPushButton(tr("library.clear"))
        self.btn_clear.setObjectName("CtrlBtn")
        self.btn_clear.clicked.connect(self._clear_all)
        toolbar.addWidget(self.btn_clear)
        root.addLayout(toolbar)

        self.list = QListWidget()
        self.list.setStyleSheet("""
            QListWidget { background: rgba(23, 23, 28, 200); border: 1px solid #2A2A33;
                          border-radius: 12px; padding: 6px; }
            QListWidget::item { padding: 10px 12px; border-radius: 8px; color: #F5F5F7; }
            QListWidget::item:selected { background: #E53935; color: white; }
            QListWidget::item:hover { background: rgba(42, 42, 51, 200); }
        """)
        self.list.itemDoubleClicked.connect(self._on_double_click)
        self.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self._on_context_menu)
        root.addWidget(self.list, 1)

        self.empty_label = QLabel(tr("library.empty"))
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #A0A0AB; font-size: 16px;")
        self.empty_label.hide()
        root.addWidget(self.empty_label, 1)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = [u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
        self.add_paths(paths)
        event.acceptProposedAction()

    def _filter_list(self):
        query = self.search_bar.text().lower()
        f_idx = self.filter_combo.currentIndex()

        for i in range(self.list.count()):
            item = self.list.item(i)
            path = item.data(Qt.UserRole)
            data = self._items_data.get(path, {})
            tags = data.get("tags", "")
            text = f"{item.text()} {tags}".lower()

            match = query in text
            if f_idx == 2 and not tags:
                match = False
            item.setHidden(not match)

    def _refresh(self):
        self.list.clear()
        idx = self.sort_combo.currentIndex()
        if idx == 0:
            self._paths.sort(key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0, reverse=True)
        else:
            self._paths.sort(key=lambda x: Path(x).name.lower())

        now = time.time()
        for path in self._paths:
            data = self._items_data.get(path, {})
            tags = data.get("tags", "")
            title = data.get("title", "") or Path(path).name
            author = data.get("author", "")
            favorite = data.get("favorite", False)
            mtime = os.path.getmtime(path) if os.path.exists(path) else 0
            is_new = (now - mtime) < NEW_THRESHOLD_SEC

            prefix = ""
            if favorite:
                prefix += "⭐ "
            if is_new:
                prefix += f"[{tr('player.new')}] "
            display = prefix + "🎬 " + title
            if author:
                display += f" — {author}"
            if tags:
                display += f"  [{tags}]"

            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, path)
            item.setToolTip(path)
            self.list.addItem(item)

        self._persist()
        self._filter_list()

        has_items = self.list.count() > 0
        self.list.setVisible(has_items)
        self.empty_label.setVisible(not has_items)

    def _persist(self):
        settings().set_library([self._items_data[p] for p in self._paths if p in self._items_data])

    def add_paths(self, paths: list[str]):
        added = False
        for p in paths:
            if not p or Path(p).suffix.lower() not in VIDEO_EXTS:
                continue
            if p not in self._paths:
                self._paths.append(p)
                self._items_data[p] = {
                    "path": p, "tags": "", "favorite": False,
                    "watch_count": 0, "last_watched": 0,
                    "title": "", "author": "",
                }
                added = True
        if added:
            self._refresh()

    def _play_all(self):
        if self._paths:
            self.playAllRequested.emit(self._paths)

    def _clear_all(self):
        if not self._paths:
            return
        ans = QMessageBox.question(self, tr("dialog.confirm"), tr("library.clear"),
                                   QMessageBox.Yes | QMessageBox.No)
        if ans == QMessageBox.Yes:
            self._paths.clear()
            self._items_data.clear()
            self._refresh()

    def _add_files(self):
        start = settings().get_default_dir() or ""
        paths, _ = QFileDialog.getOpenFileNames(self, tr("dialog.openVideo"), start, tr("dialog.videoFilt"))
        self.add_paths(paths)

    def _on_double_click(self, item: QListWidgetItem):
        path = item.data(Qt.UserRole)
        if path:
            self.playRequested.emit(path)

    def _on_context_menu(self, pos):
        item = self.list.itemAt(pos)
        if not item:
            return
        path = item.data(Qt.UserRole)
        data = self._items_data.get(path, {})
        menu = QMenu(self)

        act_play = menu.addAction("▶ Играть")
        act_fav = menu.addAction(tr("btn.unfavorite") if data.get("favorite") else tr("btn.favorite"))
        act_info = menu.addAction("ℹ️ " + tr("btn.info"))
        act_tags = menu.addAction("🏷 Изменить теги")
        act_remove = menu.addAction(tr("library.remove"))

        action = menu.exec(self.list.mapToGlobal(pos))

        if action == act_play:
            self._on_double_click(item)
        elif action == act_fav:
            data["favorite"] = not data.get("favorite", False)
            self._items_data[path] = data
            self._refresh()
        elif action == act_info:
            from ui.info_dialog import InfoDialog
            meta = {
                "path": path,
                "size": f"{os.path.getsize(path)/(1024*1024):.1f} MB" if os.path.exists(path) else "—",
            }
            dlg = InfoDialog(self, path, meta)
            dlg.exec()
            self._load_data()
            self._refresh()
        elif action == act_tags:
            from PySide6.QtWidgets import QInputDialog
            tags, ok = QInputDialog.getText(self, "Теги", "Введите теги (через запятую):",
                                            text=data.get("tags", ""))
            if ok:
                data["tags"] = tags
                self._items_data[path] = data
                self._refresh()
        elif action == act_remove:
            if path in self._paths:
                self._paths.remove(path)
            self._items_data.pop(path, None)
            self._refresh()

    def retranslate(self, _lang: str = ""):
        self._title.setText(tr("library.title"))
        self.btn_add.setText(tr("library.add"))
        self.btn_clear.setText(tr("library.clear"))
        self.empty_label.setText(tr("library.empty"))
        self.sort_combo.setItemText(0, tr("library.sort.date"))
        self.sort_combo.setItemText(1, tr("library.sort.name"))
        self.filter_combo.setItemText(0, tr("library.filter.all"))
        self.filter_combo.setItemText(1, tr("library.filter.recent"))
        self.filter_combo.setItemText(2, tr("library.filter.tagged"))