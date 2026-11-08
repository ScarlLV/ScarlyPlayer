# ui/title_bar.py
"""Кастомный title bar с кнопкой бургер-меню и перетаскиванием окна."""

from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton

from core.i18n import tr, translator


class TitleBar(QWidget):
    sidebarToggled = Signal()

    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.setObjectName("TitleBar")
        self._win = parent_window
        self._drag_pos: QPoint | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 8, 8)
        layout.setSpacing(8)

        # Кнопка-бургер
        self.btn_menu = QPushButton("☰")
        self.btn_menu.setObjectName("WinBtn")
        self.btn_menu.setFixedSize(34, 30)
        self.btn_menu.setCursor(Qt.PointingHandCursor)
        self.btn_menu.setToolTip("Toggle sidebar")
        self.btn_menu.clicked.connect(self.sidebarToggled)
        layout.addWidget(self.btn_menu)

        # Заголовок
        self._title = QLabel(f"⚡ {tr('app.title')}")
        self._title.setObjectName("TitleLabel")
        layout.addWidget(self._title)
        layout.addStretch()

        # Кнопки окна
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

    # ---------- перетаскивание окна ----------
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self._win.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() & Qt.LeftButton and not self._win.isMaximized():
            self._win.move(e.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None