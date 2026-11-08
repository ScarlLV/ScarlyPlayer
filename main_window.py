# ui/main_window.py
"""Главное окно ScarlyPlayer v1.0 — финальная сборка."""
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QGraphicsOpacityEffect, QStackedWidget
)
from PySide6.QtMultimediaWidgets import QVideoWidget

from core.i18n import translator
from core.player import ScarlyPlayer
from core.settings import settings
from ui.title_bar import TitleBar
from ui.sidebar import Sidebar
from ui.control_panel import ControlPanel
from ui.library_page import LibraryPage
from ui.settings_page import SettingsPage
from ui.about_page import AboutPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ScarlyPlayer")
        self.resize(1200, 720)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # ----- корень -----
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.title_bar = TitleBar(self)
        outer.addWidget(self.title_bar)

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        outer.addWidget(body, 1)

        self.sidebar = Sidebar()
        body_layout.addWidget(self.sidebar)

        # ----- стек страниц -----
        self.stack = QStackedWidget()
        body_layout.addWidget(self.stack, 1)

        # страницы
        self._player_page = self._build_player_page()
        self._library_page = LibraryPage()
        self._settings_page = SettingsPage()
        self._about_page = AboutPage()

        self.stack.addWidget(self._player_page)   # 0
        self.stack.addWidget(self._library_page)  # 1
        self.stack.addWidget(self._settings_page) # 2
        self.stack.addWidget(self._about_page)    # 3

        self.sidebar.pageRequested.connect(self._on_nav)

        # ----- плеер -----
        self.player = ScarlyPlayer(self)
        self.player.attach_video_widget(self.video_widget)

        # восстановить громкость
        vol = settings().get_volume()
        self.controls.volume.setValue(vol)
        self.player.set_volume(vol)

        # ----- связи -----
        self.controls.openRequested.connect(self._on_open)
        self.controls.playToggled.connect(self.player.toggle)
        self.controls.seeked.connect(self.player.set_position)
        self.controls.volumeChanged.connect(self._on_volume)
        self.controls.btn_stop.clicked.connect(self.player.stop)

        self.player.durationChanged.connect(self.controls.set_duration)
        self.player.positionChanged.connect(self.controls.set_position)
        self.player.playingChanged.connect(self.controls.set_playing)

        # библиотека → плеер
        self._library_page.playRequested.connect(self._on_open)

        # сохраняем язык при смене (на случай, если кто-то поменяет из settings_page)
        self._settings_page.languageChanged.connect(self._on_language_changed)

    # ---------- builders ----------
    def _build_player_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 0)
        layout.setSpacing(12)

        video_frame = QFrame()
        video_frame.setObjectName("VideoContainer")
        vf = QVBoxLayout(video_frame)
        vf.setContentsMargins(0, 0, 0, 0)

        self.video_widget = QVideoWidget()
        vf.addWidget(self.video_widget)

        self._opacity = QGraphicsOpacityEffect(self.video_widget)
        self.video_widget.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(1.0)

        layout.addWidget(video_frame, 1)

        self.controls = ControlPanel()
        layout.addWidget(self.controls)
        return page

    # ---------- handlers ----------
    def _on_nav(self, key: str):
        mapping = {"player": 0, "library": 1, "settings": 2, "about": 3}
        self.stack.setCurrentIndex(mapping.get(key, 0))

    def _on_open(self, path: str):
        # добавляем в библиотеку автоматически
        self._library_page.add_paths([path])
        self.player.load(path)
        self.player.play()
        self.stack.setCurrentIndex(0)
        self.sidebar.set_current("player")
        self._fade_in_video()

    def _on_volume(self, value: int):
        self.player.set_volume(value)
        settings().set_volume(value)

    def _on_language_changed(self, code: str):
        settings().set_language(code)

    def _fade_in_video(self):
        anim = QPropertyAnimation(self._opacity, b"opacity", self)
        anim.setDuration(400)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start(QPropertyAnimation.DeleteWhenStopped)
        self._anim = anim