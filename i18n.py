# core/i18n.py
"""
Лёгкий i18n для ScarlyPlayer.
Поддерживаемые языки: ru / uk / de / zh / ja / fr.
Без gettext, без .qm-файлов — всё в одном словаре.
"""

from __future__ import annotations
from PySide6.QtCore import QObject, Signal


# ============================================================
#  МЕТА
# ============================================================
APP_VERSION = "1.1.11"
APP_AUTHOR  = "ScarlyDev"
APP_REPO    = "https://github.com/ScarlLV"

DEFAULT_LANG = "ru"

LANG_NAMES = {
    "ru": "🇷🇺 Русский",
    "uk": "🇺🇦 Українська",
    "de": "🇩🇪 Deutsch",
    "zh": "🇨🇳 中文",
    "ja": "🇯🇵 日本語",
    "fr": "🇫🇷 Français",
}

# ============================================================
#  ПЕРЕВОДЫ
# ============================================================
TRANSLATIONS: dict[str, dict[str, str]] = {

    # ============================================================
    #  РУССКИЙ
    # ============================================================
    "ru": {
        "app.title":            "ScarlyPlayer",

        "nav.player":           "Плеер",
        "nav.library":          "Библиотека",
        "nav.settings":         "Настройки",
        "nav.about":            "О ScarlyPlayer",

        "btn.open":             "📂  Открыть файл",
        "btn.play":             "▶  Играть",
        "btn.pause":            "⏸  Пауза",
        "btn.stop":             "⏹",
        "label.volume":         "🔊",

        "dialog.openVideo":     "Выберите видео",
        "dialog.videoFilt":     "Видео (*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.flv *.wmv *.ts);;Все файлы (*)",
        "dialog.confirm":       "Подтверждение",
        "dialog.yes":           "Да",
        "dialog.no":            "Нет",
        "dialog.cancel":        "Отмена",

        "player.placeholder":   "Откройте видео, чтобы начать",

        "settings.lang":            "Язык интерфейса",
        "settings.appearance":      "Внешний вид",
        "settings.accent":          "Акцентный цвет",
        "settings.accent.pick":     "Выбрать цвет",
        "settings.bg":              "Свой фон",
        "settings.bg.pick":         "🖼  Выбрать картинку",
        "settings.bg.reset":        "Убрать фон",
        "settings.bg.none":         "Стандартный",
        "settings.folder":          "Папка по умолчанию",
        "settings.folder.none":     "Не выбрана",
        "settings.folder.pick":     "📁  Выбрать папку",
        "settings.folder.reset":    "Сбросить",
        "settings.extended.soon":   "Расширенные настройки скоро...",

        "library.title":        "Библиотека",
        "library.empty":        "Библиотека пуста — откройте файл, чтобы добавить его сюда",
        "library.add":          "➕  Добавить файлы",
        "library.clear":        "🗑  Очистить библиотеку",
        "library.remove":       "Удалить из библиотеки",
        "library.play_hint":    "Двойной клик — воспроизвести",
        "library.clear.confirm":"Очистить всю библиотеку?",

        "about.version":        "Версия",
        "about.author":         "Автор",
        "about.repo":           "GitHub",
        "about.thanks":         "Сделано с ❤️  на PySide6",
    },

    # ============================================================
    #  УКРАЇНСЬКА
    # ============================================================
    "uk": {
        "app.title":            "ScarlyPlayer",

        "nav.player":           "Плеєр",
        "nav.library":          "Бібліотека",
        "nav.settings":         "Налаштування",
        "nav.about":            "Про ScarlyPlayer",

        "btn.open":             "📂  Відкрити файл",
        "btn.play":             "▶  Грати",
        "btn.pause":            "⏸  Пауза",
        "btn.stop":             "⏹",
        "label.volume":         "🔊",

        "dialog.openVideo":     "Виберіть відео",
        "dialog.videoFilt":     "Відео (*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.flv *.wmv *.ts);;Усі файли (*)",
        "dialog.confirm":       "Підтвердження",
        "dialog.yes":           "Так",
        "dialog.no":            "Ні",
        "dialog.cancel":        "Скасувати",

        "player.placeholder":   "Відкрийте відео, щоб почати",

        "settings.lang":            "Мова інтерфейсу",
        "settings.appearance":      "Зовнішній вигляд",
        "settings.accent":          "Акцентний колір",
        "settings.accent.pick":     "Вибрати колір",
        "settings.bg":              "Власний фон",
        "settings.bg.pick":         "🖼  Вибрати картинку",
        "settings.bg.reset":        "Прибрати фон",
        "settings.bg.none":         "Стандартний",
        "settings.folder":          "Папка за замовчуванням",
        "settings.folder.none":     "Не обрано",
        "settings.folder.pick":     "📁  Вибрати папку",
        "settings.folder.reset":    "Скинути",
        "settings.extended.soon":   "Розширені налаштування скоро...",

        "library.title":        "Бібліотека",
        "library.empty":        "Бібліотека порожня — відкрийте файл, щоб додати його сюди",
        "library.add":          "➕  Додати файли",
        "library.clear":        "🗑  Очистити бібліотеку",
        "library.remove":       "Видалити з бібліотеки",
        "library.play_hint":    "Подвійний клік — відтворити",
        "library.clear.confirm":"Очистити всю бібліотеку?",

        "about.version":        "Версія",
        "about.author":         "Автор",
        "about.repo":           "GitHub",
        "about.thanks":         "Зроблено з ❤️  на PySide6",
    },

    # ============================================================
    #  DEUTSCH
    # ============================================================
    "de": {
        "app.title":            "ScarlyPlayer",

        "nav.player":           "Player",
        "nav.library":          "Bibliothek",
        "nav.settings":         "Einstellungen",
        "nav.about":            "Über ScarlyPlayer",

        "btn.open":             "📂  Datei öffnen",
        "btn.play":             "▶  Abspielen",
        "btn.pause":            "⏸  Pause",
        "btn.stop":             "⏹",
        "label.volume":         "🔊",

        "dialog.openVideo":     "Video auswählen",
        "dialog.videoFilt":     "Videos (*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.flv *.wmv *.ts);;Alle Dateien (*)",
        "dialog.confirm":       "Bestätigung",
        "dialog.yes":           "Ja",
        "dialog.no":            "Nein",
        "dialog.cancel":        "Abbrechen",

        "player.placeholder":   "Öffne ein Video, um zu starten",

        "settings.lang":            "Sprache der Benutzeroberfläche",
        "settings.appearance":      "Erscheinungsbild",
        "settings.accent":          "Akzentfarbe",
        "settings.accent.pick":     "Farbe wählen",
        "settings.bg":              "Eigener Hintergrund",
        "settings.bg.pick":         "🖼  Bild wählen",
        "settings.bg.reset":        "Hintergrund entfernen",
        "settings.bg.none":         "Standard",
        "settings.folder":          "Standardordner",
        "settings.folder.none":     "Nicht ausgewählt",
        "settings.folder.pick":     "📁  Ordner wählen",
        "settings.folder.reset":    "Zurücksetzen",
        "settings.extended.soon":   "Erweiterte Einstellungen folgen bald...",

        "library.title":        "Bibliothek",
        "library.empty":        "Bibliothek ist leer — öffne eine Datei, um sie hinzuzufügen",
        "library.add":          "➕  Dateien hinzufügen",
        "library.clear":        "🗑  Bibliothek leeren",
        "library.remove":       "Aus Bibliothek entfernen",
        "library.play_hint":    "Doppelklick — abspielen",
        "library.clear.confirm":"Gesamte Bibliothek leeren?",

        "about.version":        "Version",
        "about.author":         "Autor",
        "about.repo":           "GitHub",
        "about.thanks":         "Mit ❤️  auf PySide6 gemacht",
    },

    # ============================================================
    #  中文
    # ============================================================
    "zh": {
        "app.title":            "ScarlyPlayer",

        "nav.player":           "播放器",
        "nav.library":          "媒体库",
        "nav.settings":         "设置",
        "nav.about":            "关于 ScarlyPlayer",

        "btn.open":             "📂  打开文件",
        "btn.play":             "▶  播放",
        "btn.pause":            "⏸  暂停",
        "btn.stop":             "⏹",
        "label.volume":         "🔊",

        "dialog.openVideo":     "选择视频",
        "dialog.videoFilt":     "视频 (*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.flv *.wmv *.ts);;所有文件 (*)",
        "dialog.confirm":       "确认",
        "dialog.yes":           "是",
        "dialog.no":            "否",
        "dialog.cancel":        "取消",

        "player.placeholder":   "打开视频以开始播放",

        "settings.lang":            "界面语言",
        "settings.appearance":      "外观",
        "settings.accent":          "强调色",
        "settings.accent.pick":     "选择颜色",
        "settings.bg":              "自定义背景",
        "settings.bg.pick":         "🖼  选择图片",
        "settings.bg.reset":        "移除背景",
        "settings.bg.none":         "默认",
        "settings.folder":          "默认文件夹",
        "settings.folder.none":     "未选择",
        "settings.folder.pick":     "📁  选择文件夹",
        "settings.folder.reset":    "重置",
        "settings.extended.soon":   "高级设置即将推出...",

        "library.title":        "媒体库",
        "library.empty":        "媒体库为空 — 打开文件以添加",
        "library.add":          "➕  添加文件",
        "library.clear":        "🗑  清空媒体库",
        "library.remove":       "从媒体库移除",
        "library.play_hint":    "双击播放",
        "library.clear.confirm":"清空整个媒体库？",

        "about.version":        "版本",
        "about.author":         "作者",
        "about.repo":           "GitHub",
        "about.thanks":         "使用 ❤️  在 PySide6 上制作",
    },

    # ============================================================
    #  日本語
    # ============================================================
    "ja": {
        "app.title":            "ScarlyPlayer",

        "nav.player":           "プレイヤー",
        "nav.library":          "ライブラリ",
        "nav.settings":         "設定",
        "nav.about":            "ScarlyPlayerについて",

        "btn.open":             "📂  ファイルを開く",
        "btn.play":             "▶  再生",
        "btn.pause":            "⏸  一時停止",
        "btn.stop":             "⏹",
        "label.volume":         "🔊",

        "dialog.openVideo":     "動画を選択",
        "dialog.videoFilt":     "動画 (*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.flv *.wmv *.ts);;すべてのファイル (*)",
        "dialog.confirm":       "確認",
        "dialog.yes":           "はい",
        "dialog.no":            "いいえ",
        "dialog.cancel":        "キャンセル",

        "player.placeholder":   "動画を開いて開始",

        "settings.lang":            "言語",
        "settings.appearance":      "外観",
        "settings.accent":          "アクセントカラー",
        "settings.accent.pick":     "色を選択",
        "settings.bg":              "カスタム背景",
        "settings.bg.pick":         "🖼  画像を選択",
        "settings.bg.reset":        "背景を削除",
        "settings.bg.none":         "デフォルト",
        "settings.folder":          "デフォルトフォルダ",
        "settings.folder.none":     "未選択",
        "settings.folder.pick":     "📁  選択",
        "settings.folder.reset":    "リセット",
        "settings.extended.soon":   "詳細設定は近日公開...",

        "library.title":        "ライブラリ",
        "library.empty":        "ライブラリは空です — ファイルを開いて追加してください",
        "library.add":          "➕  追加",
        "library.clear":        "🗑  クリア",
        "library.remove":       "ライブラリから削除",
        "library.play_hint":    "ダブルクリックで再生",
        "library.clear.confirm":"ライブラリをすべてクリアしますか？",

        "about.version":        "バージョン",
        "about.author":         "作者",
        "about.repo":           "GitHub",
        "about.thanks":         "PySide6で作られました ❤️",
    },

    # ============================================================
    #  FRANÇAIS
    # ============================================================
    "fr": {
        "app.title":            "ScarlyPlayer",

        "nav.player":           "Lecteur",
        "nav.library":          "Bibliothèque",
        "nav.settings":         "Paramètres",
        "nav.about":            "À propos",

        "btn.open":             "📂  Ouvrir un fichier",
        "btn.play":             "▶  Lire",
        "btn.pause":            "⏸  Pause",
        "btn.stop":             "⏹",
        "label.volume":         "🔊",

        "dialog.openVideo":     "Choisir une vidéo",
        "dialog.videoFilt":     "Vidéos (*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.flv *.wmv *.ts);;Tous les fichiers (*)",
        "dialog.confirm":       "Confirmation",
        "dialog.yes":           "Oui",
        "dialog.no":            "Non",
        "dialog.cancel":        "Annuler",

        "player.placeholder":   "Ouvrez une vidéo pour commencer",

        "settings.lang":            "Langue",
        "settings.appearance":      "Apparence",
        "settings.accent":          "Couleur d'accent",
        "settings.accent.pick":     "Choisir la couleur",
        "settings.bg":              "Fond personnalisé",
        "settings.bg.pick":         "🖼  Choisir une image",
        "settings.bg.reset":        "Supprimer le fond",
        "settings.bg.none":         "Par défaut",
        "settings.folder":          "Dossier par défaut",
        "settings.folder.none":     "Non sélectionné",
        "settings.folder.pick":     "📁  Choisir",
        "settings.folder.reset":    "Réinitialiser",
        "settings.extended.soon":   "Paramètres avancés bientôt...",

        "library.title":        "Bibliothèque",
        "library.empty":        "La bibliothèque est vide — ouvrez un fichier pour l'ajouter",
        "library.add":          "➕  Ajouter",
        "library.clear":        "🗑  Vider",
        "library.remove":       "Retirer de la bibliothèque",
        "library.play_hint":    "Double-cliquez pour lire",
        "library.clear.confirm":"Vider toute la bibliothèque ?",

        "about.version":        "Version",
        "about.author":         "Auteur",
        "about.repo":           "GitHub",
        "about.thanks":         "Fait avec ❤️  sur PySide6",
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