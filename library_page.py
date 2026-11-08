# ui/library_page.py
"""Страница «Библиотека»: список видео + добавление/удаление/воспроизведение."""

from __future__ import annotations
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QFileDialog, QMenu, QMessageBox
)

from core.i18n import tr, translator
from core.settings import settings


VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v", ".flv", ".wmv", ".ts"}


class LibraryPage(QWidget):
    """Эмитит playRequested(path) при двойном клике / контекстном «Воспроизвести»."""

    playRequested = Signal(str)

    def __init__(self):
        super().__init__()
        self._paths: list[str] = settings().get_library()
        self._build_ui()
        self._refresh()

        translator().languageChanged.connect(self.retranslate)

    # ---------- UI ----------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        # header row
        header = QHBoxLayout()
        self._title = QLabel(tr("library.title"))
        self._title.setStyleSheet("font-size:20px; font-weight:700; color:#F5F5F7;")
        header.addWidget(self._title)
        header.addStretch()

        self.btn_add = QPushButton(tr("library.add"))
        self.btn_add.setObjectName("CtrlBtn")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.clicked.connect(self._add_files)

        self.btn_clear = QPushButton(tr("library.clear"))
        self.btn_clear.setObjectName("CtrlBtn")
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.clicked.connect(self._clear_all)

        header.addWidget(self.btn_add)
        header.addWidget(self.btn_clear)
        root.addLayout(header)

        # hint
        self._hint = QLabel(tr("library.play_hint"))
        self._hint.setStyleSheet("color:#5A5A66; font-size:12px;")
        root.addWidget(self._hint)

        # список
        self.list = QListWidget()
        self.list.setStyleSheet("""
            QListWidget {
                background:#17171C; border:1px solid #2A2A33;
                border-radius:12px; padding:6px;
            }
            QListWidget::item {
                padding:10px 12px; border-radius:8px; color:#F5F5F7;
            }
            QListWidget::item:selected {
                background:#E53935; color:white;
            }
            QListWidget::item:hover {
                background:#2A2A33;
            }
        """)
        self.list.itemDoubleClicked.connect(self._on_double_click)
        self.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self._on_context_menu)
        root.addWidget(self.list, 1)

        # пустое состояние
        self._empty = QLabel(tr("library.empty"))
        self._empty.setAlignment(Qt.AlignCenter)
        self._empty.setStyleSheet("color:#5A5A66; font-size:14px; padding:20px;")
        root.addWidget(self._empty)

    # ---------- данные ----------
    def _refresh(self):
        self.list.clear()
        for path in self._paths:
            if Path(path).exists():
                item = QListWidgetItem(f"🎬  {Path(path).name}")
                item.setData(Qt.UserRole, path)
                item.setToolTip(path)
                self.list.addItem(item)
        has_items = self.list.count() > 0
        self.list.setVisible(has_items)
        self._empty.setVisible(not has_items)
        self._persist()

    def _persist(self):
        settings().set_library(self._paths)

    # ---------- добавление ----------
    def _add_files(self):
        start_dir = settings().get_default_dir() or ""
        paths, _ = QFileDialog.getOpenFileNames(
            self, tr("dialog.openVideo"), start_dir, tr("dialog.videoFilt")
        )
        self.add_paths(paths)

    def add_paths(self, paths: list[str]):
        """Публичный метод — можно добавлять извне (например, при открытии файла)."""
        added = False
        for p in paths:
            if not p:
                continue
            ext = Path(p).suffix.lower()
            if ext not in VIDEO_EXTS:
                continue
            if p not in self._paths:
                self._paths.append(p)
                added = True
        if added:
            self._refresh()

    # ---------- удаление ----------
    def _clear_all(self):
        if not self._paths:
            return
        ans = QMessageBox.question(
            self, "ScarlyPlayer", tr("library.clear") + "?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if ans == QMessageBox.Yes:
            self._paths.clear()
            self._refresh()

    def _remove_item(self, item: QListWidgetItem):
        path = item.data(Qt.UserRole)
        if path in self._paths:
            self._paths.remove(path)
            self._refresh()

    # ---------- события ----------
    def _on_double_click(self, item: QListWidgetItem):
        path = item.data(Qt.UserRole)
        if path and Path(path).exists():
            self.playRequested.emit(path)

    def _on_context_menu(self, pos):
        item = self.list.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        act_play = menu.addAction("▶  " + tr("btn.play").replace("▶  ", ""))
        act_remove = menu.addAction(tr("library.remove"))
        action = menu.exec(self.list.mapToGlobal(pos))
        if action == act_play:
            self._on_double_click(item)
        elif action == act_remove:
            self._remove_item(item)

    # ---------- i18n ----------
    def retranslate(self, _lang: str = ""):
        self._title.setText(tr("library.title"))
        self.btn_add.setText(tr("library.add"))
        self.btn_clear.setText(tr("library.clear"))
        self._hint.setText(tr("library.play_hint"))
        self._empty.setText(tr("library.empty"))