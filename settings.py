# core/settings.py
"""Персистентные настройки ScarlyPlayer через QSettings."""

from __future__ import annotations
import hashlib
import json
import os
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
    def get_language(self, default: str = "en") -> str:
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

    # ---- Аудио-устройство ----
    def get_audio_device(self) -> str:
        return self._s.value("audio/device", "", type=str)
    def set_audio_device(self, name: str):
        self._s.setValue("audio/device", name)

    # ============================================================
    #  БИБЛИОТЕКА
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
                    "hash": str(item.get("hash", "")),
                })
            elif isinstance(item, str) and item:
                res.append({
                    "path": item, "tags": "", "favorite": False,
                    "watch_count": 0, "last_watched": 0,
                    "title": "", "author": "", "hash": "",
                })
        return res

    def set_library(self, items: list[dict]):
        self._s.setValue("library/files", items)

    # ============================================================
    #  ХОТКЕИ
    # ============================================================
    DEFAULT_HOTKEYS = {
        "play_pause":       "Space",
        "seek_left":        "Left",
        "seek_right":       "Right",
        "seek_left_long":   "Shift+Left",
        "seek_right_long":  "Shift+Right",
        "fullscreen":       "F",
        "exit_fullscreen":  "Esc",
        "mute":             "M",
        "open_file":        "Ctrl+O",
    }

    def get_hotkey(self, action: str) -> str:
        default = self.DEFAULT_HOTKEYS.get(action, "")
        return self._s.value(f"hotkeys/{action}", default, type=str)

    def set_hotkey(self, action: str, key: str):
        self._s.setValue(f"hotkeys/{action}", key)

    def reset_hotkeys(self):
        for action in self.DEFAULT_HOTKEYS:
            self._s.remove(f"hotkeys/{action}")

    # ============================================================
    #  ПОЗИЦИИ
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
    #  FPS
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
        """Увеличивает счётчик просмотров видео и сохраняет дату."""
        import time
        lib = self.get_library()
        for item in lib:
            if item["path"] == path:
                item["watch_count"] = int(item.get("watch_count", 0)) + 1
                item["last_watched"] = int(time.time())
                break
        self.set_library(lib)

    # ---- Статистика по дням (для графика) ----
    def get_daily_stats(self) -> dict[str, int]:
        """Возвращает {'2026-01-15': 3600, ...} — секунды по дням."""
        raw = self._s.value("stats/daily", "", type=str)
        if not raw:
            return {}
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return {str(k): int(v) for k, v in data.items()}
            return {}
        except Exception:
            return {}

    def add_daily_watch(self, seconds: int):
        """Добавляет секунды к текущей дате."""
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        data = self.get_daily_stats()
        data[today] = data.get(today, 0) + int(seconds)
        # QSettings не умеет dict → сериализуем в JSON-строку
        self._s.setValue("stats/daily", json.dumps(data, ensure_ascii=False))

    def get_today_seconds(self) -> int:
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        return self.get_daily_stats().get(today, 0)

    # ============================================================
    #  ДУБЛИКАТЫ
    # ============================================================
    @staticmethod
    def compute_hash(path: str, block_size: int = 65536) -> str:
        """Быстрый MD5-хэш файла (только первые + последние блоки для скорости)."""
        if not os.path.exists(path):
            return ""
        try:
            size = os.path.getsize(path)
            h = hashlib.md5()
            with open(path, "rb") as f:
                if size <= block_size * 2:
                    h.update(f.read())
                else:
                    h.update(f.read(block_size))
                    f.seek(-block_size, os.SEEK_END)
                    h.update(f.read(block_size))
            return h.hexdigest()
        except Exception:
            return ""

    def update_library_hashes(self) -> int:
        """Проставляет хэши для видео без них. Возвращает кол-во обновлённых."""
        lib = self.get_library()
        updated = 0
        for item in lib:
            if not item.get("hash") and os.path.exists(item["path"]):
                item["hash"] = self.compute_hash(item["path"])
                if item["hash"]:
                    updated += 1
        if updated:
            self.set_library(lib)
        return updated

    def find_duplicates(self) -> dict[str, list[dict]]:
        """Группирует видео по хэшу. Возвращает только группы с >1 файлом."""
        lib = self.get_library()
        groups: dict[str, list[dict]] = {}
        for item in lib:
            h = item.get("hash", "")
            if not h:
                continue
            groups.setdefault(h, []).append(item)
        return {h: items for h, items in groups.items() if len(items) > 1}

    # ============================================================
    #  СБРОС / ПРОФИЛИ
    # ============================================================
    def reset_all(self):
        self._s.clear()

    def export_profile(self, parent_widget) -> bool:
        path, _ = QFileDialog.getSaveFileName(
            parent_widget, tr("dialog.export"), "profile.scarly", tr("dialog.scarly")
        )
        if not path:
            return False
        data = {
            "version": 1,
            "language": self.get_language(),
            "theme": self.get_theme(),
            "accent": self.get_accent_color(),
            "bg": self.get_bg_image(),
            "bg_video": self.get_bg_video(),
            "volume": self.get_volume(),
            "audio": self.get_audio_device(),
            "library": self.get_library(),
            "hotkeys": {k: self.get_hotkey(k) for k in self.DEFAULT_HOTKEYS},
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            QMessageBox.information(parent_widget, tr("dialog.export"), "Профиль сохранён!")
            return True
        except Exception as e:
            QMessageBox.warning(parent_widget, tr("dialog.export"), f"Ошибка: {e}")
            return False

    def import_profile(self, parent_widget) -> bool:
        path, _ = QFileDialog.getOpenFileName(
            parent_widget, tr("dialog.import"), "", tr("dialog.scarly")
        )
        if not path:
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.set_language(data.get("language", "en"))
            self.set_theme(data.get("theme", "dark"))
            self.set_accent_color(data.get("accent", "#E53935"))
            self.set_bg_image(data.get("bg", ""))
            self.set_bg_video(data.get("bg_video", ""))
            self.set_volume(data.get("volume", 80))
            self.set_audio_device(data.get("audio", ""))
            self.set_library(data.get("library", []))
            for k, v in data.get("hotkeys", {}).items():
                self.set_hotkey(k, v)
            QMessageBox.information(parent_widget, tr("dialog.import"), "Профиль загружен!")
            return True
        except Exception as e:
            QMessageBox.warning(parent_widget, tr("dialog.import"), f"Ошибка: {e}")
            return False

    # ============================================================
    #  КЭШ
    # ============================================================
    def clear_cache(self) -> int:
        removed = 0
        import sys
        if hasattr(sys, "_MEIPASS"):
            return 0
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