# ui/library_page.py
import os
import time
from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QFileDialog, QMenu, QMessageBox,
    QLineEdit, QComboBox, QDialog, QScrollArea
)
from core.i18n import tr, translator
from core.settings import settings

VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v", ".flv", ".wmv", ".ts"}
NEW_THRESHOLD_SEC = 24 * 3600


class DuplicatesDialog(QDialog):
    """Диалог для показа групп дубликатов."""

    def __init__(self, parent, groups: dict[str, list[dict]]):
        super().__init__(parent)
        self.setWindowTitle(tr("library.duplicates"))
        self.resize(720, 520)
        self.setStyleSheet(
            "QDialog { background: #17171C; color: #F5F5F7; }"
            "QLabel { color: #F5F5F7; background: transparent; }"
            "QPushButton { background: #2A2A33; color: #F5F5F7; padding: 6px 12px; "
            "border-radius: 6px; }"
            "QPushButton:hover { background: #3A3A45; }"
            "QPushButton#DangerBtn { background: #C62828; }"
            "QPushButton#DangerBtn:hover { background: #E53935; }"
        )
        self._groups = groups
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        title = QLabel("🔍 " + tr("library.duplicates"))
        title.setStyleSheet("font-size: 18px; font-weight: 800;")
        root.addWidget(title)

        subtitle = QLabel(tr("library.duplicates.found").format(n=len(self._groups)))
        subtitle.setStyleSheet("color: #A0A0AB; font-size: 13px;")
        root.addWidget(subtitle)

        # Скролл с группами
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_lay = QVBoxLayout(content)
        content_lay.setSpacing(16)

        for i, (hash_, items) in enumerate(self._groups.items(), start=1):
            group_widget = QWidget()
            group_widget.setStyleSheet(
                "background: #1F1F26; border: 1px solid #2A2A33; border-radius: 10px;"
            )
            group_lay = QVBoxLayout(group_widget)
            group_lay.setContentsMargins(16, 12, 16, 12)
            group_lay.setSpacing(8)

            header = QLabel(f"Группа #{i} — {len(items)} файл(а)")
            header.setStyleSheet("font-size: 14px; font-weight: 700; color: #E53935;")
            group_lay.addWidget(header)

            for item in items:
                path = item["path"]
                row = QHBoxLayout()

                name = QLabel(Path(path).name)
                name.setStyleSheet("color: #F5F5F7; font-size: 13px;")
                name.setWordWrap(True)
                row.addWidget(name, 1)

                # Размер
                try:
                    size_mb = os.path.getsize(path) / (1024 * 1024)
                    size_lbl = QLabel(f"{size_mb:.1f} MB")
                    size_lbl.setStyleSheet("color: #A0A0AB; font-size: 12px;")
                    row.addWidget(size_lbl)
                except OSError:
                    pass

                group_lay.addLayout(row)

            content_lay.addWidget(group_widget)

        content_lay.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        # Кнопки
        btns = QHBoxLayout()
        btns.addStretch()

        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.accept)
        btns.addWidget(btn_close)

        root.addLayout(btns)


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

        # Заголовок + поиск
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

        # Панель инструментов
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

        self.btn_duplicates = QPushButton(tr("library.duplicates"))
        self.btn_duplicates.setObjectName("CtrlBtn")
        self.btn_duplicates.clicked.connect(self._find_duplicates)
        toolbar.addWidget(self.btn_duplicates)

        self.btn_clear = QPushButton(tr("library.clear"))
        self.btn_clear.setObjectName("CtrlBtn")
        self.btn_clear.clicked.connect(self._clear_all)
        toolbar.addWidget(self.btn_clear)
        root.addLayout(toolbar)

        # Список
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

        # Пустое состояние
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
            watch_count = int(data.get("watch_count", 0))
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
            if watch_count > 0:
                display += f"  👁 {watch_count}"
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
                # Считаем хэш сразу
                h = settings().compute_hash(p)
                self._items_data[p] = {
                    "path": p, "tags": "", "favorite": False,
                    "watch_count": 0, "last_watched": 0,
                    "title": "", "author": "", "hash": h,
                }
                added = True
        if added:
            self._refresh()

    def _play_all(self):
        if self._paths:
            self.playAllRequested.emit(self._paths)

    def _find_duplicates(self):
        # Обновляем хэши для тех, у кого нет
        updated = settings().update_library_hashes()
        if updated:
            self._load_data()

        groups = settings().find_duplicates()
        if not groups:
            QMessageBox.information(self, tr("library.duplicates"), tr("library.duplicates.none"))
            return
        dlg = DuplicatesDialog(self, groups)
        dlg.exec()

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
        self.btn_duplicates.setText(tr("library.duplicates"))
        self.empty_label.setText(tr("library.empty"))
        self.sort_combo.setItemText(0, tr("library.sort.date"))
        self.sort_combo.setItemText(1, tr("library.sort.name"))
        self.filter_combo.setItemText(0, tr("library.filter.all"))
        self.filter_combo.setItemText(1, tr("library.filter.recent"))
        self.filter_combo.setItemText(2, tr("library.filter.tagged"))