# ui/title_bar.py
"""Кастомный title bar с перетаскиванием окна."""
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton

from core.i18n import tr, translator


class TitleBar(QWidget):
    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.setObjectName("TitleBar")
        self._win = parent_window
        self._drag_pos: QPoint | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 8, 8)
        layout.setSpacing(8)

        self._title = QLabel(f"⚡ {tr('app.title')}")
        self._title.setObjectName("TitleLabel")
        layout.addWidget(self._title)
        layout.addStretch()

        for text, name, slot in (
            ("—", "WinBtn",   self._win.showMinimized),
            ("▢", "WinBtn",   self._toggle_max),
            ("✕", "WinClose", self._win.close),
        ):
            btn = QPushButton(text)
            btn.setObjectName(name)
            btn.setFixedSize(38, 30)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        translator().languageChanged.connect(self.retranslate)

    def retranslate(self, _lang: str = ""):
        self._title.setText(f"⚡ {tr('app.title')}")

    def _toggle_max(self):
        if self._win.isMaximized():
            self._win.showNormal()
        else:
            self._win.showMaximized()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self._win.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() & Qt.LeftButton and not self._win.isMaximized():
            self._win.move(e.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None