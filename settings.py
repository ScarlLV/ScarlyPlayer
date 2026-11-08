# core/settings.py
"""Персистентные настройки ScarlyPlayer через QSettings."""

from __future__ import annotations
import json
import shutil
import tempfile
from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QFileDialog, QMessageBox

from core.i18n import tr


ORG = "ScarlyPlayer"
APP = "ScarlyPlayer"


class Settings:
    def __init__(self):
        self._s = QSettings(ORG, APP)

    # ============================================================
    #  БАЗОВОЕ
    # ============================================================
    def get_language(self, default: str = "ru") -> str:
        return self._s.value("ui/language", default, type=str)
    def set_language(self, code: str):
        self._s.setValue("ui/language", code)

    def get_theme(self) -> str:
        return self._s.value("ui/theme", "dark", type=str)
    def set_theme(self, theme: str):
        self._s.setValue("ui/theme", theme)

    def get_accent_color(self) -> str:
        return self._s.value("ui/accent_color", "#E53935", type=str)
    def set_accent_color(self, color: str):
        self._s.setValue("ui/accent_color", color)

    def get_bg_image(self) -> str:
        return self._s.value("ui/bg_image", "", type=str)
    def set_bg_image(self, path: str):
        self._s.setValue("ui/bg_image", path)

    def get_bg_video(self) -> str:
        return self._s.value("ui/bg_video", "", type=str)
    def set_bg_video(self, path: str):
        self._s.setValue("ui/bg_video", path)

    def get_sidebar_visible(self) -> bool:
        return self._s.value("ui/sidebar_visible", True, type=bool)
    def set_sidebar_visible(self, visible: bool):
        self._s.setValue("ui/sidebar_visible", bool(visible))

    def get_default_dir(self) -> str:
        return self._s.value("files/default_dir", "", type=str)
    def set_default_dir(self, path: str):
        self._s.setValue("files/default_dir", path)

    def get_volume(self) -> int:
        return self._s.value("audio/volume", 80, type=int)
    def set_volume(self, value: int):
        self._s.setValue("audio/volume", int(value))

    def get_audio_device(self) -> str:
        return self._s.value("audio/device", "", type=str)
    def set_audio_device(self, name: str):
        self._s.setValue("audio/device", name)

    # ============================================================
    #  БИБЛИОТЕКА (с избранным и счётчиком просмотров)
    # ============================================================
    def get_library(self) -> list[dict]:
        raw = self._s.value("library/files", [], type=list)
        if not isinstance(raw, list):
            return []
        res = []
        for item in raw:
            if isinstance(item, dict) and "path" in item:
                res.append({
                    "path": str(item["path"]),
                    "tags": str(item.get("tags", "")),
                    "favorite": bool(item.get("favorite", False)),
                    "watch_count": int(item.get("watch_count", 0)),
                    "last_watched": int(item.get("last_watched", 0)),
                    "title": str(item.get("title", "")),
                    "author": str(item.get("author", "")),
                })
            elif isinstance(item, str) and item:
                res.append({
                    "path": item, "tags": "", "favorite": False,
                    "watch_count": 0, "last_watched": 0,
                    "title": "", "author": "",
                })
        return res

    def set_library(self, items: list[dict]):
        self._s.setValue("library/files", items)

    # ============================================================
    #  ХОТКЕИ
    # ============================================================
    def get_hotkey(self, action: str, default: str) -> str:
        return self._s.value(f"hotkeys/{action}", default, type=str)
    def set_hotkey(self, action: str, key: str):
        self._s.setValue(f"hotkeys/{action}", key)

    # ============================================================
    #  ПОЗИЦИИ (Продолжить просмотр)
    # ============================================================
    def get_remember_position(self) -> bool:
        return self._s.value("player/remember_position", True, type=bool)
    def set_remember_position(self, val: bool):
        self._s.setValue("player/remember_position", bool(val))

    def get_position(self, path: str) -> int:
        if not self.get_remember_position():
            return 0
        return self._s.value(f"player/pos/{path}", 0, type=int)
    def set_position(self, path: str, ms: int):
        if not self.get_remember_position():
            return
        if ms > 5000:
            self._s.setValue(f"player/pos/{path}", int(ms))
        else:
            self._s.remove(f"player/pos/{path}")

    # ============================================================
    #  FPS-ОВЕРЛЕЙ
    # ============================================================
    def get_fps_overlay(self) -> bool:
        return self._s.value("ui/fps_overlay", False, type=bool)
    def set_fps_overlay(self, val: bool):
        self._s.setValue("ui/fps_overlay", bool(val))

    # ============================================================
    #  СТАТИСТИКА
    # ============================================================
    def get_total_watch_seconds(self) -> int:
        return self._s.value("stats/total_seconds", 0, type=int)
    def add_watch_seconds(self, sec: int):
        total = self.get_total_watch_seconds() + int(sec)
        self._s.setValue("stats/total_seconds", total)

    def increment_watch_count(self, path: str):
        """Увеличивает счётчик просмотров видео."""
        import time
        lib = self.get_library()
        for item in lib:
            if item["path"] == path:
                item["watch_count"] = int(item.get("watch_count", 0)) + 1
                item["last_watched"] = int(time.time())
                break
        self.set_library(lib)

    # ============================================================
    #  СБРОС / ПРОФИЛИ
    # ============================================================
    def reset_all(self):
        self._s.clear()

    def export_profile(self, parent_widget):
        path, _ = QFileDialog.getSaveFileName(
            parent_widget, tr("dialog.export"), "profile.scarly", tr("dialog.scarly")
        )
        if not path:
            return
        data = {
            "language": self.get_language(),
            "theme": self.get_theme(),
            "accent": self.get_accent_color(),
            "bg": self.get_bg_image(),
            "volume": self.get_volume(),
            "audio": self.get_audio_device(),
            "library": self.get_library(),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        QMessageBox.information(parent_widget, tr("dialog.export"), "Профиль сохранён!")

    def import_profile(self, parent_widget) -> bool:
        path, _ = QFileDialog.getOpenFileName(
            parent_widget, tr("dialog.import"), "", tr("dialog.scarly")
        )
        if not path:
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.set_language(data.get("language", "ru"))
            self.set_theme(data.get("theme", "dark"))
            self.set_accent_color(data.get("accent", "#E53935"))
            self.set_bg_image(data.get("bg", ""))
            self.set_volume(data.get("volume", 80))
            self.set_audio_device(data.get("audio", ""))
            self.set_library(data.get("library", []))
            QMessageBox.information(parent_widget, tr("dialog.import"), "Профиль загружен!")
            return True
        except Exception as e:
            QMessageBox.warning(parent_widget, tr("dialog.import"), f"Ошибка: {e}")
            return False

    # ============================================================
    #  КЭШ
    # ============================================================
    def clear_cache(self) -> int:
        """Очищает временные файлы. Возвращает кол-во удалённых."""
        removed = 0
        # Временная папка PyInstaller (если onefile)
        import sys, os
        if hasattr(sys, "_MEIPASS"):
            return 0  # не трогаем .exe изнутри
        # Папка temp приложения
        app_temp = Path(tempfile.gettempdir()) / "ScarlyPlayer"
        if app_temp.exists():
            try:
                shutil.rmtree(app_temp)
                removed += 1
            except Exception:
                pass
        return removed


_settings: Settings | None = None


def settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings