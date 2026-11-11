# ui/playlist_carousel.py
"""Карусель миниатюр следующих видео в плейлисте."""

import os
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame
)

from core.i18n import tr


class CarouselItem(QFrame):
    """Одна миниатюра в карусели."""
    clicked = Signal(int)  # индекс

    def __init__(self, index: int, path: str, is_active: bool = False):
        super().__init__()
        self._index = index
        self._path = path
        self._is_active = is_active
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(60)
        self.setMinimumWidth(200)
        self.setMaximumWidth(280)

        # Стиль
        if is_active:
            bg = "#E53935"
            border = "#FF5252"
        else:
            bg = "rgba(31,31,38,220)"
            border = "#2A2A33"

        self.setStyleSheet(
            f"QFrame {{ background: {bg}; border: 1px solid {border}; "
            f"border-radius: 8px; }}"
            f"QFrame:hover {{ background: rgba(229,57,53,150); }}"
            f"QLabel {{ background: transparent; border: none; }}"
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(2)

        name = Path(path).name
        if len(name) > 28:
            name = name[:25] + "..."

        title_lbl = QLabel(name)
        title_lbl.setStyleSheet(
            f"color: {'white' if is_active else '#F5F5F7'}; "
            f"font-size: 12px; font-weight: {'700' if is_active else '500'};"
        )
        lay.addWidget(title_lbl)

        # Размер файла
        try:
            size_mb = os.path.getsize(path) / (1024 * 1024)
            meta_lbl = QLabel(f"{size_mb:.1f} MB")
        except OSError:
            meta_lbl = QLabel("")
        meta_lbl.setStyleSheet(
            f"color: {'rgba(255,255,255,180)' if is_active else '#A0A0AB'}; "
            f"font-size: 10px;"
        )
        lay.addWidget(meta_lbl)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit(self._index)


class PlaylistCarousel(QWidget):
    """Горизонтальная карусель следующих видео."""

    itemClicked = Signal(int)  # индекс в плейлисте

    def __init__(self):
        super().__init__()
        self.setFixedHeight(80)
        self.setStyleSheet("background: transparent;")
        self._playlist: list[str] = []
        self._current_index: int = 0

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 8, 0, 8)
        lay.setSpacing(10)

        self._label = QLabel("📋 Следующие:")
        self._label.setStyleSheet(
            "color: #A0A0AB; font-size: 12px; font-weight: 600; "
            "background: transparent; padding-right: 6px;"
        )
        self._label.setFixedWidth(110)
        lay.addWidget(self._label)

        self._items_container = QHBoxLayout()
        self._items_container.setSpacing(8)
        lay.addLayout(self._items_container, 1)

        self.hide()

    def set_playlist(self, playlist: list[str], current_index: int):
        """Установить плейлист и текущий индекс."""
        self._playlist = playlist
        self._current_index = current_index
        self._rebuild()

    def clear(self):
        self._playlist = []
        self._current_index = 0
        self._rebuild()
        self.hide()

    def _rebuild(self):
        # Удалить старые
        while self._items_container.count():
            child = self._items_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Показать следующие 5 (не текущий)
        next_items = []
        for i in range(self._current_index + 1, min(len(self._playlist), self._current_index + 6)):
            next_items.append((i, self._playlist[i]))

        if not next_items:
            self.hide()
            return

        self._label.setText(f"📋 {tr('playlist.next')}:")

        for idx, path in next_items:
            item = CarouselItem(idx, path)
            item.clicked.connect(self.itemClicked)
            self._items_container.addWidget(item)

        self._items_container.addStretch()
        self.show()

    def retranslate(self):
        if self.isVisible():
            self._label.setText(f"📋 {tr('playlist.next')}:")