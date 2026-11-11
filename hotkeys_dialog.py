# ui/hotkeys_dialog.py
"""Редактор горячих клавиш."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QKeySequenceEdit, QHeaderView,
    QMessageBox, QAbstractItemView
)

from core.i18n import tr
from core.settings import settings


# Действие → ключ i18n
ACTIONS = [
    ("play_pause",       "hotkeys.play"),
    ("seek_left",        "hotkeys.seek"),
    ("seek_right",       "hotkeys.seek"),
    ("seek_left_long",   "hotkeys.seek"),
    ("seek_right_long",  "hotkeys.seek"),
    ("fullscreen",       "hotkeys.fullscreen"),
    ("exit_fullscreen",  "hotkeys.fullscreen"),
    ("mute",             "hotkeys.mute"),
    ("open_file",        "hotkeys.open"),
]

# Для отображения — русские названия (для простоты)
ACTION_LABELS = {
    "play_pause":       "Играть / Пауза",
    "seek_left":        "Перемотка ←",
    "seek_right":       "Перемотка →",
    "seek_left_long":   "Перемотка ← (длинная)",
    "seek_right_long":  "Перемотка → (длинная)",
    "fullscreen":       "Полный экран",
    "exit_fullscreen":  "Выйти из фуллскрина",
    "mute":             "Без звука",
    "open_file":        "Открыть файл",
}


class HotkeysDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Горячие клавиши")
        self.resize(560, 480)
        self.setStyleSheet(
            "QDialog { background: #17171C; }"
            "QLabel { color: #F5F5F7; }"
            "QTableWidget { background: #1F1F26; border: 1px solid #2A2A33; "
            "border-radius: 8px; color: #F5F5F7; gridline-color: #2A2A33; }"
            "QTableWidget::item { padding: 6px; }"
            "QTableWidget::item:selected { background: #E53935; }"
            "QHeaderView::section { background: #2A2A33; color: #F5F5F7; "
            "padding: 8px; border: none; font-weight: 600; }"
            "QKeySequenceEdit { background: #2A2A33; border: 1px solid #3A3A45; "
            "border-radius: 6px; padding: 4px; color: #F5F5F7; }"
        )
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("⌨️ Горячие клавиши")
        title.setStyleSheet("font-size: 18px; font-weight: 800;")
        layout.addWidget(title)

        hint = QLabel("Клик по клавише → нажми новую комбинацию")
        hint.setStyleSheet("color: #A0A0AB; font-size: 12px;")
        layout.addWidget(hint)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Действие", "Клавиша"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setRowCount(len(ACTIONS))

        for row, (action, _) in enumerate(ACTIONS):
            # Действие
            label = ACTION_LABELS.get(action, action)
            item_action = QTableWidgetItem(label)
            item_action.setFlags(item_action.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, item_action)

            # KeySequenceEdit
            edit = QKeySequenceEdit()
            current = settings().get_hotkey(action)
            if current:
                edit.setKeySequence(QKeySequence(current))
            edit.editingFinished.connect(lambda r=row, a=action, e=edit: self._on_key_changed(a, e))
            self.table.setCellWidget(row, 1, edit)

        layout.addWidget(self.table, 1)

        # Кнопки
        btns = QHBoxLayout()

        btn_reset = QPushButton("↺ Сбросить всё")
        btn_reset.setStyleSheet(
            "background: #2A2A33; color: #F5F5F7; padding: 8px 16px; "
            "border-radius: 8px; font-weight: 600;"
        )
        btn_reset.setCursor(Qt.PointingHandCursor)
        btn_reset.clicked.connect(self._reset_all)
        btns.addWidget(btn_reset)

        btns.addStretch()

        btn_cancel = QPushButton("Отмена")
        btn_cancel.setStyleSheet(
            "background: #2A2A33; color: #F5F5F7; padding: 8px 16px; border-radius: 8px;"
        )
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)

        btn_save = QPushButton("Сохранить")
        btn_save.setStyleSheet(
            "background: #E53935; color: white; padding: 8px 20px; "
            "border-radius: 8px; font-weight: 600;"
        )
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self._save)
        btns.addWidget(btn_save)

        layout.addLayout(btns)

    def _on_key_changed(self, action: str, edit: QKeySequenceEdit):
        """Проверить конфликты и подсветить."""
        seq = edit.keySequence().toString()
        if not seq:
            return
        # Проверка на конфликт
        for row, (other_action, _) in enumerate(ACTIONS):
            if other_action == action:
                continue
            other_edit = self.table.cellWidget(row, 1)
            if other_edit and other_edit.keySequence().toString() == seq:
                edit.setKeySequence(QKeySequence())
                QMessageBox.warning(
                    self, "Конфликт",
                    f"Комбинация {seq} уже занята: {ACTION_LABELS.get(other_action, other_action)}"
                )
                return

    def _reset_all(self):
        for row, (action, _) in enumerate(ACTIONS):
            edit = self.table.cellWidget(row, 1)
            if edit:
                default = settings().DEFAULT_HOTKEYS.get(action, "")
                edit.setKeySequence(QKeySequence(default))

    def _save(self):
        for row, (action, _) in enumerate(ACTIONS):
            edit = self.table.cellWidget(row, 1)
            if edit:
                seq = edit.keySequence().toString()
                if seq:
                    settings().set_hotkey(action, seq)
                else:
                    settings().set_hotkey(action, settings().DEFAULT_HOTKEYS.get(action, ""))
        self.accept()