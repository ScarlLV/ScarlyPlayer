# ui/toast.py
"""Кастомные всплывающие уведомления (Toast) в углу экрана."""

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QPushButton, QGraphicsDropShadowEffect
)


class Toast(QWidget):
    def __init__(self, parent, message: str, action_text: str = None, action_func=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.setStyleSheet("""
            QWidget { background: #1F1F26; border-radius: 8px; color: white; }
            QLabel { background: transparent; font-size: 13px; }
            QPushButton {
                background: #E53935; border-radius: 4px;
                padding: 4px 10px; color: white; font-weight: bold;
            }
            QPushButton:hover { background: #FF5252; }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        lbl = QLabel(message)
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

        if action_text and action_func:
            btn = QPushButton(action_text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda: (action_func(), self.close()))
            layout.addWidget(btn)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        self.adjustSize()

        # Позиция: правый нижний угол родителя (или экрана, если родитель — QMainWindow)
        p_rect = parent.rect()
        margin = 30
        x = p_rect.width() - self.width() - margin
        y = p_rect.height() - self.height() - margin

        # Анимация выезда снизу вверх
        self.move(x, y + 20)
        self._anim_in = QPropertyAnimation(self, b"pos", self)
        self._anim_in.setDuration(300)
        self._anim_in.setStartValue(QPoint(x, y + 20))
        self._anim_in.setEndValue(QPoint(x, y))
        self._anim_in.setEasingCurve(QEasingCurve.OutCubic)
        self._anim_in.start()

        # Автозакрытие
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._fade_out)
        self._timer.start(4000)

        self.show()

    def _fade_out(self):
        self._anim_out = QPropertyAnimation(self, b"windowOpacity", self)
        self._anim_out.setDuration(300)
        self._anim_out.setStartValue(1.0)
        self._anim_out.setEndValue(0.0)
        self._anim_out.finished.connect(self.close)
        self._anim_out.start()