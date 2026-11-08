# ui/about_page.py
"""Экран «О ScarlyPlayer» — версия, автор, ссылки."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QFrame
)
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

from core.i18n import tr, translator, APP_VERSION, APP_AUTHOR, APP_REPO


class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        translator().languageChanged.connect(self.retranslate)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignCenter)
        root.setContentsMargins(40, 40, 40, 40)
        root.setSpacing(16)

        # Логотип-заголовок
        logo = QLabel("SCARLY")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet(
            "color:#E53935; font-size:48px; font-weight:900; letter-spacing:8px;"
        )
        root.addWidget(logo)

        subtitle = QLabel("PLAYER")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(
            "color:#F5F5F7; font-size:16px; letter-spacing:12px; margin-top:-10px;"
        )
        root.addWidget(subtitle)

        # карточка с инфой
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background:#17171C; border:1px solid #2A2A33; "
            "border-radius:16px; }"
        )
        card.setFixedWidth(420)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(24, 20, 24, 20)
        card_lay.setSpacing(10)

        self._info = {}
        for key, val in (
            ("about.version", APP_VERSION),
            ("about.author",  APP_AUTHOR),
        ):
            row = QHBoxLayout()
            k = QLabel(tr(key))
            k.setStyleSheet("color:#A0A0AB; font-size:13px;")
            v = QLabel(val)
            v.setStyleSheet("color:#F5F5F7; font-size:13px; font-weight:600;")
            row.addWidget(k); row.addStretch(); row.addWidget(v)
            card_lay.addLayout(row)
            self._info[key] = k

        # ссылка на GitHub
        self._repo_label = QLabel(tr("about.repo"))
        self._repo_label.setStyleSheet("color:#A0A0AB; font-size:13px;")
        repo_btn = QPushButton("🔗  " + APP_REPO.split("//")[-1])
        repo_btn.setStyleSheet(
            "QPushButton { background:transparent; color:#E53935; "
            "border:none; text-align:right; font-size:13px; }"
            "QPushButton:hover { color:#FF5252; text-decoration:underline; }"
        )
        repo_btn.setCursor(Qt.PointingHandCursor)
        repo_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(APP_REPO))
        )

        repo_row = QHBoxLayout()
        repo_row.addWidget(self._repo_label)
        repo_row.addStretch()
        repo_row.addWidget(repo_btn)
        card_lay.addLayout(repo_row)

        root.addWidget(card, alignment=Qt.AlignCenter)

        # подпись
        self._thanks = QLabel(tr("about.thanks"))
        self._thanks.setAlignment(Qt.AlignCenter)
        self._thanks.setStyleSheet("color:#5A5A66; font-size:12px; margin-top:10px;")
        root.addWidget(self._thanks)

    def retranslate(self, _lang: str = ""):
        for key, lbl in self._info.items():
            lbl.setText(tr(key))
        self._repo_label.setText(tr("about.repo"))
        self._thanks.setText(tr("about.thanks"))