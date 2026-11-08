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

    # ============================================================
    #  ЯЗЫК
    # ============================================================
    def get_language(self, default: str = "ru") -> str:
        return self._s.value("ui/language", default, type=str)

    def set_language(self, code: str) -> None:
        self._s.setValue("ui/language", code)

    # ============================================================
    #  ПАПКА ПО УМОЛЧАНИЮ
    # ============================================================
    def get_default_dir(self) -> str:
        return self._s.value("files/default_dir", "", type=str)

    def set_default_dir(self, path: str) -> None:
        self._s.setValue("files/default_dir", path)

    # ============================================================
    #  БИБЛИОТЕКА
    #  Формат: list[dict]  →  [{"path": str, "tags": str}, ...]
    # ============================================================
    def get_library(self) -> list[dict]:
        raw = self._s.value("library/files", [], type=list)

        # QSettings может вернуть строку вместо списка
        if isinstance(raw, str):
            raw = [p for p in raw.split("|") if p]
        if not isinstance(raw, list):
            return []

        result: list[dict] = []
        for item in raw:
            if isinstance(item, dict) and "path" in item:
                # новый формат
                result.append({
                    "path": str(item.get("path", "")),
                    "tags": str(item.get("tags", "")),
                })
            elif isinstance(item, str) and item:
                # старый формат (просто строки) — конвертируем
                result.append({"path": item, "tags": ""})
        return result

    def set_library(self, items: list[dict]) -> None:
        # Нормализуем перед сохранением
        clean: list[dict] = []
        for it in items:
            path = str(it.get("path", "")) if isinstance(it, dict) else str(it)
            tags = str(it.get("tags", "")) if isinstance(it, dict) else ""
            if path:
                clean.append({"path": path, "tags": tags})
        self._s.setValue("library/files", clean)

    # ============================================================
    #  ГРОМКОСТЬ
    # ============================================================
    def get_volume(self, default: int = 80) -> int:
        return self._s.value("audio/volume", default, type=int)

    def set_volume(self, value: int) -> None:
        self._s.setValue("audio/volume", int(value))

    # ============================================================
    #  ТЕМА / АКЦЕНТ
    # ============================================================
    def get_accent_color(self, default: str = "#E53935") -> str:
        return self._s.value("ui/accent_color", default, type=str)

    def set_accent_color(self, color_hex: str) -> None:
        self._s.setValue("ui/accent_color", color_hex)

    # ============================================================
    #  ФОН ПРИЛОЖЕНИЯ
    # ============================================================
    def get_bg_image(self) -> str:
        return self._s.value("ui/bg_image", "", type=str)

    def set_bg_image(self, path: str) -> None:
        self._s.setValue("ui/bg_image", path)

    # ============================================================
    #  ВИДИМОСТЬ САЙДБАРА
    # ============================================================
    def get_sidebar_visible(self, default: bool = True) -> bool:
        return self._s.value("ui/sidebar_visible", default, type=bool)

    def set_sidebar_visible(self, visible: bool) -> None:
        self._s.setValue("ui/sidebar_visible", bool(visible))

    # ============================================================
    #  (Опционально) СКОРОСТЬ / ASPECT — если захочешь запоминать
    # ============================================================
    def get_playback_rate(self, default: float = 1.0) -> float:
        return float(self._s.value("player/rate", default, type=float))

    def set_playback_rate(self, rate: float) -> None:
        self._s.setValue("player/rate", float(rate))

    def get_aspect_mode(self, default: str = "fit") -> str:
        return self._s.value("player/aspect", default, type=str)

    def set_aspect_mode(self, mode: str) -> None:
        self._s.setValue("player/aspect", mode)


# ============================================================
#  СИНГЛТОН
# ============================================================
_settings: Settings | None = None


def settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings