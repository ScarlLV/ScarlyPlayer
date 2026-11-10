# ui/control_panel.py
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSlider, QLabel, QFileDialog, QComboBox
)
from PySide6.QtGui import QIcon

from core.i18n import tr, translator
from core.settings import settings
from core.icons import load_svg_icon


def _fmt(ms: int) -> str:
    s = max(0, int(ms) // 1000)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


class HoverButton(QPushButton):
    """Кнопка с плавной анимацией тени/opacity при ховере."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(150)
        self._base_opacity = 1.0

    def enterEvent(self, event):
        super().enterEvent(event)
        self._anim.stop()
        self._anim.setStartValue(self.windowOpacity())
        self._anim.setEndValue(1.0)
        self._anim.start()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._anim.stop()
        self._anim.setStartValue(self.windowOpacity())
        self._anim.setEndValue(0.92)
        self._anim.start()


class ControlPanel(QWidget):
    openRequested = Signal(str)
    playToggled   = Signal()
    seeked        = Signal(int)
    volumeChanged = Signal(int)
    speedChanged  = Signal(float)
    aspectChanged = Signal(str)
    fullscreenToggled = Signal()
    infoRequested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("ControlPanel")
        self.setFixedHeight(110)
        self._is_playing = False
        self._seeking = False
        self._show_remaining = False  # B4: показывать оставшееся?
        self._total_dur = 0
        self._current_pos = 0

        self._build_ui()
        translator().languageChanged.connect(self.retranslate)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 10, 16, 12)
        root.setSpacing(8)

        # ============ ROW 1: seek ============
        seek_row = QHBoxLayout()
        seek_row.setSpacing(10)

        self.time_current = QLabel("00:00")
        self.time_current.setObjectName("TimeLabel")
        self.time_current.setCursor(Qt.PointingHandCursor)
        self.time_current.setToolTip("Клик — переключить оставшееся/текущее")
        # B4: клик по текущему времени переключает режим
        # (обработка через mousePressEvent)
        self.time_current.mousePressEvent = self._on_time_clicked

        self.time_total = QLabel("00:00")
        self.time_total.setObjectName("TimeLabel")

        self.seek = QSlider(Qt.Horizontal)
        self.seek.setRange(0, 0)
        self.seek.sliderMoved.connect(self.seeked)
        self.seek.sliderPressed.connect(lambda: setattr(self, "_seeking", True))
        self.seek.sliderReleased.connect(lambda: setattr(self, "_seeking", False))

        seek_row.addWidget(self.time_current)
        seek_row.addWidget(self.seek, 1)
        seek_row.addWidget(self.time_total)
        root.addLayout(seek_row)

        # ============ ROW 2: buttons ============
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        # Open (SVG)
        self.btn_open = HoverButton()
        self.btn_open.setObjectName("CtrlBtn")
        self.btn_open.setIcon(load_svg_icon("open", "#F5F5F7", 20))
        self.btn_open.setText("  " + tr("btn.open").replace("📂 ", ""))
        self.btn_open.clicked.connect(self._pick_file)

        # Stop (SVG)
        self.btn_stop = HoverButton()
        self.btn_stop.setObjectName("CtrlBtn")
        self.btn_stop.setFixedWidth(50)
        self.btn_stop.setIcon(load_svg_icon("stop", "#F5F5F7", 18))

        # Play / Pause (SVG)
        self.btn_play = HoverButton()
        self.btn_play.setObjectName("PlayBtn")
        self.btn_play.setFixedWidth(150)
        self.btn_play.setIcon(load_svg_icon("play", "#FFFFFF", 18))
        self.btn_play.setText("  " + tr("btn.play").replace("▶ ", ""))
        self.btn_play.clicked.connect(self.playToggled)

        # Info (SVG)
        self.btn_info = HoverButton()
        self.btn_info.setObjectName("CtrlBtn")
        self.btn_info.setFixedWidth(40)
        self.btn_info.setIcon(load_svg_icon("info", "#F5F5F7", 18))
        self.btn_info.clicked.connect(self.infoRequested)

        # Fullscreen (SVG)
        self.btn_fullscreen = HoverButton()
        self.btn_fullscreen.setObjectName("CtrlBtn")
        self.btn_fullscreen.setFixedWidth(40)
        self.btn_fullscreen.setIcon(load_svg_icon("fullscreen", "#F5F5F7", 18))
        self.btn_fullscreen.clicked.connect(self.fullscreenToggled)

        # Speed / Aspect
        self.speed_combo = QComboBox()
        self.speed_combo.setObjectName("CtrlBtn")
        self.speed_combo.setFixedWidth(80)
        self.speed_combo.addItems(["0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x"])
        self.speed_combo.setCurrentText("1.0x")
        self.speed_combo.currentTextChanged.connect(
            lambda t: self.speedChanged.emit(float(t.replace("x", "")))
        )

        self.aspect_combo = QComboBox()
        self.aspect_combo.setObjectName("CtrlBtn")
        self.aspect_combo.setFixedWidth(100)
        self.aspect_combo.addItems(["Fit", "Fill", "Stretch"])
        self.aspect_combo.currentTextChanged.connect(
            lambda t: self.aspectChanged.emit(t.lower())
        )

        # Volume (SVG icon + slider)
        self._vol_icon = QLabel()
        self._vol_icon.setPixmap(load_svg_icon("volume", "#A0A0AB", 18).pixmap(18, 18))
        self._vol_icon.setStyleSheet("background: transparent; padding-right: 4px;")

        self.volume = QSlider(Qt.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(settings().get_volume())
        self.volume.setFixedWidth(120)
        self.volume.valueChanged.connect(self.volumeChanged)

        btn_row.addWidget(self.btn_open)
        btn_row.addWidget(self.btn_stop)
        btn_row.addWidget(self.btn_play)
        btn_row.addWidget(self.btn_info)
        btn_row.addWidget(self.btn_fullscreen)
        btn_row.addWidget(self.speed_combo)
        btn_row.addWidget(self.aspect_combo)
        btn_row.addStretch()
        btn_row.addWidget(self._vol_icon)
        btn_row.addWidget(self.volume)
        root.addLayout(btn_row)

    def _pick_file(self):
        start = settings().get_default_dir() or ""
        path, _ = QFileDialog.getOpenFileName(
            self, tr("dialog.openVideo"), start, tr("dialog.videoFilt")
        )
        if path:
            self.openRequested.emit(path)

    def _on_time_clicked(self, event):
        """B4: клик по текущему времени — переключение режима."""
        self._show_remaining = not self._show_remaining
        self._refresh_time_labels()

    def _refresh_time_labels(self):
        if self._show_remaining:
            remaining = max(0, self._total_dur - self._current_pos)
            self.time_current.setText(f"-{_fmt(remaining)}")
        else:
            self.time_current.setText(_fmt(self._current_pos))

    def set_duration(self, ms: int):
        self._total_dur = int(ms)
        self.seek.setRange(0, self._total_dur)
        self.time_total.setText(_fmt(ms))
        self._refresh_time_labels()

    def set_position(self, ms: int):
        self._current_pos = int(ms)
        if not self._seeking:
            self.seek.setValue(self._current_pos)
            self._refresh_time_labels()

    def set_playing(self, playing: bool):
        self._is_playing = playing
        if playing:
            self.btn_play.setIcon(load_svg_icon("pause", "#FFFFFF", 18))
            self.btn_play.setText("  " + tr("btn.pause").replace("⏸ ", ""))
        else:
            self.btn_play.setIcon(load_svg_icon("play", "#FFFFFF", 18))
            self.btn_play.setText("  " + tr("btn.play").replace("▶ ", ""))

    def retranslate(self, _lang: str = ""):
        self.btn_open.setText("  " + tr("btn.open").replace("📂 ", ""))
        self.set_playing(self._is_playing)