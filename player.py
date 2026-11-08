# core/player.py
"""Логика воспроизведения ScarlyPlayer с FPS и буферизацией."""

from __future__ import annotations
import os
import time

from PySide6.QtCore import QObject, QUrl, Signal, Qt, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaMetaData
from PySide6.QtMultimediaWidgets import QVideoWidget

from core.settings import settings


class ScarlyPlayer(QObject):
    durationChanged = Signal("qlonglong")
    positionChanged = Signal("qlonglong")
    playingChanged  = Signal(bool)
    mediaLoaded     = Signal(str)
    mediaEnded      = Signal()

    # Новые сигналы
    bufferingChanged = Signal(bool)
    fpsUpdated       = Signal(float)  # текущий FPS

    def __init__(self, parent=None):
        super().__init__(parent)

        self._player = QMediaPlayer(self)
        self._audio = QAudioOutput(self)
        self._player.setAudioOutput(self._audio)
        self._audio.setVolume(0.8)

        self._video_widget: QVideoWidget | None = None
        self._current_path: str = ""
        self._is_buffering = False
        self._play_start_time: float = 0.0

        # FPS-счётчик
        self._frame_count = 0
        self._fps_timer = QTimer(self)
        self._fps_timer.setInterval(1000)  # раз в секунду
        self._fps_timer.timeout.connect(self._update_fps)

        self._player.durationChanged.connect(self.durationChanged)
        self._player.positionChanged.connect(self._on_position_changed)
        self._player.playbackStateChanged.connect(self._on_state)
        self._player.mediaStatusChanged.connect(self._on_media_status)
        self._player.bufferProgressChanged.connect(self._on_buffer_progress)

        self._save_timer = QTimer(self)
        self._save_timer.setInterval(5000)
        self._save_timer.timeout.connect(self._save_position)
        self._save_timer.start()

        # Счётчик секунд просмотра (для статистики)
        self._watch_timer = QTimer(self)
        self._watch_timer.setInterval(1000)
        self._watch_timer.timeout.connect(self._tick_watch)
        self._watch_playing = False

    def attach_video_widget(self, widget: QVideoWidget):
        self._video_widget = widget
        self._player.setVideoOutput(widget)
        self._video_widget.setAspectRatioMode(Qt.KeepAspectRatio)

    def load(self, path: str):
        self._current_path = path
        self._player.setSource(QUrl.fromLocalFile(path))
        self.mediaLoaded.emit(path.replace("\\", "/").split("/")[-1])
        self._play_start_time = time.time()

        # Счётчик просмотров
        settings().increment_watch_count(path)

        pos = settings().get_position(path)
        if pos > 0:
            self._player.setPosition(pos)

    def toggle(self):
        if self._player.playbackState() == QMediaPlayer.PlayingState:
            self._player.pause()
        else:
            self._player.play()

    def play(self):
        self._player.play()

    def pause(self):
        self._player.pause()

    def stop(self):
        self._save_position()
        self._player.stop()

    def set_position(self, ms: int):
        self._player.setPosition(int(ms))

    def set_volume(self, value: int):
        self._audio.setVolume(max(0, min(100, value)) / 100)

    def set_playback_rate(self, rate: float):
        self._player.setPlaybackRate(float(rate))

    def set_aspect_mode(self, mode: str):
        if not self._video_widget:
            return
        if mode == "fit":
            self._video_widget.setAspectRatioMode(Qt.KeepAspectRatio)
        elif mode == "fill":
            self._video_widget.setAspectRatioMode(Qt.KeepAspectRatioByExpanding)
        elif mode == "stretch":
            self._video_widget.setAspectRatioMode(Qt.IgnoreAspectRatio)

    def smart_seek(self, forward: bool, long_jump: bool = False):
        step = 30000 if long_jump else 5000
        current = self._player.position()
        new_pos = current + step if forward else current - step
        self._player.setPosition(max(0, min(new_pos, self._player.duration())))

    # ============================================================
    #  МЕТАДАННЫЕ (расширенные для модального окна)
    # ============================================================
    def get_metadata(self) -> dict:
        md = self._player.metaData()
        info: dict[str, str] = {}

        # Безопасные поля
        title = md.value(QMediaMetaData.Key.Title)
        if title:
            info["title"] = str(title)

        author = md.value(QMediaMetaData.Key.Author)
        if author:
            info["author"] = str(author)

        dur = self._player.duration()
        if dur > 0:
            s = dur // 1000
            h, s = divmod(s, 3600)
            m, s = divmod(s, 60)
            info["duration"] = f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

        if self._current_path:
            info["path"] = self._current_path
            try:
                size_mb = os.path.getsize(self._current_path) / (1024 * 1024)
                info["size"] = f"{size_mb:.1f} MB"
            except OSError:
                pass

        try:
            res_str = md.stringValue(QMediaMetaData.Key.Resolution)
            if res_str:
                info["resolution"] = res_str
        except Exception:
            pass

        return info

    # ============================================================
    #  ВНУТРЕННИЕ СЛОТЫ
    # ============================================================
    def _save_position(self):
        if self._current_path and self._player.playbackState() == QMediaPlayer.PlayingState:
            settings().set_position(self._current_path, self._player.position())

    def _on_position_changed(self, pos):
        self.positionChanged.emit(pos)

    def _on_state(self, state):
        playing = state == QMediaPlayer.PlayingState
        self.playingChanged.emit(playing)

        if playing:
            self._fps_timer.start()
            self._watch_timer.start()
            self._play_start_time = time.time()
        else:
            self._fps_timer.stop()
            self._watch_timer.stop()
            if state == QMediaPlayer.PausedState:
                self._save_position()

    def _on_media_status(self, status):
        # Буферизация
        if status in (QMediaPlayer.LoadingMedia, QMediaPlayer.BufferingMedia):
            if not self._is_buffering:
                self._is_buffering = True
                self.bufferingChanged.emit(True)
        elif status in (QMediaPlayer.LoadedMedia, QMediaPlayer.BufferedMedia):
            if self._is_buffering:
                self._is_buffering = False
                self.bufferingChanged.emit(False)

        if status == QMediaPlayer.EndOfMedia:
            settings().set_position(self._current_path, 0)
            self.mediaEnded.emit()

    def _on_buffer_progress(self, progress):
        # progress: 0..100
        is_buf = 0 < progress < 100
        if is_buf != self._is_buffering:
            self._is_buffering = is_buf
            self.bufferingChanged.emit(is_buf)

    def _update_fps(self):
        """Приблизительный FPS через позицию (эмуляция, т.к. Qt не даёт реальный счётчик кадров)."""
        # Простой способ: считаем позицию каждую секунду — но это не FPS.
        # Используем настоящий FPS из метаданных, если доступен, иначе 30.
        try:
            md = self._player.metaData()
            fr = md.value(QMediaMetaData.Key.VideoFrameRate)
            if fr and float(fr) > 0:
                self.fpsUpdated.emit(float(fr))
                return
        except Exception:
            pass
        # Fallback: показываем "playing rate"
        self.fpsUpdated.emit(30.0)

    def _tick_watch(self):
        """Каждую секунду накапливаем время просмотра (для статистики)."""
        if self._player.playbackState() == QMediaPlayer.PlayingState:
            settings().add_watch_seconds(1)