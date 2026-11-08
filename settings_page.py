# ui/settings_page.py
"""Страница «Настройки»: язык + папка по умолчанию + заглушка «расширенные скоро»."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QFrame
)

from core.i18n import tr, translator, LANG_NAMES
from core.settings import settings


class SettingsPage(QWidget):
    """languageChanged сигнал наружу — чтобы MainWindow обновил состояние кнопок."""

    languageChanged = Signal(str)
    defaultDirChanged = Signal(str)

    def __init__(self):
        super().__init__()
        self._build_ui()
        self._refresh_dir_label()
        translator().languageChanged.connect(self.retranslate)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(20)

        # ===== Язык =====
        self._lang_title = self._section_title(tr("settings.lang"))
        root.addWidget(self._lang_title)

        lang_row = QHBoxLayout()
        lang_row.setSpacing(10)
        self._lang_buttons = {}
        for code, name in LANG_NAMES.items():
            btn = QPushButton(name)
            btn.setObjectName("NavBtn")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedWidth(150)
            btn.setChecked(settings().get_language() == code)
            btn.clicked.connect(lambda _, c=code: self._set_lang(c))
            lang_row.addWidget(btn)
            self._lang_buttons[code] = btn
        lang_row.addStretch()
        root.addLayout(lang_row)

        # ===== Папка по умолчанию =====
        self._folder_title = self._section_title(tr("settings.folder"))
        root.addWidget(self._folder_title)

        folder_card = QFrame()
        folder_card.setStyleSheet(
            "QFrame { background:#17171C; border:1px solid #2A2A33; "
            "border-radius:12px; }"
        )
        folder_lay = QHBoxLayout(folder_card)
        folder_lay.setContentsMargins(16, 12, 16, 12)
        folder_lay.setSpacing(10)

        self._folder_label = QLabel("")
        self._folder_label.setStyleSheet(
            "color:#A0A0AB; font-size:13px; font-family:Consolas, monospace;"
        )
        self._folder_label.setWordWrap(False)
        folder_lay.addWidget(self._folder_label, 1)

        self._btn_pick = QPushButton(tr("settings.folder.pick"))
        self._btn_pick.setObjectName("CtrlBtn")
        self._btn_pick.setCursor(Qt.PointingHandCursor)
        self._btn_pick.clicked.connect(self._pick_folder)

        self._btn_reset = QPushButton(tr("settings.folder.reset"))
        self._btn_reset.setObjectName("CtrlBtn")
        self._btn_reset.setCursor(Qt.PointingHandCursor)
        self._btn_reset.clicked.connect(self._reset_folder)

        folder_lay.addWidget(self._btn_pick)
        folder_lay.addWidget(self._btn_reset)
        root.addWidget(folder_card)

        # ===== Заглушка расширенных настроек =====
        self._extended = QLabel(tr("settings.extended.soon"))
        self._extended.setStyleSheet(
            "color:#5A5A66; font-size:13px; font-style:italic; margin-top:30px;"
        )
        root.addWidget(self._extended)

        root.addStretch()

    def _section_title(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("color:#F5F5F7; font-size:15px; font-weight:600;")
        return lbl

    # ---------- handlers ----------
    def _set_lang(self, code: str):
        settings().set_language(code)
        translator().set_language(code)
        for c, b in self._lang_buttons.items():
            b.setChecked(c == code)
        self.languageChanged.emit(code)

    def _pick_folder(self):
        current = settings().get_default_dir() or ""
        path = QFileDialog.getExistingDirectory(
            self, tr("settings.folder"), current
        )
        if path:
            settings().set_default_dir(path)
            self._refresh_dir_label()
            self.defaultDirChanged.emit(path)

    def _reset_folder(self):
        settings().set_default_dir("")
        self._refresh_dir_label()
        self.defaultDirChanged.emit("")

    def _refresh_dir_label(self):
        p = settings().get_default_dir()
        self._folder_label.setText(p if p else tr("settings.folder.none"))

    # ---------- i18n ----------
    def retranslate(self, _lang: str = ""):
        self._lang_title.setText(tr("settings.lang"))
        self._folder_title.setText(tr("settings.folder"))
        self._btn_pick.setText(tr("settings.folder.pick"))
        self._btn_reset.setText(tr("settings.folder.reset"))
        self._extended.setText(tr("settings.extended.soon"))
        self._refresh_dir_label()