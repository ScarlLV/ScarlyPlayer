# ui/audio_selector.py
"""Диалог выбора аудио-устройства."""

from PySide6.QtCore import Qt
from PySide6.QtMultimedia import QMediaDevices
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem
)

from core.settings import settings


class AudioSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Аудио-устройство")
        self.resize(480, 360)
        self.setStyleSheet(
            "QDialog { background: #17171C; }"
            "QLabel { color: #F5F5F7; }"
            "QListWidget { background: #1F1F26; border: 1px solid #2A2A33; "
            "border-radius: 8px; color: #F5F5F7; padding: 6px; }"
            "QListWidget::item { padding: 10px; border-radius: 6px; }"
            "QListWidget::item:selected { background: #E53935; }"
            "QListWidget::item:hover { background: #2A2A33; }"
        )
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("🎧 Аудио-устройство")
        title.setStyleSheet("font-size: 18px; font-weight: 800;")
        layout.addWidget(title)

        hint = QLabel("Выбери устройство вывода звука")
        hint.setStyleSheet("color: #A0A0AB; font-size: 12px;")
        layout.addWidget(hint)

        self.list = QListWidget()
        current = settings().get_audio_device()

        # "По умолчанию" — всегда первый
        item_default = QListWidgetItem("🎧 Системное по умолчанию")
        item_default.setData(Qt.UserRole, "")
        self.list.addItem(item_default)

        # Устройства
        devices = QMediaDevices.audioOutputs()
        for dev in devices:
            name = dev.description()
            item = QListWidgetItem(f"🔊 {name}")
            item.setData(Qt.UserRole, name)
            self.list.addItem(item)
            if name == current:
                self.list.setCurrentItem(item)

        if not current:
            self.list.setCurrentItem(item_default)

        layout.addWidget(self.list, 1)

        # Кнопки
        btns = QHBoxLayout()
        btns.addStretch()

        btn_cancel = QPushButton("Отмена")
        btn_cancel.setStyleSheet(
            "background: #2A2A33; color: #F5F5F7; padding: 8px 16px; border-radius: 8px;"
        )
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)

        btn_save = QPushButton("Выбрать")
        btn_save.setStyleSheet(
            "background: #E53935; color: white; padding: 8px 20px; "
            "border-radius: 8px; font-weight: 600;"
        )
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self._save)
        btns.addWidget(btn_save)

        layout.addLayout(btns)

    def _save(self):
        item = self.list.currentItem()
        if item:
            settings().set_audio_device(item.data(Qt.UserRole))
        self.accept()