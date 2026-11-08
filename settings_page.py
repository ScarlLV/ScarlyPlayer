from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFileDialog, QFrame, QColorDialog, QScrollArea
)
from PySide6.QtGui import QColor

from core.i18n import tr, translator, LANG_NAMES
from core.settings import settings

class SettingsPage(QWidget):
    languageChanged = Signal(str)
    defaultDirChanged = Signal(str)
    themeChanged = Signal()

    def __init__(self):
        super().__init__()
        self._build_ui()
        self._refresh_labels()
        translator().languageChanged.connect(self.retranslate)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        root = QVBoxLayout(content)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(20)

        # ===== ПЛИТКА 1: ЯЗЫК =====
        card_lang = self._create_card()
        lay_lang = QVBoxLayout(card_lang)
        lay_lang.setContentsMargins(20, 20, 20, 20)
        lay_lang.setSpacing(16)

        self._lang_title = QLabel(tr("settings.lang"))
        self._lang_title.setStyleSheet("color: #F5F5F7; font-size: 16px; font-weight: 700;")
        lay_lang.addWidget(self._lang_title)

        lang_grid = QVBoxLayout()
        lang_grid.setSpacing(8)
        self._lang_buttons = {}
        
        row = QHBoxLayout()
        for i, (code, name) in enumerate(LANG_NAMES.items()):
            if i > 0 and i % 3 == 0:
                lang_grid.addLayout(row)
                row = QHBoxLayout()
                
            btn = QPushButton(name)
            btn.setObjectName("CtrlBtn") # Используем стиль кнопок из темы
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(40)
            btn.setChecked(settings().get_language() == code)
            # Меняем стиль, если выбрано
            if btn.isChecked():
                btn.setStyleSheet("background: #E53935; color: white; font-weight: bold;")
            btn.clicked.connect(lambda _, c=code: self._set_lang(c))
            row.addWidget(btn)
            self._lang_buttons[code] = btn
        
        row.addStretch()
        lang_grid.addLayout(row)
        lay_lang.addLayout(lang_grid)
        root.addWidget(card_lang)

        # ===== ПЛИТКА 2: ВНЕШНИЙ ВИД =====
        card_app = self._create_card()
        lay_app = QVBoxLayout(card_app)
        lay_app.setContentsMargins(20, 20, 20, 20)
        lay_app.setSpacing(16)

        self._appearance_title = QLabel(tr("settings.appearance"))
        self._appearance_title.setStyleSheet("color: #F5F5F7; font-size: 16px; font-weight: 700;")
        lay_app.addWidget(self._appearance_title)

        # Цвет
        color_row = QHBoxLayout()
        self._accent_label = QLabel(tr("settings.accent"))
        self._accent_label.setStyleSheet("color: #A0A0AB; font-size: 14px;")
        
        self._color_preview = QLabel()
        self._color_preview.setFixedSize(28, 28)
        self._update_color_preview()
        
        self._btn_color = QPushButton(tr("settings.accent.pick"))
        self._btn_color.setObjectName("CtrlBtn")
        self._btn_color.setCursor(Qt.PointingHandCursor)
        self._btn_color.clicked.connect(self._pick_color)
        
        color_row.addWidget(self._accent_label)
        color_row.addWidget(self._color_preview)
        color_row.addWidget(self._btn_color)
        color_row.addStretch()
        lay_app.addLayout(color_row)

        # Фон
        bg_row = QHBoxLayout()
        self._bg_label = QLabel(tr("settings.bg"))
        self._bg_label.setStyleSheet("color: #A0A0AB; font-size: 14px;")
        
        self._btn_bg_pick = QPushButton(tr("settings.bg.pick"))
        self._btn_bg_pick.setObjectName("CtrlBtn")
        self._btn_bg_pick.setCursor(Qt.PointingHandCursor)
        self._btn_bg_pick.clicked.connect(self._pick_bg)
        
        self._btn_bg_reset = QPushButton(tr("settings.bg.reset"))
        self._btn_bg_reset.setObjectName("CtrlBtn")
        self._btn_bg_reset.setCursor(Qt.PointingHandCursor)
        self._btn_bg_reset.clicked.connect(self._reset_bg)
        
        bg_row.addWidget(self._bg_label)
        bg_row.addWidget(self._btn_bg_pick)
        bg_row.addWidget(self._btn_bg_reset)
        bg_row.addStretch()
        lay_app.addLayout(bg_row)
        root.addWidget(card_app)

        # ===== ПЛИТКА 3: ПАПКА =====
        card_folder = self._create_card()
        lay_folder = QVBoxLayout(card_folder)
        lay_folder.setContentsMargins(20, 20, 20, 20)
        lay_folder.setSpacing(16)

        self._folder_title = QLabel(tr("settings.folder"))
        self._folder_title.setStyleSheet("color: #F5F5F7; font-size: 16px; font-weight: 700;")
        lay_folder.addWidget(self._folder_title)

        folder_row = QHBoxLayout()
        self._folder_label = QLabel("")
        self._folder_label.setStyleSheet("color: #A0A0AB; font-family: Consolas, monospace; font-size: 13px;")
        folder_row.addWidget(self._folder_label, 1)

        self._btn_folder_pick = QPushButton(tr("settings.folder.pick"))
        self._btn_folder_pick.setObjectName("CtrlBtn")
        self._btn_folder_pick.clicked.connect(self._pick_folder)
        
        self._btn_folder_reset = QPushButton(tr("settings.folder.reset"))
        self._btn_folder_reset.setObjectName("CtrlBtn")
        self._btn_folder_reset.clicked.connect(self._reset_folder)
        
        folder_row.addWidget(self._btn_folder_pick)
        folder_row.addWidget(self._btn_folder_reset)
        lay_folder.addLayout(folder_row)
        root.addWidget(card_folder)
        
        root.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _create_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("SettingsCard")
        # Легкая тень для объема
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)
        return card

    def _section_title(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #F5F5F7; font-size: 16px; font-weight: 700; margin-top: 10px;")
        return lbl

    def _set_lang(self, code: str):
        settings().set_language(code)
        translator().set_language(code)
        for c, b in self._lang_buttons.items():
            b.setChecked(c == code)
            if c == code:
                b.setStyleSheet("background: #E53935; color: white; font-weight: bold;")
            else:
                b.setStyleSheet("") # Сброс на дефолт
        self.languageChanged.emit(code)

    def _pick_color(self):
        current = QColor(settings().get_accent_color())
        color = QColorDialog.getColor(current, self, tr("settings.accent.pick"))
        if color.isValid():
            settings().set_accent_color(color.name())
            self._update_color_preview()
            self.themeChanged.emit()

    def _update_color_preview(self):
        c = settings().get_accent_color()
        self._color_preview.setStyleSheet(f"background: {c}; border-radius: 14px; border: 2px solid #5A5A66;")

    def _pick_bg(self):
        path, _ = QFileDialog.getOpenFileName(self, tr("settings.bg"), "", "Изображения (*.png *.jpg *.jpeg)")
        if path:
            settings().set_bg_image(path)
            self.themeChanged.emit()

    def _reset_bg(self):
        settings().set_bg_image("")
        self.themeChanged.emit()

    def _pick_folder(self):
        path = QFileDialog.getExistingDirectory(self, tr("settings.folder"), settings().get_default_dir())
        if path:
            settings().set_default_dir(path)
            self._refresh_labels()
            self.defaultDirChanged.emit(path)

    def _reset_folder(self):
        settings().set_default_dir("")
        self._refresh_labels()
        self.defaultDirChanged.emit("")

    def _refresh_labels(self):
        p = settings().get_default_dir()
        self._folder_label.setText(p if p else tr("settings.folder.none"))

    def retranslate(self, _lang: str = ""):
        self._lang_title.setText(tr("settings.lang"))
        self._appearance_title.setText(tr("settings.appearance"))
        self._accent_label.setText(tr("settings.accent"))
        self._btn_color.setText(tr("settings.accent.pick"))
        self._bg_label.setText(tr("settings.bg"))
        self._btn_bg_pick.setText(tr("settings.bg.pick"))
        self._btn_bg_reset.setText(tr("settings.bg.reset"))
        self._folder_title.setText(tr("settings.folder"))
        self._btn_folder_pick.setText(tr("settings.folder.pick"))
        self._btn_folder_reset.setText(tr("settings.folder.reset"))
        self._refresh_labels()