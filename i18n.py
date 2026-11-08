# core/i18n.py
"""
Лёгкий i18n для ScarlyPlayer.
Поддерживаемые языки: ru / uk / de / zh.
Без gettext, без .qm-файлов — всё в одном словаре.
"""

from __future__ import annotations
from PySide6.QtCore import QObject, Signal


# ============================================================
#  МЕТА
# ============================================================
APP_VERSION = "1.0.0"
APP_AUTHOR  = "ScarlyDev"
APP_REPO    = "https://github.com/ScarlLV"

DEFAULT_LANG = "ru"

LANG_NAMES = {
    "ru": "Русский",
    "uk": "Українська",
    "de": "Deutsch",
    "zh": "中文",
}


# ============================================================
#  ПЕРЕВОДЫ
# ============================================================
TRANSLATIONS: dict[str, dict[str, str]] = {

    # ============================================================
    #  РУССКИЙ
    # ============================================================
    "ru": {
        # --- общее / окно ---
        "app.title":            "ScarlyPlayer",

        # --- sidebar ---
        "nav.player":           "Плеер",
        "nav.library":          "Библиотека",
        "nav.settings":         "Настройки",
        "nav.about":            "О ScarlyPlayer",

        # --- control panel ---
        "btn.open":             "📂  Открыть файл",
        "btn.play":             "▶  Играть",
        "btn.pause":            "⏸  Пауза",
        "btn.stop":             "⏹",
        "label.volume":         "🔊",

        # --- диалоги ---
        "dialog.openVideo":     "Выберите видео",
        "dialog.videoFilt":     "Видео (*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.flv *.wmv *.ts);;Все файлы (*)",
        "dialog.confirm":       "Подтверждение",
        "dialog.yes":           "Да",
        "dialog.no":            "Нет",
        "dialog.cancel":        "Отмена",

        # --- плеер ---
        "player.placeholder":   "Откройте видео, чтобы начать",

        # --- настройки ---
        "settings.lang":            "Язык интерфейса",
        "settings.folder":          "Папка по умолчанию",
        "settings.folder.none":     "Не выбрана",
        "settings.folder.pick":     "📁  Выбрать папку",
        "settings.folder.reset":    "Сбросить",
        "settings.extended.soon":   "Расширенные настройки скоро...",

        # --- библиотека ---
        "library.title":        "Библиотека",
        "library.empty":        "Библиотека пуста — откройте файл, чтобы добавить его сюда",
        "library.add":          "➕  Добавить файлы",
        "library.clear":        "🗑  Очистить библиотеку",
        "library.remove":       "Удалить из библиотеки",
        "library.play_hint":    "Двойной клик — воспроизвести",
        "library.clear.confirm":"Очистить всю библиотеку?",

        # --- about ---
        "about.version":        "Версия",
        "about.author":         "Автор",
        "about.repo":           "GitHub",
        "about.thanks":         "Сделано с ❤️  на PySide6",
    },

    # ============================================================
    #  УКРАЇНСЬКА
    # ============================================================
    "uk": {
        # --- общее / окно ---
        "app.title":            "ScarlyPlayer",

        # --- sidebar ---
        "nav.player":           "Плеєр",
        "nav.library":          "Бібліотека",
        "nav.settings":         "Налаштування",
        "nav.about":            "Про ScarlyPlayer",

        # --- control panel ---
        "btn.open":             "📂  Відкрити файл",
        "btn.play":             "▶  Грати",
        "btn.pause":            "⏸  Пауза",
        "btn.stop":             "⏹",
        "label.volume":         "🔊",

        # --- диалоги ---
        "dialog.openVideo":     "Виберіть відео",
        "dialog.videoFilt":     "Відео (*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.flv *.wmv *.ts);;Усі файли (*)",
        "dialog.confirm":       "Підтвердження",
        "dialog.yes":           "Так",
        "dialog.no":            "Ні",
        "dialog.cancel":        "Скасувати",

        # --- плеер ---
        "player.placeholder":   "Відкрийте відео, щоб почати",

        # --- настройки ---
        "settings.lang":            "Мова інтерфейсу",
        "settings.folder":          "Папка за замовчуванням",
        "settings.folder.none":     "Не обрано",
        "settings.folder.pick":     "📁  Вибрати папку",
        "settings.folder.reset":    "Скинути",
        "settings.extended.soon":   "Розширені налаштування скоро...",

        # --- библиотека ---
        "library.title":        "Бібліотека",
        "library.empty":        "Бібліотека порожня — відкрийте файл, щоб додати його сюди",
        "library.add":          "➕  Додати файли",
        "library.clear":        "🗑  Очистити бібліотеку",
        "library.remove":       "Видалити з бібліотеки",
        "library.play_hint":    "Подвійний клік — відтворити",
        "library.clear.confirm":"Очистити всю бібліотеку?",

        # --- about ---
        "about.version":        "Версія",
        "about.author":         "Автор",
        "about.repo":           "GitHub",
        "about.thanks":         "Зроблено з ❤️  на PySide6",
    },

    # ============================================================
    #  DEUTSCH
    # ============================================================
    "de": {
        # --- общее / окно ---
        "app.title":            "ScarlyPlayer",

        # --- sidebar ---
        "nav.player":           "Player",
        "nav.library":          "Bibliothek",
        "nav.settings":         "Einstellungen",
        "nav.about":            "Über ScarlyPlayer",

        # --- control panel ---
        "btn.open":             "📂  Datei öffnen",
        "btn.play":             "▶  Abspielen",
        "btn.pause":            "⏸  Pause",
        "btn.stop":             "⏹",
        "label.volume":         "🔊",

        # --- диалоги ---
        "dialog.openVideo":     "Video auswählen",
        "dialog.videoFilt":     "Videos (*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.flv *.wmv *.ts);;Alle Dateien (*)",
        "dialog.confirm":       "Bestätigung",
        "dialog.yes":           "Ja",
        "dialog.no":            "Nein",
        "dialog.cancel":        "Abbrechen",

        # --- плеер ---
        "player.placeholder":   "Öffne ein Video, um zu starten",

        # --- настройки ---
        "settings.lang":            "Sprache der Benutzeroberfläche",
        "settings.folder":          "Standardordner",
        "settings.folder.none":     "Nicht ausgewählt",
        "settings.folder.pick":     "📁  Ordner wählen",
        "settings.folder.reset":    "Zurücksetzen",
        "settings.extended.soon":   "Erweiterte Einstellungen folgen bald...",

        # --- библиотека ---
        "library.title":        "Bibliothek",
        "library.empty":        "Bibliothek ist leer — öffne eine Datei, um sie hinzuzufügen",
        "library.add":          "➕  Dateien hinzufügen",
        "library.clear":        "🗑  Bibliothek leeren",
        "library.remove":       "Aus Bibliothek entfernen",
        "library.play_hint":    "Doppelklick — abspielen",
        "library.clear.confirm":"Gesamte Bibliothek leeren?",

        # --- about ---
        "about.version":        "Version",
        "about.author":         "Autor",
        "about.repo":           "GitHub",
        "about.thanks":         "Mit ❤️  auf PySide6 gemacht",
    },

    # ============================================================
    #  中文
    # ============================================================
    "zh": {
        # --- общее / окно ---
        "app.title":            "ScarlyPlayer",

        # --- sidebar ---
        "nav.player":           "播放器",
        "nav.library":          "媒体库",
        "nav.settings":         "设置",
        "nav.about":            "关于 ScarlyPlayer",

        # --- control panel ---
        "btn.open":             "📂  打开文件",
        "btn.play":             "▶  播放",
        "btn.pause":            "⏸  暂停",
        "btn.stop":             "⏹",
        "label.volume":         "🔊",

        # --- диалоги ---
        "dialog.openVideo":     "选择视频",
        "dialog.videoFilt":     "视频 (*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.flv *.wmv *.ts);;所有文件 (*)",
        "dialog.confirm":       "确认",
        "dialog.yes":           "是",
        "dialog.no":            "否",
        "dialog.cancel":        "取消",

        # --- плеер ---
        "player.placeholder":   "打开视频以开始播放",

        # --- настройки ---
        "settings.lang":            "界面语言",
        "settings.folder":          "默认文件夹",
        "settings.folder.none":     "未选择",
        "settings.folder.pick":     "📁  选择文件夹",
        "settings.folder.reset":    "重置",
        "settings.extended.soon":   "高级设置即将推出...",

        # --- библиотека ---
        "library.title":        "媒体库",
        "library.empty":        "媒体库为空 — 打开文件以添加",
        "library.add":          "➕  添加文件",
        "library.clear":        "🗑  清空媒体库",
        "library.remove":       "从媒体库移除",
        "library.play_hint":    "双击播放",
        "library.clear.confirm":"清空整个媒体库？",

        # --- about ---
        "about.version":        "版本",
        "about.author":         "作者",
        "about.repo":           "GitHub",
        "about.thanks":         "使用 ❤️  在 PySide6 上制作",
    },
}


# ============================================================
#  TRANSLATOR
# ============================================================
class Translator(QObject):
    """Глобальный переводчик. UI подписывается на languageChanged()."""

    languageChanged = Signal(str)

    def __init__(self, lang: str = DEFAULT_LANG):
        super().__init__()
        self._lang = lang if lang in TRANSLATIONS else DEFAULT_LANG

    @property
    def language(self) -> str:
        return self._lang

    def set_language(self, lang: str) -> None:
        if lang in TRANSLATIONS and lang != self._lang:
            self._lang = lang
            self.languageChanged.emit(lang)

    def t(self, key: str) -> str:
        """Перевод ключа. Fallback: выбранный → ru → сам ключ."""
        return (
            TRANSLATIONS.get(self._lang, {}).get(key)
            or TRANSLATIONS[DEFAULT_LANG].get(key)
            or key
        )


# ============================================================
#  СИНГЛТОН
# ============================================================
_tr: Translator | None = None


def translator() -> Translator:
    global _tr
    if _tr is None:
        _tr = Translator()
    return _tr


def tr(key: str) -> str:
    return translator().t(key)