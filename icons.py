# core/icons.py
"""Хелпер для загрузки SVG-иконок с перекраской."""

import os
import sys

from PySide6.QtCore import Qt, QByteArray, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer


def resource_path(rel: str) -> str:
    """Путь к ресурсу (работает из исходников и из .exe)."""
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def load_svg_icon(name: str, color: str = "#F5F5F7", size: int = 20) -> QIcon:
    """
    Загружает SVG из assets/icons/ и перекрашивает в нужный цвет.
    `name` — без расширения, например: "play", "open".
    """
    path = resource_path(f"assets/icons/{name}.svg")
    if not os.path.exists(path):
        print(f"[icons] Не найден: {path}")
        return QIcon()

    # Читаем SVG как байты и заменяем currentColor на нужный цвет
    with open(path, "rb") as f:
        svg_bytes = f.read()

    svg_text = svg_bytes.decode("utf-8")
    svg_text = svg_text.replace("currentColor", color)

    renderer = QSvgRenderer(QByteArray(svg_text.encode("utf-8")))
    if not renderer.isValid():
        return QIcon()

    pixmap = QPixmap(QSize(size, size))
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    return QIcon(pixmap)