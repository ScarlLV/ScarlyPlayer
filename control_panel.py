# ui/control_panel.py
"""
Нижняя панель ScarlyPlayer:
Play/Pause, Stop, seek-слайдер, громкость, кнопка «Открыть файл».
Поддерживает локализацию, папку по умолчанию, сохранение громкости.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QSlider, QLabel, QFileDialog,
)

from core.i18n import tr, translator
from core.settings import settings


# ------------------------------------------------------------
#  Форматирование времени
# ------------------------------------------------------------
def _fmt(ms: int) -> str:
    s = max(0, int(ms) // 1000)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


class ControlPanel(QWidget):
    """
    Панель управления воспроизведением.

    Сигналы:
        openRequested(str)  — выбран путь к файлу
        playToggled()       — нажата кнопка Play/Pause
        seeked(int)         — пользователь дёрнул seek-слайдер (мс)
        volumeChanged(int)  — изменилась громкость (0..100)
    """

    openRequested = Signal(str)
    playToggled   = Signal()
    seeked        = Signal(int)
    volumeChanged = Signal(int)

    def __init__(self):
        super().__init__()
        self.setObjectName("ControlPanel")
        self.setFixedHeight(110)

        self._is_playing: bool = False
        self._seeking:    bool = False

        self._build_ui()

        # реакция на смену языка
        translator().languageChanged.connect(self.retranslate)

    # --------------------------------------------------------
    #  Построение UI
    # --------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 10, 16, 12)
        root.setSpacing(8)

        # =============== ROW 1: seek ===============
        seek_row = QHBoxLayout()
        seek_row.setSpacing(10)

        self.time_current = QLabel("00:00")
        self.time_current.setObjectName("TimeLabel")

        self.time_total = QLabel("00:00")
        self.time_total.setObjectName("TimeLabel")

        self.seek = QSlider(Qt.Horizontal)
        self.seek.setRange(0, 0)
        self.seek.sliderMoved.connect(self.seeked)
        self.seek.sliderPressed.connect(self._on_seek_pressed)
        self.seek.sliderReleased.connect(self._on_seek_released)

        seek_row.addWidget(self.time_current)
        seek_row.addWidget(self.seek, 1)
        seek_row.addWidget(self.time_total)
        root.addLayout(seek_row)

        # =============== ROW 2: buttons ===============
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        # --- открыть файл ---
        self.btn_open = QPushButton(tr("btn.open"))
        self.btn_open.setObjectName("CtrlBtn")
        self.btn_open.setCursor(Qt.PointingHandCursor)
        self.btn_open.clicked.connect(self._pick_file)

        # --- play / pause ---
        self.btn_play = QPushButton(tr("btn.play"))
        self.btn_play.setObjectName("PlayBtn")
        self.btn_play.setCursor(Qt.PointingHandCursor)
        self.btn_play.setFixedWidth(140)
        self.btn_play.clicked.connect(self.playToggled)

        # --- stop ---
        self.btn_stop = QPushButton(tr("btn.stop"))
        self.btn_stop.setObjectName("CtrlBtn")
        self.btn_stop.setCursor(Qt.PointingHandCursor)
        self.btn_stop.setFixedWidth(50)

        # --- громкость ---
        self._vol_icon = QLabel(tr("label.volume"))

        self.volume = QSlider(Qt.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(settings().get_volume())
        self.volume.setFixedWidth(120)
        self.volume.valueChanged.connect(self.volumeChanged)

        # --- сборка ряда ---
        btn_row.addWidget(self.btn_open)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_stop)
        btn_row.addWidget(self.btn_play)
        btn_row.addStretch()
        btn_row.addWidget(self._vol_icon)
        btn_row.addWidget(self.volume)
        root.addLayout(btn_row)

    # --------------------------------------------------------
    #  Обработчики
    # --------------------------------------------------------
    def _on_seek_pressed(self):
        self._seeking = True

    def _on_seek_released(self):
        self._seeking = False

    def _pick_file(self):
        """Диалог выбора видео. Стартовая папка — из настроек."""
        start_dir = settings().get_default_dir() or ""
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr("dialog.openVideo"),
            start_dir,
            tr("dialog.videoFilt"),
        )
        if path:
            self.openRequested.emit(path)

    # --------------------------------------------------------
    #  Публичный API
    # --------------------------------------------------------
    def set_duration(self, ms: int):
        self.seek.setRange(0, int(ms))
        self.time_total.setText(_fmt(ms))

    def set_position(self, ms: int):
        if not self._seeking:
            self.seek.setValue(int(ms))
            self.time_current.setText(_fmt(ms))

    def set_playing(self, playing: bool):
        self._is_playing = playing
        self._update_play_text()

    # --------------------------------------------------------
    #  Локализация
    # --------------------------------------------------------
    def retranslate(self, _lang: str = ""):
        self.btn_open.setText(tr("btn.open"))
        self.btn_stop.setText(tr("btn.stop"))
        self._vol_icon.setText(tr("label.volume"))
        self._update_play_text()

    def _update_play_text(self):
        self.btn_play.setText(
            tr("btn.pause") if self._is_playing else tr("btn.play")
        )