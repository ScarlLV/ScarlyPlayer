# ui/library_page.py
import os
from pathlib import Path
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QFileDialog, QMenu, QMessageBox, QLineEdit
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtMultimedia import QMediaPlayer, QVideoSink, QVideoFrame

from core.i18n import tr, translator
from core.settings import settings

VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v", ".flv", ".wmv", ".ts"}

class LibraryPage(QWidget):
    playRequested = Signal(str)
    playAllRequested = Signal(list)

    def __init__(self):
        super().__init__()
        self._items_data = {} # path -> {tags, name}
        self._load_data()
        self._build_ui()
        self._refresh()
        translator().languageChanged.connect(self.retranslate)
        self.setAcceptDrops(True)

    def _load_data(self):
        raw = settings().get_library()
        self._paths = []
        for item in raw:
            if isinstance(item, dict):
                path = item.get("path")
                tags = item.get("tags", "")
            else:
                path = item
                tags = ""
            if path and Path(path).exists():
                self._paths.append(path)
                self._items_data[path] = {"tags": tags}
        settings().set_library([{"path": p, "tags": self._items_data[p]["tags"]} for p in self._paths])

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        header = QHBoxLayout()
        self._title = QLabel(tr("library.title"))
        self._title.setStyleSheet("font-size:20px; font-weight:700; color:#F5F5F7;")
        header.addWidget(self._title)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Поиск по имени/тегу...")
        self.search_bar.setStyleSheet("background:#1F1F26; border:1px solid #2A2A33; border-radius:8px; padding:6px;")
        self.search_bar.textChanged.connect(self._filter_list)
        header.addWidget(self.search_bar, 1)

        self.btn_add = QPushButton(tr("library.add"))
        self.btn_add.setObjectName("CtrlBtn")
        self.btn_add.clicked.connect(self._add_files)
        header.addWidget(self.btn_add)

        self.btn_play_all = QPushButton("▶ Играть всё")
        self.btn_play_all.setObjectName("CtrlBtn")
        self.btn_play_all.clicked.connect(self._play_all)
        header.addWidget(self.btn_play_all)

        self.btn_clear = QPushButton(tr("library.clear"))
        self.btn_clear.setObjectName("CtrlBtn")
        self.btn_clear.clicked.connect(self._clear_all)
        header.addWidget(self.btn_clear)
        root.addLayout(header)

        self.list = QListWidget()
        self.list.setStyleSheet("""
            QListWidget { background:#17171C; border:1px solid #2A2A33; border-radius:12px; padding:6px; }
            QListWidget::item { padding:10px 12px; border-radius:8px; color:#F5F5F7; }
            QListWidget::item:selected { background:#E53935; color:white; }
            QListWidget::item:hover { background:#2A2A33; }
        """)
        self.list.itemDoubleClicked.connect(self._on_double_click)
        self.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self._on_context_menu)
        root.addWidget(self.list, 1)

    # --- Drag & Drop ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                paths.append(url.toLocalFile())
        self.add_paths(paths)
        event.acceptProposedAction()

    # --- Поиск ---
    def _filter_list(self):
        query = self.search_bar.text().lower()
        for i in range(self.list.count()):
            item = self.list.item(i)
            path = item.data(Qt.UserRole)
            tags = self._items_data.get(path, {}).get("tags", "")
            text = f"{item.text()} {tags}".lower()
            item.setHidden(query not in text)

    # --- Данные ---
    def _refresh(self):
        self.list.clear()
        for path in self._paths:
            tags = self._items_data[path]["tags"]
            name = Path(path).name
            display = f"🎬 {name}"
            if tags:
                display += f"  [{tags}]"
            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, path)
            item.setToolTip(path)
            self.list.addItem(item)
        self._persist()
        self._filter_list()

    def _persist(self):
        data = [{"path": p, "tags": self._items_data[p]["tags"]} for p in self._paths]
        settings().set_library(data)

    def add_paths(self, paths: list[str]):
        added = False
        for p in paths:
            if not p: continue
            if Path(p).suffix.lower() not in VIDEO_EXTS: continue
            if p not in self._paths:
                self._paths.append(p)
                self._items_data[p] = {"tags": ""}
                added = True
        if added:
            self._refresh()

    def _play_all(self):
        if self._paths:
            self.playAllRequested.emit(self._paths)

    def _clear_all(self):
        if not self._paths: return
        ans = QMessageBox.question(self, tr("dialog.confirm"), tr("library.clear.confirm"), QMessageBox.Yes | QMessageBox.No)
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
        if not item: return
        path = item.data(Qt.UserRole)
        menu = QMenu(self)
        act_play = menu.addAction("▶ Играть")
        act_tags = menu.addAction("🏷 Изменить теги")
        act_remove = menu.addAction(tr("library.remove"))
        action = menu.exec(self.list.mapToGlobal(pos))
        
        if action == act_play:
            self._on_double_click(item)
        elif action == act_remove:
            if path in self._paths: self._paths.remove(path)
            self._items_data.pop(path, None)
            self._refresh()
        elif action == act_tags:
            from PySide6.QtWidgets import QInputDialog
            tags, ok = QInputDialog.getText(self, "Теги", "Введите теги (через запятую):", text=self._items_data[path]["tags"])
            if ok:
                self._items_data[path]["tags"] = tags
                self._refresh()

    def retranslate(self, _lang: str = ""):
        self._title.setText(tr("library.title"))
        self.btn_add.setText(tr("library.add"))
        self.btn_clear.setText(tr("library.clear"))