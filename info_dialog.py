# ui/info_dialog.py
"""Модальное окно с информацией о файле + редактирование названия/автора."""

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QFormLayout
)
from core.i18n import tr
from core.settings import settings


class InfoDialog(QDialog):
    def __init__(self, parent, path: str, metadata: dict):
        super().__init__(parent)
        self.setWindowTitle(tr("info.title_full"))
        self.setMinimumWidth(500)
        self._path = path
        self._metadata = metadata
        self.setStyleSheet(
            "QDialog { background: #17171C; color: #F5F5F7; }"
            "QLabel { color: #F5F5F7; }"
            "QLineEdit { background: #1F1F26; border: 1px solid #2A2A33; "
            "border-radius: 6px; padding: 6px; color: #F5F5F7; }"
            "QPushButton { background: #1F1F26; border-radius: 8px; "
            "padding: 8px 16px; color: white; }"
            "QPushButton:hover { background: #2A2A33; }"
            "QPushButton#AccentBtn { background: #E53935; font-weight: bold; }"
            "QPushButton#AccentBtn:hover { background: #FF5252; }"
        )
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Заголовок
        title = QLabel(tr("info.title_full"))
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(title)

        # Название файла
        filename_lbl = QLabel(Path(self._path).name)
        filename_lbl.setStyleSheet("color: #A0A0AB; font-size: 13px;")
        filename_lbl.setWordWrap(True)
        layout.addWidget(filename_lbl)

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background: #2A2A33; border: none;")
        line.setFixedHeight(1)
        layout.addWidget(line)

        # Форма с метаданными
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        # Редактируемые поля
        lib = settings().get_library()
        item = next((i for i in lib if i["path"] == self._path), {})
        self.title_edit = QLineEdit(item.get("title", "") or "")
        self.title_edit.setPlaceholderText(Path(self._path).stem)
        form.addRow(tr("info.meta.title") + ":", self.title_edit)

        self.author_edit = QLineEdit(item.get("author", "") or "")
        form.addRow(tr("info.meta.author") + ":", self.author_edit)

        # Только для чтения
        for key, label in [
            ("duration", tr("info.meta.duration")),
            ("size", tr("info.meta.size")),
            ("resolution", tr("info.meta.resolution")),
            ("path", tr("info.meta.path")),
        ]:
            val = self._metadata.get(key, "—")
            lbl = QLabel(str(val))
            lbl.setStyleSheet("color: #A0A0AB;")
            lbl.setWordWrap(True)
            lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            form.addRow(label + ":", lbl)

        layout.addLayout(form)
        layout.addStretch()

        # Кнопки
        btns = QHBoxLayout()
        btns.addStretch()

        btn_cancel = QPushButton(tr("info.close"))
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)

        btn_save = QPushButton(tr("info.meta.save"))
        btn_save.setObjectName("AccentBtn")
        btn_save.clicked.connect(self._save)
        btns.addWidget(btn_save)

        layout.addLayout(btns)

    def _save(self):
        lib = settings().get_library()
        for item in lib:
            if item["path"] == self._path:
                item["title"] = self.title_edit.text().strip()
                item["author"] = self.author_edit.text().strip()
                break
        settings().set_library(lib)
        self.accept()