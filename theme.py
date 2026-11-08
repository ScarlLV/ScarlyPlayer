# core/theme.py — полный код

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication
from core.settings import settings

BG_DARK       = "#0F0F12"
BG_PANEL      = "#17171C"
BG_ELEVATED   = "#1F1F26"
BG_HOVER      = "#2A2A33"
TEXT_PRIMARY  = "#F5F5F7"
TEXT_SECONDARY= "#A0A0AB"
BORDER        = "#2A2A33"
RADIUS        = 12

def _adjust_color(hex_color: str, factor: float) -> str:
    c = QColor(hex_color)
    h, s, v, a = c.getHsvF()
    v = max(0.0, min(1.0, v * factor))
    c.setHsvF(h, s, v, a)
    return c.name()

def build_qss() -> str:
    s = settings()
    accent = s.get_accent_color()
    accent_hover = _adjust_color(accent, 1.2)
    accent_press = _adjust_color(accent, 0.8)
    
    bg_img = s.get_bg_image()
    
    # Если есть фон, делаем панели почти непрозрачными, чтобы текст читался
    bg_main = "transparent" if bg_img else BG_DARK
    bg_panel = "rgba(23, 23, 28, 245)" if bg_img else BG_PANEL
    bg_elevated = "rgba(31, 31, 38, 245)" if bg_img else BG_ELEVATED
    bg_card = "rgba(31, 31, 38, 245)" if bg_img else BG_ELEVATED

    return f"""
    QWidget {{
        background: {bg_main};
        color: {TEXT_PRIMARY};
        font-family: "Segoe UI", "SF Pro Display", "Inter", sans-serif;
        font-size: 13px;
    }}
    QMainWindow {{
        background: transparent;
    }}
    #TitleBar {{
        background: {bg_panel};
        border-bottom: 1px solid {BORDER};
        border-top-left-radius: {RADIUS}px;
        border-top-right-radius: {RADIUS}px;
    }}
    #TitleLabel {{
        color: {TEXT_PRIMARY};
        font-weight: 600;
        font-size: 14px;
        letter-spacing: 0.5px;
    }}
    QPushButton#WinBtn {{
        background: transparent;
        border: none;
        color: {TEXT_SECONDARY};
        font-size: 16px;
        padding: 6px 12px;
        border-radius: 8px;
    }}
    QPushButton#WinBtn:hover {{
        background: {BG_HOVER};
        color: {TEXT_PRIMARY};
    }}
    QPushButton#WinClose:hover {{
        background: {accent};
        color: white;
    }}
    #Sidebar {{
        background: {bg_panel};
        border-right: 1px solid {BORDER};
    }}
    QPushButton#NavBtn {{
        background: transparent;
        border: none;
        color: {TEXT_SECONDARY};
        text-align: left;
        padding: 12px 16px;
        border-radius: {RADIUS}px;
        font-size: 13px;
    }}
    QPushButton#NavBtn:hover {{
        background: {BG_HOVER};
        color: {TEXT_PRIMARY};
    }}
    QPushButton#NavBtn:checked {{
        background: {accent};
        color: white;
        font-weight: 600;
    }}
    #VideoContainer {{
        background: #000000;
        border-radius: {RADIUS}px;
    }}
    #ControlPanel {{
        background: {bg_panel};
        border-top: 1px solid {BORDER};
        border-bottom-left-radius: {RADIUS}px;
        border-bottom-right-radius: {RADIUS}px;
    }}
    QPushButton#CtrlBtn {{
        background: {bg_elevated};
        border: none;
        color: {TEXT_PRIMARY};
        border-radius: {RADIUS}px;
        padding: 10px 16px;
        font-weight: 600;
    }}
    QPushButton#CtrlBtn:hover {{
        background: {BG_HOVER};
    }}
    QPushButton#PlayBtn {{
        background: {accent};
        border: none;
        color: white;
        border-radius: {RADIUS}px;
        padding: 12px 22px;
        font-weight: 700;
        font-size: 14px;
    }}
    QPushButton#PlayBtn:hover  {{ background: {accent_hover}; }}
    QPushButton#PlayBtn:pressed{{ background: {accent_press}; }}
    QSlider::groove:horizontal {{
        height: 4px;
        background: {bg_elevated};
        border-radius: 2px;
    }}
    QSlider::sub-page:horizontal {{
        background: {accent};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {TEXT_PRIMARY};
        width: 14px; height: 14px;
        margin: -5px 0;
        border-radius: 7px;
    }}
    QSlider::handle:horizontal:hover {{
        background: {accent_hover};
    }}
    #TimeLabel {{
        color: {TEXT_SECONDARY};
        font-family: "Consolas", monospace;
        font-size: 12px;
    }}
    QToolTip {{
        background: {BG_ELEVATED};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px;
    }}
    QScrollArea {{
        background: transparent;
    }}
    QScrollArea > QWidget > QWidget {{
        background: transparent;
    }}
    
    /* Стили для плиток в настройках */
    QFrame#SettingsCard {{
        background: {bg_card};
        border: 1px solid {BORDER};
        border-radius: 16px;
    }}
    QLabel {{
        background: transparent;
    }}
    """

def apply_theme(app: QApplication):
    app.setStyleSheet(build_qss())