# core/player.py
"""Логика воспроизведения ScarlyPlayer."""

from __future__ import annotations

from PySide6.QtCore import QObject, QUrl, Signal, Qt
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget


class ScarlyPlayer(QObject):
    """Обёртка над QMediaPlayer с сигналами и кастомизацией."""

    durationChanged = Signal("qlonglong")
    positionChanged = Signal("qlonglong")
    playingChanged  = Signal(bool)
    mediaLoaded     = Signal(str)
    mediaEnded      = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._player = QMediaPlayer(self)
        self._audio = QAudioOutput(self)
        self._player.setAudioOutput(self._audio)
        self._audio.setVolume(0.8)

        self._video_widget: QVideoWidget | None = None

        self._player.durationChanged.connect(self.durationChanged)
        self._player.positionChanged.connect(self.positionChanged)
        self._player.playbackStateChanged.connect(self._on_state)
        self._player.mediaStatusChanged.connect(self._on_media_status)

    # --------------------------------------------------------
    #  Видео-виджет
    # --------------------------------------------------------
    def attach_video_widget(self, widget: QVideoWidget) -> None:
        self._video_widget = widget
        self._player.setVideoOutput(widget)
        self._video_widget.setAspectRatioMode(Qt.KeepAspectRatio)

    # --------------------------------------------------------
    #  Загрузка / управление
    # --------------------------------------------------------
    def load(self, path: str) -> None:
        self._player.setSource(QUrl.fromLocalFile(path))
        filename = path.replace("\\", "/").split("/")[-1]
        self.mediaLoaded.emit(filename)

    def toggle(self) -> None:
        if self._player.playbackState() == QMediaPlayer.PlayingState:
            self._player.pause()
        else:
            self._player.play()

    def play(self):
        self._player.play()

    def pause(self):
        self._player.pause()

    def stop(self):
        self._player.stop()

    def set_position(self, ms: int) -> None:
        self._player.setPosition(int(ms))

    def set_volume(self, value: int) -> None:
        self._audio.setVolume(max(0, min(100, value)) / 100)

    # --------------------------------------------------------
    #  Скорость воспроизведения
    # --------------------------------------------------------
    def set_playback_rate(self, rate: float) -> None:
        """0.5 — 2.0"""
        self._player.setPlaybackRate(float(rate))

    # --------------------------------------------------------
    #  Соотношение сторон
    # --------------------------------------------------------
    def set_aspect_mode(self, mode: str) -> None:
        """
        'fit'     — вписать с сохранением пропорций (чёрные полосы)
        'fill'    — заполнить, обрезая края
        'stretch' — растянуть без сохранения пропорций
        """
        if not self._video_widget:
            return

        mode = mode.lower()
        if mode == "fit":
            self._video_widget.setAspectRatioMode(Qt.KeepAspectRatio)
        elif mode == "fill":
            self._video_widget.setAspectRatioMode(Qt.KeepAspectRatioByExpanding)
        elif mode == "stretch":
            self._video_widget.setAspectRatioMode(Qt.IgnoreAspectRatio)

    # --------------------------------------------------------
    #  Слоты
    # --------------------------------------------------------
    def _on_state(self, state):
        self.playingChanged.emit(state == QMediaPlayer.PlayingState)

    def _on_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.mediaEnded.emit()