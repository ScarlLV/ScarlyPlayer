# core/player.py
"""Логика воспроизведения ScarlyPlayer v1.0."""
from __future__ import annotations

from PySide6.QtCore import QObject, QUrl, Signal, Qt
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput


class ScarlyPlayer(QObject):
    """Тонкая обёртка над QMediaPlayer с удобными сигналами."""

    # ВАЖНО: qlonglong = int64, как у QMediaPlayer
    durationChanged = Signal("qlonglong")
    positionChanged = Signal("qlonglong")
    playingChanged  = Signal(bool)
    mediaLoaded     = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._player = QMediaPlayer(self)
        self._audio = QAudioOutput(self)
        self._player.setAudioOutput(self._audio)
        self._audio.setVolume(0.8)

        self._player.durationChanged.connect(self.durationChanged)
        self._player.positionChanged.connect(self.positionChanged)
        self._player.playbackStateChanged.connect(self._on_state)

    # ----- публичный API -----
    def attach_video_widget(self, widget) -> None:
        self._player.setVideoOutput(widget)

    def load(self, path: str) -> None:
        self._player.setSource(QUrl.fromLocalFile(path))
        self.mediaLoaded.emit(path.split("/")[-1].split("\\")[-1])

    def toggle(self) -> None:
        if self._player.playbackState() == QMediaPlayer.PlayingState:
            self._player.pause()
        else:
            self._player.play()

    def play(self):  self._player.play()
    def pause(self): self._player.pause()
    def stop(self):  self._player.stop()

    def set_position(self, ms: int) -> None:
        self._player.setPosition(int(ms))

    def set_volume(self, value: int) -> None:
        self._audio.setVolume(max(0, min(100, value)) / 100)

    # ----- слоты -----
    def _on_state(self, state):
        self.playingChanged.emit(state == QMediaPlayer.PlayingState)