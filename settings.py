# core/settings.py
"""Персистентные настройки ScarlyPlayer через QSettings."""

from __future__ import annotations
from pathlib import Path
from PySide6.QtCore import QSettings


ORG = "ScarlyPlayer"
APP = "ScarlyPlayer"


class Settings:
    """Тонкая обёртка над QSettings."""

    def __init__(self):
        self._s = QSettings(ORG, APP)

    # ---- язык ----
    def get_language(self, default: str = "ru") -> str:
        return self._s.value("ui/language", default, type=str)

    def set_language(self, code: str) -> None:
        self._s.setValue("ui/language", code)

    # ---- папка по умолчанию ----
    def get_default_dir(self) -> str:
        return self._s.value("files/default_dir", "", type=str)

    def set_default_dir(self, path: str) -> None:
        self._s.setValue("files/default_dir", path)

    # ---- библиотека (список путей) ----
    def get_library(self) -> list[str]:
        raw = self._s.value("library/files", [], type=list)
        # QSettings иногда возвращает строку вместо списка — нормализуем
        if isinstance(raw, str):
            return [p for p in raw.split("|") if p]
        return [str(p) for p in raw if p]

    def set_library(self, paths: list[str]) -> None:
        self._s.setValue("library/files", list(paths))

    # ---- громкость ----
    def get_volume(self, default: int = 80) -> int:
        return self._s.value("audio/volume", default, type=int)

    def set_volume(self, value: int) -> None:
        self._s.setValue("audio/volume", int(value))


# синглтон
_settings: Settings | None = None


def settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings