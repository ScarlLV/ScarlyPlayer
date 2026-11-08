# ui/main_window.py
"""Главное окно ScarlyPlayer v1.1.11 — плейлист, трей, кастомизация."""

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QPixmap, QColor, QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QGraphicsOpacityEffect, QStackedWidget, QApplication,
    QSystemTrayIcon, QMenu, QStyle
)
from PySide6.QtMultimediaWidgets import QVideoWidget

from core.i18n import translator, tr
from core.player import ScarlyPlayer
from core.settings import settings
from core.theme import apply_theme

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

        self._bg_pixmap: QPixmap | None = None
        self._sidebar_visible: bool = settings().get_sidebar_visible()
        self._load_background()

        self._playlist: list[str] = []
        self._current_index: int = -1

        self._setup_ui()
        self._setup_player_connections()
        self._setup_tray()

    # ============================================================
    #  UI
    # ============================================================
    def _setup_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.title_bar = TitleBar(self)
        self.title_bar.sidebarToggled.connect(self._toggle_sidebar)
        outer.addWidget(self.title_bar)

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        outer.addWidget(body, 1)

        self.sidebar = Sidebar()
        self.sidebar.setVisible(self._sidebar_visible)
        self.sidebar.setFixedWidth(220 if self._sidebar_visible else 0)
        body_layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")
        body_layout.addWidget(self.stack, 1)

        self._player_page = self._build_player_page()
        self._library_page = LibraryPage()
        self._settings_page = SettingsPage()
        self._about_page = AboutPage()

        self.stack.addWidget(self._player_page)    # 0
        self.stack.addWidget(self._library_page)   # 1
        self.stack.addWidget(self._settings_page)  # 2
        self.stack.addWidget(self._about_page)     # 3

        self.sidebar.pageRequested.connect(self._on_nav)
        self._library_page.playRequested.connect(self._on_open)
        self._library_page.playAllRequested.connect(self._play_all)
        self._settings_page.languageChanged.connect(self._on_language_changed)
        self._settings_page.themeChanged.connect(self._on_theme_changed)

    def _setup_player_connections(self):
        self.player = ScarlyPlayer(self)
        self.player.attach_video_widget(self.video_widget)

        vol = settings().get_volume()
        self.controls.volume.setValue(vol)
        self.player.set_volume(vol)

        self.controls.openRequested.connect(self._on_open)
        self.controls.playToggled.connect(self.player.toggle)
        self.controls.seeked.connect(self.player.set_position)
        self.controls.volumeChanged.connect(self._on_volume)
        self.controls.btn_stop.clicked.connect(self.player.stop)
        self.controls.speedChanged.connect(self.player.set_playback_rate)
        self.controls.aspectChanged.connect(self.player.set_aspect_mode)

        self.player.durationChanged.connect(self.controls.set_duration)
        self.player.positionChanged.connect(self.controls.set_position)
        self.player.playingChanged.connect(self.controls.set_playing)
        self.player.mediaEnded.connect(self._play_next)

    # ============================================================
    #  Трей (ФИКС: QStyle.StandardPixmap.SP_MediaPlay)
    # ============================================================
    def _setup_tray(self):
        self.tray = QSystemTrayIcon(self)
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        self.tray.setIcon(icon)
        self.tray.setToolTip("ScarlyPlayer")

        menu = QMenu()
        action_show = menu.addAction("Развернуть")
        action_show.triggered.connect(self._show_from_tray)

        action_play = menu.addAction("Play / Pause")
        action_play.triggered.connect(self.player.toggle)

        menu.addSeparator()
        action_quit = menu.addAction("Выход")
        action_quit.triggered.connect(QApplication.quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _show_from_tray(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self._show_from_tray()

    # ============================================================
    #  Плейлист
    # ============================================================
    def _play_all(self, paths: list[str]):
        self._playlist = paths
        self._current_index = 0
        self._on_open(paths[0], add_to_playlist=False)

    def _play_next(self):
        if self._current_index + 1 < len(self._playlist):
            self._current_index += 1
            self._on_open(self._playlist[self._current_index], add_to_playlist=False)

    # ============================================================
    #  Background
    # ============================================================
    def _load_background(self):
        bg_path = settings().get_bg_image()
        self._bg_pixmap = QPixmap(bg_path) if bg_path else None

    def paintEvent(self, event):
        painter = QPainter(self)
        if self._bg_pixmap and not self._bg_pixmap.isNull():
            scaled = self._bg_pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation,
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 180))
        else:
            painter.fillRect(self.rect(), QColor("#0F0F12"))

    # ============================================================
    #  Player page
    # ============================================================
    def _build_player_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: transparent;")
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

    # ============================================================
    #  Handlers
    # ============================================================
    def _on_nav(self, key: str):
        mapping = {"player": 0, "library": 1, "settings": 2, "about": 3}
        self.stack.setCurrentIndex(mapping.get(key, 0))

    def _on_open(self, path: str, add_to_playlist: bool = True):
        self._library_page.add_paths([path])
        if add_to_playlist:
            self._playlist = [path]
            self._current_index = 0

        self.player.load(path)
        self.player.play()
        self.stack.setCurrentIndex(0)
        self.sidebar.set_current("player")
        self._fade_in_video()

        # Обновляем tooltip трея
        filename = path.replace("\\", "/").split("/")[-1]
        self.tray.setToolTip(f"ScarlyPlayer — {filename}")

    def _on_volume(self, value: int):
        self.player.set_volume(value)
        settings().set_volume(value)

    def _on_language_changed(self, code: str):
        settings().set_language(code)

    def _on_theme_changed(self):
        self._load_background()
        app = QApplication.instance()
        if app:
            apply_theme(app)
        self.update()

    def _toggle_sidebar(self):
        self._sidebar_visible = not self._sidebar_visible
        settings().set_sidebar_visible(self._sidebar_visible)

        start_w = self.sidebar.width()
        end_w = 220 if self._sidebar_visible else 0

        self.sidebar.setVisible(True)

        anim_min = QPropertyAnimation(self.sidebar, b"minimumWidth", self)
        anim_min.setDuration(250)
        anim_min.setStartValue(start_w)
        anim_min.setEndValue(end_w)
        anim_min.setEasingCurve(QEasingCurve.InOutCubic)

        anim_max = QPropertyAnimation(self.sidebar, b"maximumWidth", self)
        anim_max.setDuration(250)
        anim_max.setStartValue(start_w)
        anim_max.setEndValue(end_w)
        anim_max.setEasingCurve(QEasingCurve.InOutCubic)

        if not self._sidebar_visible:
            anim_min.finished.connect(lambda: self.sidebar.setVisible(False))

        self._anim_sidebar_min = anim_min
        self._anim_sidebar_max = anim_max
        anim_min.start()
        anim_max.start()

    def _fade_in_video(self):
        anim = QPropertyAnimation(self._opacity, b"opacity", self)
        anim.setDuration(400)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start(QPropertyAnimation.DeleteWhenStopped)
        self._anim = anim