# ui/settings_page.py
"""Страница настроек ScarlyPlayer v1.3.0."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QFrame, QColorDialog, QScrollArea, QCheckBox, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QColor
from core.i18n import tr, translator, LANG_NAMES
from core.settings import settings


class SettingsPage(QWidget):
    languageChanged = Signal(str)
    defaultDirChanged = Signal(str)
    themeChanged = Signal()
    resetRequested = Signal()
    bgVideoChanged = Signal()

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
        root.setSpacing(16)

        # ============================================================
        #  ПЛИТКА 1: ЯЗЫК
        # ============================================================
        card_lang = self._create_card()
        lay_lang = QVBoxLayout(card_lang)
        lay_lang.setContentsMargins(20, 20, 20, 20)
        lay_lang.setSpacing(12)

        self._lang_title = self._section_title(tr("settings.lang"))
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
            btn.setObjectName("CtrlBtn")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(38)
            btn.setChecked(settings().get_language() == code)
            if btn.isChecked():
                btn.setStyleSheet("background: #E53935; color: white; font-weight: bold;")
            btn.clicked.connect(lambda _, c=code: self._set_lang(c))
            row.addWidget(btn)
            self._lang_buttons[code] = btn

        row.addStretch()
        lang_grid.addLayout(row)
        lay_lang.addLayout(lang_grid)
        root.addWidget(card_lang)

        # ============================================================
        #  ПЛИТКА 2: ВНЕШНИЙ ВИД
        # ============================================================
        card_app = self._create_card()
        lay_app = QVBoxLayout(card_app)
        lay_app.setContentsMargins(20, 20, 20, 20)
        lay_app.setSpacing(12)

        self._appearance_title = self._section_title(tr("settings.appearance"))
        lay_app.addWidget(self._appearance_title)

        # Акцент
        color_row = QHBoxLayout()
        self._accent_label = QLabel(tr("settings.accent"))
        self._accent_label.setStyleSheet("color: #A0A0AB;")
        self._color_preview = QLabel()
        self._color_preview.setFixedSize(24, 24)
        self._update_color_preview()
        self._btn_color = QPushButton(tr("settings.accent.pick"))
        self._btn_color.setObjectName("CtrlBtn")
        self._btn_color.clicked.connect(self._pick_color)
        color_row.addWidget(self._accent_label)
        color_row.addWidget(self._color_preview)
        color_row.addWidget(self._btn_color)
        color_row.addStretch()
        lay_app.addLayout(color_row)

        # Фон (картинка)
        bg_row = QHBoxLayout()
        self._bg_label = QLabel(tr("settings.bg"))
        self._bg_label.setStyleSheet("color: #A0A0AB;")
        self._btn_bg_pick = QPushButton(tr("settings.bg.pick"))
        self._btn_bg_pick.setObjectName("CtrlBtn")
        self._btn_bg_pick.clicked.connect(self._pick_bg)
        self._btn_bg_reset = QPushButton(tr("settings.bg.reset"))
        self._btn_bg_reset.setObjectName("CtrlBtn")
        self._btn_bg_reset.clicked.connect(self._reset_bg)
        bg_row.addWidget(self._bg_label)
        bg_row.addWidget(self._btn_bg_pick)
        bg_row.addWidget(self._btn_bg_reset)
        bg_row.addStretch()
        lay_app.addLayout(bg_row)

        # Видео-фон
        vbg_row = QHBoxLayout()
        self._vbg_label = QLabel(tr("settings.video_bg"))
        self._vbg_label.setStyleSheet("color: #A0A0AB;")
        self._btn_vbg_pick = QPushButton(tr("settings.video_bg.pick"))
        self._btn_vbg_pick.setObjectName("CtrlBtn")
        self._btn_vbg_pick.clicked.connect(self._pick_vbg)
        self._btn_vbg_reset = QPushButton(tr("settings.video_bg.reset"))
        self._btn_vbg_reset.setObjectName("CtrlBtn")
        self._btn_vbg_reset.clicked.connect(self._reset_vbg)
        vbg_row.addWidget(self._vbg_label)
        vbg_row.addWidget(self._btn_vbg_pick)
        vbg_row.addWidget(self._btn_vbg_reset)
        vbg_row.addStretch()
        lay_app.addLayout(vbg_row)

        root.addWidget(card_app)

        # ============================================================
        #  ПЛИТКА 3: ВОСПРОИЗВЕДЕНИЕ
        # ============================================================
        card_play = self._create_card()
        lay_play = QVBoxLayout(card_play)
        lay_play.setContentsMargins(20, 20, 20, 20)
        lay_play.setSpacing(12)

        self._playback_title = self._section_title("Воспроизведение")
        lay_play.addWidget(self._playback_title)

        self._remember_cb = QCheckBox(tr("settings.remember_position"))
        self._remember_cb.setChecked(settings().get_remember_position())
        self._remember_cb.setStyleSheet("color: #F5F5F7;")
        self._remember_cb.toggled.connect(lambda v: settings().set_remember_position(v))
        lay_play.addWidget(self._remember_cb)

        self._fps_cb = QCheckBox(tr("settings.fps_overlay"))
        self._fps_cb.setChecked(settings().get_fps_overlay())
        self._fps_cb.setStyleSheet("color: #F5F5F7;")
        self._fps_cb.toggled.connect(lambda v: settings().set_fps_overlay(v))
        lay_play.addWidget(self._fps_cb)

        root.addWidget(card_play)

        # ============================================================
        #  ПЛИТКА 4: АУДИО-УСТРОЙСТВО  (НОВОЕ)
        # ============================================================
        card_audio = self._create_card()
        lay_audio = QVBoxLayout(card_audio)
        lay_audio.setContentsMargins(20, 20, 20, 20)
        lay_audio.setSpacing(12)

        self._audio_title = self._section_title(tr("settings.audio"))
        lay_audio.addWidget(self._audio_title)

        audio_row = QHBoxLayout()
        self._audio_label = QLabel(settings().get_audio_device() or tr("settings.audio.none"))
        self._audio_label.setStyleSheet("color: #A0A0AB; font-family: Consolas, monospace;")
        audio_row.addWidget(self._audio_label, 1)

        self._btn_audio = QPushButton(tr("settings.audio.pick"))
        self._btn_audio.setObjectName("CtrlBtn")
        self._btn_audio.clicked.connect(self._pick_audio)
        audio_row.addWidget(self._btn_audio)
        lay_audio.addLayout(audio_row)
        root.addWidget(card_audio)

        # ============================================================
        #  ПЛИТКА 5: ГОРЯЧИЕ КЛАВИШИ  (НОВОЕ)
        # ============================================================
        card_hotkeys = self._create_card()
        lay_hotkeys = QVBoxLayout(card_hotkeys)
        lay_hotkeys.setContentsMargins(20, 20, 20, 20)
        lay_hotkeys.setSpacing(12)

        self._hotkeys_title = self._section_title(tr("settings.hotkeys"))
        lay_hotkeys.addWidget(self._hotkeys_title)

        hotkey_row = QHBoxLayout()
        hotkey_hint = QLabel("Клик → откроется редактор")
        hotkey_hint.setStyleSheet("color: #A0A0AB; font-size: 12px;")
        hotkey_row.addWidget(hotkey_hint, 1)

        self._btn_hotkeys = QPushButton(tr("settings.hotkeys.edit"))
        self._btn_hotkeys.setObjectName("CtrlBtn")
        self._btn_hotkeys.clicked.connect(self._open_hotkeys)
        hotkey_row.addWidget(self._btn_hotkeys)
        lay_hotkeys.addLayout(hotkey_row)
        root.addWidget(card_hotkeys)

        # ============================================================
        #  ПЛИТКА 6: ПРОФИЛЬ  (НОВОЕ)
        # ============================================================
        card_profile = self._create_card()
        lay_profile = QVBoxLayout(card_profile)
        lay_profile.setContentsMargins(20, 20, 20, 20)
        lay_profile.setSpacing(12)

        self._profile_title = self._section_title(tr("settings.profile"))
        lay_profile.addWidget(self._profile_title)

        profile_hint = QLabel("Сохранить/загрузить все настройки в .scarly файл")
        profile_hint.setStyleSheet("color: #A0A0AB; font-size: 12px;")
        lay_profile.addWidget(profile_hint)

        profile_row = QHBoxLayout()
        self._btn_export = QPushButton(tr("settings.profile.export"))
        self._btn_export.setObjectName("CtrlBtn")
        self._btn_export.clicked.connect(self._export_profile)
        profile_row.addWidget(self._btn_export)

        self._btn_import = QPushButton(tr("settings.profile.import"))
        self._btn_import.setObjectName("CtrlBtn")
        self._btn_import.clicked.connect(self._import_profile)
        profile_row.addWidget(self._btn_import)
        profile_row.addStretch()
        lay_profile.addLayout(profile_row)
        root.addWidget(card_profile)

        # ============================================================
        #  ПЛИТКА 7: ПАПКА
        # ============================================================
        card_folder = self._create_card()
        lay_folder = QVBoxLayout(card_folder)
        lay_folder.setContentsMargins(20, 20, 20, 20)
        lay_folder.setSpacing(12)

        self._folder_title = self._section_title(tr("settings.folder"))
        lay_folder.addWidget(self._folder_title)

        folder_row = QHBoxLayout()
        self._folder_label = QLabel("")
        self._folder_label.setStyleSheet("color: #A0A0AB; font-family: Consolas, monospace;")
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

        # ============================================================
        #  ПЛИТКА 8: КЭШ
        # ============================================================
        card_cache = self._create_card()
        lay_cache = QVBoxLayout(card_cache)
        lay_cache.setContentsMargins(20, 20, 20, 20)
        lay_cache.setSpacing(12)

        self._cache_title = self._section_title(tr("settings.cache"))
        lay_cache.addWidget(self._cache_title)

        self._btn_cache = QPushButton(tr("settings.cache.clear"))
        self._btn_cache.setObjectName("CtrlBtn")
        self._btn_cache.clicked.connect(self._clear_cache)
        lay_cache.addWidget(self._btn_cache, alignment=Qt.AlignLeft)

        self._cache_status = QLabel("")
        self._cache_status.setStyleSheet("color: #5A5A66;")
        lay_cache.addWidget(self._cache_status)

        root.addWidget(card_cache)

        # ============================================================
        #  ПЛИТКА 9: ОПАСНАЯ ЗОНА
        # ============================================================
        card_danger = self._create_card()
        lay_danger = QVBoxLayout(card_danger)
        lay_danger.setContentsMargins(20, 20, 20, 20)
        lay_danger.setSpacing(12)

        self._danger_title = self._section_title(tr("settings.danger"))
        self._danger_title.setStyleSheet("color: #E53935; font-size: 16px; font-weight: 700;")
        lay_danger.addWidget(self._danger_title)

        self._danger_desc = QLabel(tr("settings.reset.desc"))
        self._danger_desc.setStyleSheet("color: #A0A0AB;")
        lay_danger.addWidget(self._danger_desc)

        self._btn_reset = QPushButton(tr("settings.reset.button"))
        self._btn_reset.setObjectName("PlayBtn")
        self._btn_reset.setStyleSheet("background: #C62828; color: white; padding: 10px;")
        self._btn_reset.clicked.connect(self._confirm_reset)
        lay_danger.addWidget(self._btn_reset, alignment=Qt.AlignLeft)

        root.addWidget(card_danger)

        root.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _create_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("SettingsCard")
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)
        return card

    def _section_title(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #F5F5F7; font-size: 16px; font-weight: 700;")
        return lbl

    # ============================================================
    #  ОБРАБОТЧИКИ
    # ============================================================
    def _set_lang(self, code: str):
        settings().set_language(code)
        translator().set_language(code)
        for c, b in self._lang_buttons.items():
            b.setChecked(c == code)
            if c == code:
                b.setStyleSheet("background: #E53935; color: white; font-weight: bold;")
            else:
                b.setStyleSheet("")
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
        self._color_preview.setStyleSheet(
            f"background: {c}; border-radius: 12px; border: 1px solid #5A5A66;"
        )

    def _pick_bg(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr("settings.bg"), "", "Изображения (*.png *.jpg *.jpeg)"
        )
        if path:
            settings().set_bg_image(path)
            self.themeChanged.emit()

    def _reset_bg(self):
        settings().set_bg_image("")
        self.themeChanged.emit()

    def _pick_vbg(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr("settings.video_bg"), "", "Видео (*.mp4 *.webm)"
        )
        if path:
            settings().set_bg_video(path)
            self.bgVideoChanged.emit()

    def _reset_vbg(self):
        settings().set_bg_video("")
        self.bgVideoChanged.emit()

    def _pick_audio(self):
        from ui.audio_selector import AudioSelectorDialog
        dlg = AudioSelectorDialog(self)
        if dlg.exec():
            self._audio_label.setText(
                settings().get_audio_device() or tr("settings.audio.none")
            )

    def _open_hotkeys(self):
        from ui.hotkeys_dialog import HotkeysDialog
        dlg = HotkeysDialog(self)
        dlg.exec()

    def _export_profile(self):
        settings().export_profile(self)

    def _import_profile(self):
        if settings().import_profile(self):
            self._refresh_labels()
            translator().set_language(settings().get_language())
            self.themeChanged.emit()

    def _pick_folder(self):
        path = QFileDialog.getExistingDirectory(
            self, tr("settings.folder"), settings().get_default_dir()
        )
        if path:
            settings().set_default_dir(path)
            self._refresh_labels()
            self.defaultDirChanged.emit(path)

    def _reset_folder(self):
        settings().set_default_dir("")
        self._refresh_labels()
        self.defaultDirChanged.emit("")

    def _clear_cache(self):
        settings().clear_cache()
        self._cache_status.setText(tr("settings.cache.cleared"))
        from PySide6.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self._cache_status.setText(""))

    def _confirm_reset(self):
        from PySide6.QtWidgets import QMessageBox
        ans = QMessageBox.question(
            self, tr("dialog.confirm"), tr("dialog.reset.confirm"),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if ans == QMessageBox.Yes:
            self.resetRequested.emit()

    def _refresh_labels(self):
        p = settings().get_default_dir()
        self._folder_label.setText(p if p else tr("settings.folder.none"))
        self._audio_label.setText(
            settings().get_audio_device() or tr("settings.audio.none")
        )

    def retranslate(self, _lang: str = ""):
        self._lang_title.setText(tr("settings.lang"))
        self._appearance_title.setText(tr("settings.appearance"))
        self._accent_label.setText(tr("settings.accent"))
        self._btn_color.setText(tr("settings.accent.pick"))
        self._bg_label.setText(tr("settings.bg"))
        self._btn_bg_pick.setText(tr("settings.bg.pick"))
        self._btn_bg_reset.setText(tr("settings.bg.reset"))
        self._vbg_label.setText(tr("settings.video_bg"))
        self._btn_vbg_pick.setText(tr("settings.video_bg.pick"))
        self._btn_vbg_reset.setText(tr("settings.video_bg.reset"))
        self._remember_cb.setText(tr("settings.remember_position"))
        self._fps_cb.setText(tr("settings.fps_overlay"))
        self._audio_title.setText(tr("settings.audio"))
        self._btn_audio.setText(tr("settings.audio.pick"))
        self._hotkeys_title.setText(tr("settings.hotkeys"))
        self._btn_hotkeys.setText(tr("settings.hotkeys.edit"))
        self._profile_title.setText(tr("settings.profile"))
        self._btn_export.setText(tr("settings.profile.export"))
        self._btn_import.setText(tr("settings.profile.import"))
        self._folder_title.setText(tr("settings.folder"))
        self._btn_folder_pick.setText(tr("settings.folder.pick"))
        self._btn_folder_reset.setText(tr("settings.folder.reset"))
        self._cache_title.setText(tr("settings.cache"))
        self._btn_cache.setText(tr("settings.cache.clear"))
        self._danger_title.setText(tr("settings.danger"))
        self._danger_desc.setText(tr("settings.reset.desc"))
        self._btn_reset.setText(tr("settings.reset.button"))
        self._refresh_labels()