# ui/main_window.py
"""Главное окно ScarlyPlayer v1.2.333."""

import os
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QUrl
from PySide6.QtGui import QPainter, QPixmap, QColor, QKeySequence, QShortcut
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
from core.icons import load_svg_icon, resource_path
from ui.toast import Toast
from ui.info_dialog import InfoDialog
from ui.player_page import PlayerPage

from ui.title_bar import TitleBar
from ui.sidebar import Sidebar
from ui.library_page import LibraryPage
from ui.settings_page import SettingsPage
from ui.about_page import AboutPage


class StatusBar(QWidget):
    """E1: статусбар внизу окна."""

    def __init__(self):
        super().__init__()
        self.setObjectName("StatusBar")
        self.setFixedHeight(28)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 12, 0)
        lay.setSpacing(20)

        self.lbl_file = QLabel("—")
        self.lbl_time = QLabel("")
        self.lbl_speed = QLabel("1.0x")
        self.lbl_aspect = QLabel("Fit")

        for lbl in (self.lbl_file, self.lbl_time, self.lbl_speed, self.lbl_aspect):
            lbl.setStyleSheet("color: #A0A0AB; font-size: 11px; background: transparent;")

        lay.addWidget(self.lbl_file, 1)
        lay.addWidget(self.lbl_time)
        lay.addWidget(QLabel("│"))
        lay.addWidget(self.lbl_speed)
        lay.addWidget(QLabel("│"))
        lay.addWidget(self.lbl_aspect)

        # Разделители
        for sep in self.findChildren(QLabel):
            if sep.text() == "│":
                sep.setStyleSheet("color: #2A2A33; font-size: 11px;")

    def set_file(self, name: str):
        self.lbl_file.setText(name if name else "—")

    def set_time(self, text: str):
        self.lbl_time.setText(text)

    def set_speed(self, text: str):
        self.lbl_speed.setText(text)

    def set_aspect(self, text: str):
        self.lbl_aspect.setText(text)


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
        self._current_filename: str = ""

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

        # Стек
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")
        body_layout.addWidget(self.stack, 1)

        self._player_page = PlayerPage()
        self._library_page = LibraryPage()
        self._settings_page = SettingsPage()
        self._about_page = AboutPage()

        self.stack.addWidget(self._player_page)
        self.stack.addWidget(self._library_page)
        self.stack.addWidget(self._settings_page)
        self.stack.addWidget(self._about_page)

        # E1: статусбар
        self.status_bar = StatusBar()
        outer.addWidget(self.status_bar)

        # Сигналы
        self.sidebar.pageRequested.connect(self._on_nav)
        self._player_page.openRequested.connect(self._on_open)
        self._library_page.playRequested.connect(self._on_open)
        self._library_page.playAllRequested.connect(self._play_all)
        self._settings_page.languageChanged.connect(self._on_language_changed)
        self._settings_page.themeChanged.connect(self._on_theme_changed)
        self._settings_page.resetRequested.connect(self._on_reset_all)
        self._settings_page.bgVideoChanged.connect(self._setup_video_background)

    def _setup_player_connections(self):
        self.player = ScarlyPlayer(self)
        self.player.attach_video_widget(self._player_page.video_widget)

        controls = self._player_page.controls
        vol = settings().get_volume()
        controls.volume.setValue(vol)
        self.player.set_volume(vol)

        self._player_page.playToggled.connect(self.player.toggle)
        self._player_page.seeked.connect(self.player.set_position)
        self._player_page.volumeChanged.connect(self._on_volume)
        self._player_page.speedChanged.connect(self._on_speed_changed)
        self._player_page.aspectChanged.connect(self._on_aspect_changed)
        self._player_page.fullscreenToggled.connect(self._toggle_fullscreen)
        self._player_page.infoRequested.connect(self._show_video_info)

        controls.btn_stop.clicked.connect(self.player.stop)

        self.player.durationChanged.connect(controls.set_duration)
        self.player.positionChanged.connect(self._on_position)
        self.player.playingChanged.connect(controls.set_playing)
        self.player.mediaEnded.connect(self._play_next)
        self.player.bufferingChanged.connect(self._on_buffering)
        self.player.fpsUpdated.connect(self._on_fps)

        if settings().get_fps_overlay():
            self._player_page.fps_label.show()

    def _on_position(self, ms: int):
        self._player_page.controls.set_position(ms)
        # E1: обновляем статусбар
        dur = self.player._player.duration()
        if dur > 0:
            s = ms // 1000
            m, s = divmod(s, 60)
            h, m = divmod(m, 60)
            tstr = f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
            self.status_bar.set_time(f"⏱ {tstr}")

    def _on_speed_changed(self, rate: float):
        self.player.set_playback_rate(rate)
        self.status_bar.set_speed(f"{rate:.2f}x")

    def _on_aspect_changed(self, mode: str):
        self.player.set_aspect_mode(mode)
        self.status_bar.set_aspect(mode.capitalize())

    def _setup_tray(self):
        self.tray = QSystemTrayIcon(self)
        icon_path = resource_path("assets/icon.png")
        from PySide6.QtGui import QIcon
        if os.path.exists(icon_path):
            self.tray.setIcon(QIcon(icon_path))
        else:
            self.tray.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
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
        if self._bg_player:
            self._bg_player.stop()
            self._bg_player = None

        if not path or not os.path.exists(path):
            return

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
        QShortcut(QKeySequence("M"), self, lambda: self._player_page.controls.volume.setValue(
            0 if self._player_page.controls.volume.value() > 0 else 80
        ))
        QShortcut(QKeySequence("Ctrl+O"), self, self._player_page.controls._pick_file)

    # ============================================================
    #  КУРСОР
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
        return self._player_page.video_widget.geometry().contains(pos)

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
            self.status_bar.hide()
            self.showFullScreen()
            self._player_page.controls.hide()
            QApplication.restoreOverrideCursor()
            self._cursor_timer.start()
            Toast(self, "Полный экран (F / Esc — выход)")

    def _exit_fullscreen(self):
        if not self._is_fullscreen:
            return
        self._is_fullscreen = False
        QApplication.restoreOverrideCursor()
        self.showNormal()
        self.title_bar.show()
        self.status_bar.show()
        self._player_page.controls.show()
        if self._sidebar_visible:
            self.sidebar.show()

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
        lbl = self._player_page.buffering_label
        if is_buffering:
            lbl.adjustSize()
            lbl.move(
                (self._player_page.video_widget.width() - lbl.width()) // 2,
                (self._player_page.video_widget.height() - lbl.height()) // 2,
            )
            lbl.show()
        else:
            lbl.hide()

    def _on_fps(self, fps: float):
        lbl = self._player_page.fps_label
        if settings().get_fps_overlay():
            lbl.setText(f"{tr('player.fps')}: {fps:.0f}")
            lbl.show()
        else:
            lbl.hide()

    # ============================================================
    #  НАВИГАЦИЯ
    # ============================================================
    def _on_nav(self, key: str):
        mapping = {"player": 0, "library": 1, "settings": 2, "about": 3}
        self.stack.setCurrentIndex(mapping.get(key, 0))
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
        if self._bg_player and self._bg_player.playbackState() == QMediaPlayer.PlayingState:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 120))
            return
        if self._bg_pixmap and not self._bg_pixmap.isNull():
            scaled = self._bg_pixmap.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
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
        self._playlist = paths
        self._current_index = 0
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
            self._playlist = [path]
            self._current_index = 0

        self.player.load(path)
        self.player.play()
        self.stack.setCurrentIndex(0)
        self.sidebar.set_current("player")
        self._player_page.show_video()
        self._fade_in_video()

        filename = path.replace("\\", "/").split("/")[-1]
        self._current_filename = filename
        self.tray.setToolTip(f"ScarlyPlayer — {filename}")
        self.status_bar.set_file(filename)
        self.setWindowTitle(f"⚡ ScarlyPlayer — {filename}")
        Toast(self, f"▶ {filename}", "⏸", self.player.toggle)

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

    def _on_reset_all(self):
        settings().reset_all()
        app = QApplication.instance()
        if app:
            apply_theme(app)
        self._load_background()
        self._library_page._load_data()
        self._library_page._refresh()
        self._player_page.show_empty()
        self.status_bar.set_file("")
        self.setWindowTitle("⚡ ScarlyPlayer")
        self.update()
        Toast(self, "Настройки сброшены")

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
        anim = QPropertyAnimation(self._player_page._opacity, b"opacity", self)
        anim.setDuration(400)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start(QPropertyAnimation.DeleteWhenStopped)
        self._anim = anim