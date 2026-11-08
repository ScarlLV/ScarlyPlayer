# ui/main_window.py
"""Главное окно ScarlyPlayer v1.2.22."""

import os
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QUrl
from PySide6.QtGui import QPainter, QPixmap, QColor, QKeySequence, QShortcut, QCursor
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QGraphicsOpacityEffect, QStackedWidget, QApplication,
    QSystemTrayIcon, QMenu, QStyle, QLabel
)
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

from core.i18n import translator, tr, APP_VERSION
from core.player import ScarlyPlayer
from core.settings import settings
from core.theme import apply_theme
from ui.toast import Toast
from ui.info_dialog import InfoDialog

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
        self._is_fullscreen = False
        self._load_background()

        self._playlist: list[str] = []
        self._current_index: int = -1

        # Видео-фон
        self._bg_player: QMediaPlayer | None = None
        self._bg_audio: QAudioOutput | None = None

        self._setup_ui()
        self._setup_player_connections()
        self._setup_tray()
        self._setup_hotkeys()
        self._setup_cursor_timer()
        self._setup_video_background()

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

        self.stack.addWidget(self._player_page)
        self.stack.addWidget(self._library_page)
        self.stack.addWidget(self._settings_page)
        self.stack.addWidget(self._about_page)

        self.sidebar.pageRequested.connect(self._on_nav)
        self._library_page.playRequested.connect(self._on_open)
        self._library_page.playAllRequested.connect(self._play_all)
        self._settings_page.languageChanged.connect(self._on_language_changed)
        self._settings_page.themeChanged.connect(self._on_theme_changed)
        self._settings_page.resetRequested.connect(self._on_reset_all)
        self._settings_page.bgVideoChanged.connect(self._setup_video_background)

    def _build_player_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 0)
        layout.setSpacing(12)

        # Видео-фрейм с оверлеями
        video_frame = QFrame()
        video_frame.setObjectName("VideoContainer")
        video_frame.setStyleSheet("QFrame#VideoContainer { background: #000000; border-radius: 12px; }")
        vf = QVBoxLayout(video_frame)
        vf.setContentsMargins(0, 0, 0, 0)

        self.video_widget = QVideoWidget()
        vf.addWidget(self.video_widget)

        self._opacity = QGraphicsOpacityEffect(self.video_widget)
        self.video_widget.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(1.0)

        # FPS-оверлей (поверх видео)
        self.fps_label = QLabel(video_frame)
        self.fps_label.setText("")
        self.fps_label.setStyleSheet(
            "background: rgba(0,0,0,180); color: #0F0; "
            "padding: 4px 8px; border-radius: 4px; font-family: Consolas; font-size: 11px;"
        )
        self.fps_label.move(10, 10)
        self.fps_label.hide()

        # Индикатор буферизации
        self.buffering_label = QLabel(video_frame)
        self.buffering_label.setText(tr("player.buffering"))
        self.buffering_label.setStyleSheet(
            "background: rgba(0,0,0,200); color: white; "
            "padding: 8px 16px; border-radius: 8px; font-size: 14px; font-weight: 600;"
        )
        self.buffering_label.setAlignment(Qt.AlignCenter)
        self.buffering_label.hide()

        layout.addWidget(video_frame, 1)

        self.controls = ControlPanel()
        self.controls.fullscreenToggled.connect(self._toggle_fullscreen)
        self.controls.infoRequested.connect(self._show_video_info)
        layout.addWidget(self.controls)
        return page

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
        self.player.bufferingChanged.connect(self._on_buffering)
        self.player.fpsUpdated.connect(self._on_fps)

        # Показывать/скрывать FPS
        if settings().get_fps_overlay():
            self.fps_label.show()

    def _setup_tray(self):
        self.tray = QSystemTrayIcon(self)
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        self.tray.setIcon(icon)
        self.tray.setToolTip("ScarlyPlayer")

        menu = QMenu()
        action_show = menu.addAction("Развернуть")
        action_show.triggered.connect(self._show_from_tray)
        action_play = menu.addAction("Play/Pause")
        action_play.triggered.connect(self.player.toggle)
        menu.addSeparator()
        action_quit = menu.addAction("Выход")
        action_quit.triggered.connect(QApplication.quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda r: self._show_from_tray() if r == QSystemTrayIcon.Trigger else None)
        self.tray.show()

    def _show_from_tray(self):
        self.showNormal(); self.raise_(); self.activateWindow()

    # ============================================================
    #  ВИДЕО-ФОН
    # ============================================================
    def _setup_video_background(self):
        path = settings().get_bg_video()
        # Останавливаем предыдущий
        if self._bg_player:
            self._bg_player.stop()
            self._bg_player = None

        if not path or not os.path.exists(path):
            return

        # Создаём фоновый QVideoWidget
        if not hasattr(self, "_bg_video_widget"):
            self._bg_video_widget = QVideoWidget(self)
            self._bg_video_widget.setAttribute(Qt.WA_TransparentForMouseEvents)
            self._bg_video_widget.setStyleSheet("background: black;")
            self._bg_video_widget.setGeometry(self.rect())
            self._bg_video_widget.lower()

        self._bg_player = QMediaPlayer(self)
        self._bg_audio = QAudioOutput(self)
        self._bg_audio.setVolume(0)
        self._bg_player.setAudioOutput(self._bg_audio)
        self._bg_player.setVideoOutput(self._bg_video_widget)
        self._bg_player.setSource(QUrl.fromLocalFile(path))
        self._bg_player.setLoops(QMediaPlayer.Infinite)
        self._bg_player.play()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "_bg_video_widget"):
            self._bg_video_widget.setGeometry(self.rect())
        # Перемещаем оверлеи
        if hasattr(self, "fps_label"):
            self.fps_label.move(10, 10)
        if hasattr(self, "buffering_label"):
            self.buffering_label.adjustSize()
            self.buffering_label.move(
                (self.video_widget.width() - self.buffering_label.width()) // 2,
                (self.video_widget.height() - self.buffering_label.height()) // 2
            )

    # ============================================================
    #  ХОТКЕИ
    # ============================================================
    def _setup_hotkeys(self):
        QShortcut(QKeySequence("Space"), self, self.player.toggle)
        QShortcut(QKeySequence("Left"), self, lambda: self.player.smart_seek(False, False))
        QShortcut(QKeySequence("Right"), self, lambda: self.player.smart_seek(True, False))
        QShortcut(QKeySequence("Shift+Left"), self, lambda: self.player.smart_seek(False, True))
        QShortcut(QKeySequence("Shift+Right"), self, lambda: self.player.smart_seek(True, True))
        QShortcut(QKeySequence("F"), self, self._toggle_fullscreen)
        QShortcut(QKeySequence("F11"), self, self._toggle_fullscreen)
        QShortcut(QKeySequence("Esc"), self, self._exit_fullscreen)
        QShortcut(QKeySequence("M"), self, lambda: self.controls.volume.setValue(0 if self.controls.volume.value() > 0 else 80))
        QShortcut(QKeySequence("Ctrl+O"), self, self.controls._pick_file)

    # ============================================================
    #  КУРСОР (исчезновение при бездействии)
    # ============================================================
    def _setup_cursor_timer(self):
        self._cursor_timer = QTimer(self)
        self._cursor_timer.setSingleShot(True)
        self._cursor_timer.setInterval(2000)
        self._cursor_timer.timeout.connect(self._hide_cursor)

    def _hide_cursor(self):
        if self._is_fullscreen and self._on_video_area():
            QApplication.setOverrideCursor(Qt.BlankCursor)

    def _on_video_area(self) -> bool:
        from PySide6.QtGui import QCursor
        pos = self.mapFromGlobal(QCursor.pos())
        return self.video_widget.geometry().contains(pos)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        QApplication.restoreOverrideCursor()
        self._cursor_timer.start()

    # ============================================================
    #  ПОЛНОЭКРАННЫЙ
    # ============================================================
    def _toggle_fullscreen(self):
        if self._is_fullscreen:
            self._exit_fullscreen()
        else:
            self._is_fullscreen = True
            self.title_bar.hide()
            self.sidebar.hide()
            self.showFullScreen()
            self.controls.hide()
            QApplication.restoreOverrideCursor()
            self._cursor_timer.start()
            Toast(self, "Полный экран (F / Esc — выход)")

    def _exit_fullscreen(self):
        if not self._is_fullscreen: return
        self._is_fullscreen = False
        QApplication.restoreOverrideCursor()
        self.showNormal()
        self.title_bar.show()
        self.controls.show()
        if self._sidebar_visible: self.sidebar.show()

    # ============================================================
    #  ИНФО
    # ============================================================
    def _show_video_info(self):
        if not self.player._current_path:
            return
        meta = self.player.get_metadata()
        dlg = InfoDialog(self, self.player._current_path, meta)
        dlg.exec()

    # ============================================================
    #  БУФЕР / FPS
    # ============================================================
    def _on_buffering(self, is_buffering: bool):
        if is_buffering:
            self.buffering_label.adjustSize()
            self.buffering_label.move(
                (self.video_widget.width() - self.buffering_label.width()) // 2,
                (self.video_widget.height() - self.buffering_label.height()) // 2
            )
            self.buffering_label.show()
        else:
            self.buffering_label.hide()

    def _on_fps(self, fps: float):
        if settings().get_fps_overlay():
            self.fps_label.setText(f"{tr('player.fps')}: {fps:.0f}")
            self.fps_label.show()
        else:
            self.fps_label.hide()

    # ============================================================
    #  НАВИГАЦИЯ
    # ============================================================
    def _on_nav(self, key: str):
        mapping = {"player": 0, "library": 1, "settings": 2, "about": 3}
        self.stack.setCurrentIndex(mapping.get(key, 0))
        # Fade
        self.stack.setWindowOpacity(0.0)
        self._fade = QPropertyAnimation(self.stack, b"windowOpacity")
        self._fade.setDuration(200)
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.start()

    # ============================================================
    #  BACKGROUND
    # ============================================================
    def _load_background(self):
        bg_path = settings().get_bg_image()
        self._bg_pixmap = QPixmap(bg_path) if bg_path else None

    def paintEvent(self, event):
        painter = QPainter(self)
        # Если есть видео-фон — не рисуем картинку (видео-виджет сам покажет)
        if self._bg_player and self._bg_player.playbackState() == QMediaPlayer.PlayingState:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 120))
            return
        if self._bg_pixmap and not self._bg_pixmap.isNull():
            scaled = self._bg_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 180))
        else:
            painter.fillRect(self.rect(), QColor("#0F0F12"))

    # ============================================================
    #  PLAYLIST
    # ============================================================
    def _play_all(self, paths: list[str]):
        self._playlist = paths; self._current_index = 0
        self._on_open(paths[0], add_to_playlist=False)

    def _play_next(self):
        if self._current_index + 1 < len(self._playlist):
            self._current_index += 1
            self._on_open(self._playlist[self._current_index], add_to_playlist=False)

    # ============================================================
    #  HANDLERS
    # ============================================================
    def _on_open(self, path: str, add_to_playlist=True):
        self._library_page.add_paths([path])
        if add_to_playlist:
            self._playlist = [path]; self._current_index = 0

        self.player.load(path)
        self.player.play()
        self.stack.setCurrentIndex(0)
        self.sidebar.set_current("player")
        self._fade_in_video()

        filename = path.replace("\\", "/").split("/")[-1]
        self.tray.setToolTip(f"ScarlyPlayer — {filename}")
        Toast(self, f"▶ {filename}", "⏸", self.player.toggle)

    def _on_volume(self, value: int):
        self.player.set_volume(value); settings().set_volume(value)

    def _on_language_changed(self, code: str):
        settings().set_language(code)

    def _on_theme_changed(self):
        self._load_background()
        app = QApplication.instance()
        if app: apply_theme(app)
        self.update()

    def _on_reset_all(self):
        settings().reset_all()
        app = QApplication.instance()
        if app: apply_theme(app)
        self._load_background()
        self._library_page._load_data()
        self._library_page._refresh()
        self.update()
        Toast(self, "Настройки сброшены")

    def _toggle_sidebar(self):
        self._sidebar_visible = not self._sidebar_visible
        settings().set_sidebar_visible(self._sidebar_visible)
        start_w = self.sidebar.width()
        end_w = 220 if self._sidebar_visible else 0
        self.sidebar.setVisible(True)

        anim_min = QPropertyAnimation(self.sidebar, b"minimumWidth", self)
        anim_min.setDuration(250); anim_min.setStartValue(start_w); anim_min.setEndValue(end_w)
        anim_min.setEasingCurve(QEasingCurve.InOutCubic)

        anim_max = QPropertyAnimation(self.sidebar, b"maximumWidth", self)
        anim_max.setDuration(250); anim_max.setStartValue(start_w); anim_max.setEndValue(end_w)
        anim_max.setEasingCurve(QEasingCurve.InOutCubic)

        if not self._sidebar_visible: anim_min.finished.connect(lambda: self.sidebar.setVisible(False))
        self._anim_sidebar_min = anim_min; self._anim_sidebar_max = anim_max
        anim_min.start(); anim_max.start()

    def _fade_in_video(self):
        anim = QPropertyAnimation(self._opacity, b"opacity", self)
        anim.setDuration(400); anim.setStartValue(0.0); anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start(QPropertyAnimation.DeleteWhenStopped)
        self._anim = anim