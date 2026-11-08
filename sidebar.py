# ui/sidebar.py
"""
Боковая панель ScarlyPlayer.
Пункты: Плеер / Библиотека / Настройки / О ScarlyPlayer.
Эмитит СТАБИЛЬНЫЙ ключ страницы (не локализованную строку).
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
)

from core.i18n import tr, translator


# ------------------------------------------------------------
#  Конфигурация пунктов навигации
#  (ключ страницы, иконка, i18n-ключ названия)
# ------------------------------------------------------------
NAV_ITEMS: list[tuple[str, str, str]] = [
    ("player",   "▶",  "nav.player"),
    ("library",  "📁", "nav.library"),
    ("settings", "⚙",  "nav.settings"),
    ("about",    "ℹ",  "nav.about"),
]


class Sidebar(QWidget):
    """
    Боковая панель навигации.

    Сигналы:
        pageRequested(str) — эмитит КЛЮЧ страницы:
                             'player' | 'library' | 'settings' | 'about'
    """

    pageRequested = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(220)

        self._current: str = "player"
        self._buttons: dict[str, QPushButton] = {}

        self._build_ui()

        # реакция на смену языка
        translator().languageChanged.connect(self.retranslate)

    # --------------------------------------------------------
    #  Построение UI
    # --------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(6)

        # --- логотип ---
        logo = QLabel("SCARLY")
        logo.setObjectName("SidebarLogo")
        logo.setStyleSheet(
            "color: #E53935;"
            "font-size: 20px;"
            "font-weight: 900;"
            "letter-spacing: 3px;"
            "padding: 0 6px 16px 6px;"
        )
        layout.addWidget(logo)

        # --- тонкая линия под лого ---
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFixedHeight(1)
        line.setStyleSheet("background: #2A2A33; border: none; margin-bottom: 6px;")
        layout.addWidget(line)

        # --- кнопки навигации ---
        for key, icon, i18n_key in NAV_ITEMS:
            btn = QPushButton(f"  {icon}   {tr(i18n_key)}")
            btn.setObjectName("NavBtn")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setChecked(key == self._current)
            btn.clicked.connect(lambda _, k=key: self._select(k))
            layout.addWidget(btn)
            self._buttons[key] = btn

        layout.addStretch()

        # --- версия ---
        self._version = QLabel("v1.0.0")
        self._version.setStyleSheet(
            "color: #5A5A66; font-size: 11px; padding: 6px;"
        )
        layout.addWidget(self._version)

    # --------------------------------------------------------
    #  Внутренние методы
    # --------------------------------------------------------
    def _select(self, key: str):
        """Пользователь кликнул пункт."""
        if key == self._current:
            # если кликнули по активному — просто подтверждаем
            self._buttons[key].setChecked(True)
            return

        self._current = key
        for k, btn in self._buttons.items():
            btn.setChecked(k == key)
        self.pageRequested.emit(key)

    # --------------------------------------------------------
    #  Публичный API
    # --------------------------------------------------------
    def set_current(self, key: str) -> None:
        """
        Программно выбрать страницу (без эмита pageRequested).
        Используется, например, при открытии файла → автоматический
        переход на страницу 'player'.
        """
        if key not in self._buttons or key == self._current:
            return
        self._current = key
        for k, btn in self._buttons.items():
            btn.setChecked(k == key)

    def current_page(self) -> str:
        """Возвращает текущий ключ страницы."""
        return self._current

    def retranslate(self, _lang: str = "") -> None:
        """Обновляет тексты кнопок при смене языка."""
        for key, icon, i18n_key in NAV_ITEMS:
            self._buttons[key].setText(f"  {icon}   {tr(i18n_key)}")