# ui/player_page.py
"""Страница плеера с пустым состоянием + каруселью плейлиста."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QLabel, QPushButton,
    QGraphicsOpacityEffect, QStackedWidget
)
from PySide6.QtMultimediaWidgets import QVideoWidget

from core.i18n import tr, translator
from core.icons import load_svg_icon
from ui.control_panel import ControlPanel
from ui.playlist_carousel import PlaylistCarousel


class PlayerPage(QWidget):
    openRequested = Signal(str)
    playToggled = Signal()
    seeked = Signal(int)
    volumeChanged = Signal(int)
    speedChanged = Signal(float)
    aspectChanged = Signal(str)
    fullscreenToggled = Signal()
    infoRequested = Signal()
    carouselItemClicked = Signal(int)  # индекс в плейлисте

    def __init__(self):
        super().__init__()
        self._build_ui()
        translator().languageChanged.connect(self.retranslate)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 0)
        root.setSpacing(8)
        self.setStyleSheet("background: transparent;")

        # Видео-контейнер
        self._video_frame = QFrame()
        self._video_frame.setObjectName("VideoContainer")
        self._video_frame.setStyleSheet(
            "QFrame#VideoContainer { background: #000000; border-radius: 12px; }"
        )
        vf = QVBoxLayout(self._video_frame)
        vf.setContentsMargins(0, 0, 0, 0)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background: transparent;")

        self._empty_widget = self._build_empty_state()
        self._stack.addWidget(self._empty_widget)

        self.video_widget = QVideoWidget()
        self._opacity = QGraphicsOpacityEffect(self.video_widget)
        self.video_widget.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(1.0)
        self._stack.addWidget(self.video_widget)

        vf.addWidget(self._stack)

        # FPS-оверлей
        self.fps_label = QLabel(self._video_frame)
        self.fps_label.setText("")
        self.fps_label.setStyleSheet(
            "background: rgba(0,0,0,180); color: #00FF00; "
            "padding: 4px 8px; border-radius: 4px; "
            "font-family: Consolas; font-size: 11px;"
        )
        self.fps_label.move(10, 10)
        self.fps_label.hide()

        # Буферизация
        self.buffering_label = QLabel(self._video_frame)
        self.buffering_label.setText(tr("player.buffering"))
        self.buffering_label.setStyleSheet(
            "background: rgba(0,0,0,200); color: white; "
            "padding: 8px 16px; border-radius: 8px; "
            "font-size: 14px; font-weight: 600;"
        )
        self.buffering_label.setAlignment(Qt.AlignCenter)
        self.buffering_label.hide()

        root.addWidget(self._video_frame, 1)

        # ============ КАРУСЕЛЬ ПЛЕЙЛИСТА ============
        self.carousel = PlaylistCarousel()
        self.carousel.itemClicked.connect(self.carouselItemClicked)
        root.addWidget(self.carousel)

        # Панель управления
        self.controls = ControlPanel()
        self.controls.fullscreenToggled.connect(self.fullscreenToggled)
        self.controls.infoRequested.connect(self.infoRequested)
        self.controls.playToggled.connect(self.playToggled)
        self.controls.seeked.connect(self.seeked)
        self.controls.volumeChanged.connect(self.volumeChanged)
        self.controls.speedChanged.connect(self.speedChanged)
        self.controls.aspectChanged.connect(self.aspectChanged)
        self.controls.openRequested.connect(self.openRequested)
        root.addWidget(self.controls)

        self.show_empty()

    def _build_empty_state(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: #000000;")
        lay = QVBoxLayout(w)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(20)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(load_svg_icon("play", "#E53935", 80).pixmap(80, 80))
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("background: transparent;")
        lay.addWidget(icon_lbl)

        self._empty_title = QLabel(tr("empty.title"))
        self._empty_title.setAlignment(Qt.AlignCenter)
        self._empty_title.setStyleSheet(
            "color: #F5F5F7; font-size: 20px; font-weight: 600; background: transparent;"
        )
        lay.addWidget(self._empty_title)

        self._empty_hint = QLabel(tr("empty.hint"))
        self._empty_hint.setAlignment(Qt.AlignCenter)
        self._empty_hint.setStyleSheet(
            "color: #A0A0AB; font-size: 14px; background: transparent;"
        )
        lay.addWidget(self._empty_hint)

        self._empty_btn = QPushButton("  " + tr("empty.button"))
        self._empty_btn.setIcon(load_svg_icon("open", "#FFFFFF", 18))
        self._empty_btn.setCursor(Qt.PointingHandCursor)
        self._empty_btn.setFixedSize(200, 48)
        self._empty_btn.setStyleSheet("""
            QPushButton {
                background: #E53935;
                border: none;
                border-radius: 12px;
                color: white;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover { background: #FF5252; }
            QPushButton:pressed { background: #C62828; }
        """)
        self._empty_btn.clicked.connect(self._on_empty_open)
        lay.addWidget(self._empty_btn, alignment=Qt.AlignCenter)

        return w

    def _on_empty_open(self):
        from PySide6.QtWidgets import QFileDialog
        from core.settings import settings
        start = settings().get_default_dir() or ""
        path, _ = QFileDialog.getOpenFileName(
            self, tr("dialog.openVideo"), start, tr("dialog.videoFilt")
        )
        if path:
            self.openRequested.emit(path)

    def show_empty(self):
        self._stack.setCurrentIndex(0)
        self.carousel.hide()

    def show_video(self):
        self._stack.setCurrentIndex(1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "fps_label"):
            self.fps_label.move(10, 10)
        if hasattr(self, "buffering_label") and self.buffering_label.isVisible():
            self.buffering_label.adjustSize()
            self.buffering_label.move(
                (self.video_widget.width() - self.buffering_label.width()) // 2,
                (self.video_widget.height() - self.buffering_label.height()) // 2,
            )

    def retranslate(self, _lang: str = ""):
        self._empty_title.setText(tr("empty.title"))
        self._empty_hint.setText(tr("empty.hint"))
        self._empty_btn.setText("  " + tr("empty.button"))
        self.buffering_label.setText(tr("player.buffering"))
        self.carousel.retranslate()