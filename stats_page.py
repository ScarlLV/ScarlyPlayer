# ui/stats_page.py
"""Страница статистики: график часов + топ-5 видео."""

import time
from datetime import datetime, timedelta
from pathlib import Path

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QGraphicsDropShadowEffect
)

from core.i18n import tr, translator
from core.settings import settings


class StatsChart(QWidget):
    """Кастомный виджет — столбчатый график за последние 7 дней."""

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(220)
        self.setStyleSheet("background: transparent;")
        self._data: list[tuple[str, int]] = []
        self.refresh()

    def refresh(self):
        daily = settings().get_daily_stats()
        # Последние 7 дней
        today = datetime.now().date()
        data = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            key = d.strftime("%Y-%m-%d")
            label = d.strftime("%d.%m")
            data.append((label, daily.get(key, 0)))
        self._data = data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        pad_left = 40
        pad_bottom = 30
        pad_top = 20
        chart_w = w - pad_left - 20
        chart_h = h - pad_bottom - pad_top

        # Фон
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

        if not self._data:
            return

        max_val = max((v for _, v in self._data), default=0) or 1
        # Округляем max вверх до часа
        max_hours = max(1, (max_val + 3599) // 3600)

        # Сетка
        grid_pen = QPen(QColor(42, 42, 51))
        grid_pen.setWidth(1)
        painter.setPen(grid_pen)
        for i in range(max_hours + 1):
            y = pad_top + chart_h - (i / max_hours) * chart_h
            painter.drawLine(pad_left, int(y), w - 20, int(y))
            # Подпись
            painter.setPen(QColor(90, 90, 102))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(0, int(y) - 8, pad_left - 6, 16,
                             Qt.AlignRight | Qt.AlignVCenter, f"{i}ч")
            painter.setPen(grid_pen)

        # Столбцы
        n = len(self._data)
        bar_w = chart_w / n * 0.55
        gap = chart_w / n

        for i, (label, seconds) in enumerate(self._data):
            x = pad_left + i * gap + (gap - bar_w) / 2
            bar_h = (seconds / (max_hours * 3600)) * chart_h if max_hours > 0 else 0
            y = pad_top + chart_h - bar_h

            # Градиент
            grad = QLinearGradient(x, y, x, y + bar_h)
            grad.setColorAt(0, QColor("#FF5252"))
            grad.setColorAt(1, QColor("#C62828"))
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.NoPen)

            if bar_h > 0:
                painter.drawRoundedRect(QRectF(x, y, bar_w, bar_h), 4, 4)
            else:
                # Минимальная полоска для нулевых
                painter.setBrush(QColor(42, 42, 51))
                painter.drawRoundedRect(QRectF(x, pad_top + chart_h - 2, bar_w, 2), 1, 1)

            # Подпись дня
            painter.setPen(QColor(160, 160, 171))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(int(x - 10), h - pad_bottom + 8,
                             int(bar_w + 20), 20, Qt.AlignCenter, label)


class TopVideoRow(QWidget):
    """Одна строка топ-видео."""

    def __init__(self, rank: int, path: str, count: int):
        super().__init__()
        self.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 8, 0, 8)
        lay.setSpacing(12)

        rank_lbl = QLabel(f"#{rank}")
        rank_lbl.setStyleSheet("color: #E53935; font-size: 16px; font-weight: 800;")
        rank_lbl.setFixedWidth(36)
        lay.addWidget(rank_lbl)

        name = Path(path).name
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("color: #F5F5F7; font-size: 13px;")
        lay.addWidget(name_lbl, 1)

        count_lbl = QLabel(f"👁 {count}")
        count_lbl.setStyleSheet("color: #A0A0AB; font-size: 12px;")
        lay.addWidget(count_lbl)


class StatsPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        translator().languageChanged.connect(self.retranslate)
        # Обновлять при показе
        self.refresh()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        root = QVBoxLayout(content)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(16)

        # Заголовок
        self._title = QLabel(tr("stats.title"))
        self._title.setStyleSheet("color: #F5F5F7; font-size: 24px; font-weight: 800;")
        root.addWidget(self._title)

        # ==== Карточка 1: Сводка ====
        card_summary = self._create_card()
        lay_sum = QHBoxLayout(card_summary)
        lay_sum.setContentsMargins(20, 20, 20, 20)
        lay_sum.setSpacing(30)

        self._total_hours_lbl = self._stat_block(
            tr("stats.total_hours"), "0", "🕒"
        )
        self._total_videos_lbl = self._stat_block(
            tr("stats.total_videos"), "0", "🎬"
        )
        self._favorite_lbl = self._stat_block(
            tr("stats.favorite_count"), "0", "⭐"
        )
        self._library_lbl = self._stat_block(
            tr("stats.library_count"), "0", "📚"
        )

        lay_sum.addWidget(self._total_hours_lbl)
        lay_sum.addWidget(self._total_videos_lbl)
        lay_sum.addWidget(self._favorite_lbl)
        lay_sum.addWidget(self._library_lbl)
        lay_sum.addStretch()
        root.addWidget(card_summary)

        # ==== Карточка 2: График ====
        card_chart = self._create_card()
        lay_chart = QVBoxLayout(card_chart)
        lay_chart.setContentsMargins(20, 20, 20, 20)
        lay_chart.setSpacing(12)

        chart_title = QLabel("📊 " + tr("stats.total_hours") + " (7 дней)")
        chart_title.setStyleSheet("color: #F5F5F7; font-size: 16px; font-weight: 700;")
        lay_chart.addWidget(chart_title)

        self.chart = StatsChart()
        lay_chart.addWidget(self.chart)
        root.addWidget(card_chart)

        # ==== Карточка 3: Топ-5 ====
        card_top = self._create_card()
        lay_top = QVBoxLayout(card_top)
        lay_top.setContentsMargins(20, 20, 20, 20)
        lay_top.setSpacing(8)

        self._top_title = QLabel("🏆 " + tr("stats.top_videos"))
        self._top_title.setStyleSheet("color: #F5F5F7; font-size: 16px; font-weight: 700;")
        lay_top.addWidget(self._top_title)

        self._top_container = QVBoxLayout()
        self._top_container.setSpacing(4)
        lay_top.addLayout(self._top_container)

        self._top_empty = QLabel("—")
        self._top_empty.setStyleSheet("color: #5A5A66; font-size: 13px; padding: 20px;")
        self._top_empty.setAlignment(Qt.AlignCenter)
        lay_top.addWidget(self._top_empty)

        root.addWidget(card_top)
        root.addStretch()

        scroll.setWidget(content)
        main.addWidget(scroll)

    def _create_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("SettingsCard")
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)
        return card

    def _stat_block(self, label: str, value: str, icon: str) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 24px;")
        lay.addWidget(icon_lbl)

        val_lbl = QLabel(value)
        val_lbl.setStyleSheet("color: #F5F5F7; font-size: 26px; font-weight: 800;")
        val_lbl.setObjectName(f"stat_{label}")  # чтобы потом найти
        lay.addWidget(val_lbl)

        text_lbl = QLabel(label)
        text_lbl.setStyleSheet("color: #A0A0AB; font-size: 11px;")
        lay.addWidget(text_lbl)

        # сохраняем ссылку на val_lbl
        w._val_lbl = val_lbl
        return w

    def refresh(self):
        """Обновить данные."""
        lib = settings().get_library()

        # Всего часов
        total_sec = settings().get_total_watch_seconds()
        hours = total_sec // 3600
        minutes = (total_sec % 3600) // 60
        self._total_hours_lbl._val_lbl.setText(f"{hours}ч {minutes}м")

        # Просмотрено видео (сумма watch_count)
        total_watched = sum(item.get("watch_count", 0) for item in lib)
        self._total_videos_lbl._val_lbl.setText(str(total_watched))

        # Избранное
        fav_count = sum(1 for item in lib if item.get("favorite"))
        self._favorite_lbl._val_lbl.setText(str(fav_count))

        # Библиотека
        self._library_lbl._val_lbl.setText(str(len(lib)))

        # График
        self.chart.refresh()

        # Топ-5
        # Очистить старые
        while self._top_container.count():
            item = self._top_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Топ по watch_count
        top = sorted(lib, key=lambda x: x.get("watch_count", 0), reverse=True)[:5]
        top = [t for t in top if t.get("watch_count", 0) > 0]

        if top:
            self._top_empty.hide()
            for i, item in enumerate(top, start=1):
                row = TopVideoRow(i, item["path"], item["watch_count"])
                self._top_container.addWidget(row)
        else:
            self._top_empty.show()

    def retranslate(self, _lang: str = ""):
        self._title.setText(tr("stats.title"))
        self._top_title.setText("🏆 " + tr("stats.top_videos"))
        self.refresh()