# core/theme.py
"""Централизованная тема ScarlyPlayer с поддержкой смены акцента и фона."""

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication
from core.settings import settings


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
    bg_img = s.get_bg_image() or s.get_bg_video()

    BG_DARK       = "#0F0F12"
    BG_PANEL      = "#17171C"
    BG_ELEVATED   = "#1F1F26"
    BG_HOVER      = "#2A2A33"
    TEXT_PRIMARY  = "#F5F5F7"
    TEXT_SECONDARY = "#A0A0AB"
    BORDER        = "#2A2A33"
    RADIUS        = 12

    bg_main = "transparent" if bg_img else BG_DARK
    bg_panel = "rgba(23, 23, 28, 245)" if bg_img else BG_PANEL
    bg_elevated = "rgba(31, 31, 38, 245)" if bg_img else BG_ELEVATED

    return f"""
    QWidget {{
        background: {bg_main};
        color: {TEXT_PRIMARY};
        font-family: "Segoe UI", "SF Pro Display", "Inter", sans-serif;
        font-size: 13px;
    }}
    QMainWindow {{ background: transparent; }}
    #TitleBar {{
        background: {bg_panel};
        border-bottom: 1px solid {BORDER};
        border-top-left-radius: {RADIUS}px;
        border-top-right-radius: {RADIUS}px;
    }}
    #TitleLabel {{ color: {TEXT_PRIMARY}; font-weight: 600; font-size: 14px; }}
    QPushButton#WinBtn {{
        background: transparent; border: none; color: {TEXT_SECONDARY};
        font-size: 16px; padding: 6px 12px; border-radius: 8px;
    }}
    QPushButton#WinBtn:hover {{ background: {BG_HOVER}; color: {TEXT_PRIMARY}; }}
    QPushButton#WinClose:hover {{ background: {accent}; color: white; }}

    /* ============ SIDEBAR ============ */
    #Sidebar {{ background: {bg_panel}; border-right: 1px solid {BORDER}; }}
    QPushButton#NavBtn {{
        background: transparent; border: none; color: {TEXT_SECONDARY};
        text-align: left; padding: 12px 16px; border-radius: {RADIUS}px;
        font-size: 13px;
    }}
    QPushButton#NavBtn:hover {{ background: {BG_HOVER}; color: {TEXT_PRIMARY}; }}
    QPushButton#NavBtn:checked {{ background: {accent}; color: white; font-weight: 600; }}

    /* ============ VIDEO / CONTROLS ============ */
    #VideoContainer {{ background: #000000; border-radius: {RADIUS}px; }}
    #ControlPanel {{
        background: {bg_panel};
        border-top: 1px solid {BORDER};
        border-bottom-left-radius: {RADIUS}px;
        border-bottom-right-radius: {RADIUS}px;
    }}
    QPushButton#CtrlBtn {{
        background: {bg_elevated}; border: none; color: {TEXT_PRIMARY};
        border-radius: {RADIUS}px; padding: 10px 16px; font-weight: 600;
    }}
    QPushButton#CtrlBtn:hover {{ background: {BG_HOVER}; }}
    QPushButton#CtrlBtn:pressed {{ background: {accent_press}; }}

    QPushButton#PlayBtn {{
        background: {accent}; border: none; color: white;
        border-radius: {RADIUS}px; padding: 12px 22px; font-weight: 700;
    }}
    QPushButton#PlayBtn:hover {{ background: {accent_hover}; }}
    QPushButton#PlayBtn:pressed {{ background: {accent_press}; }}

    /* ============ SLIDERS ============ */
    QSlider::groove:horizontal {{
        height: 4px; background: {bg_elevated}; border-radius: 2px;
    }}
    QSlider::sub-page:horizontal {{ background: {accent}; border-radius: 2px; }}
    QSlider::handle:horizontal {{
        background: {TEXT_PRIMARY}; width: 14px; height: 14px;
        margin: -5px 0; border-radius: 7px;
    }}
    QSlider::handle:horizontal:hover {{ background: {accent_hover}; }}

    /* ============ SCROLLBAR (A2) ============ */
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 0;
        border: none;
    }}
    QScrollBar::handle:vertical {{
        background: rgba(160, 160, 171, 80);
        min-height: 30px;
        border-radius: 5px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {accent};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        background: none; border: none; height: 0;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}
    QScrollBar:horizontal {{
        background: transparent; height: 10px; margin: 0; border: none;
    }}
    QScrollBar::handle:horizontal {{
        background: rgba(160, 160, 171, 80);
        min-width: 30px; border-radius: 5px; margin: 2px;
    }}
    QScrollBar::handle:horizontal:hover {{ background: {accent}; }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        background: none; border: none; width: 0;
    }}
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: none;
    }}

    /* ============ CHECKBOX (A3) ============ */
    QCheckBox {{
        color: {TEXT_PRIMARY};
        spacing: 8px;
        font-size: 13px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 2px solid {BORDER};
        background: {bg_elevated};
    }}
    QCheckBox::indicator:hover {{
        border-color: {accent};
    }}
    QCheckBox::indicator:checked {{
        background: {accent};
        border-color: {accent};
    }}

    /* ============ COMBOBOX (A3) ============ */
    QComboBox {{
        background: {bg_elevated};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 6px 12px;
        color: {TEXT_PRIMARY};
        min-width: 80px;
    }}
    QComboBox:hover {{
        border-color: {accent};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox QAbstractItemView {{
        background: {bg_elevated};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 4px;
        color: {TEXT_PRIMARY};
        selection-background-color: {accent};
        outline: none;
    }}
    QComboBox QAbstractItemView::item {{
        padding: 6px 12px;
        border-radius: 4px;
        min-height: 24px;
    }}
    QComboBox QAbstractItemView::item:hover {{
        background: {BG_HOVER};
    }}

    /* ============ QLABEL ============ */
    #TimeLabel {{ color: {TEXT_SECONDARY}; font-family: "Consolas", monospace; font-size: 12px; }}

    /* ============ TOOLTIP ============ */
    QToolTip {{
        background: {BG_ELEVATED}; color: {TEXT_PRIMARY};
        border: 1px solid {BORDER}; border-radius: 6px; padding: 6px;
    }}

    /* ============ SCROLL AREA ============ */
    QScrollArea {{ background: transparent; border: none; }}
    QScrollArea > QWidget > QWidget {{ background: transparent; }}

    /* ============ SETTINGS CARD ============ */
    QFrame#SettingsCard {{
        background: {bg_elevated};
        border: 1px solid {BORDER};
        border-radius: 16px;
    }}
    QLabel {{ background: transparent; }}

    /* ============ STATUSBAR (E1) ============ */
    #StatusBar {{
        background: {bg_panel};
        border-top: 1px solid {BORDER};
        color: {TEXT_SECONDARY};
        font-size: 11px;
    }}
    #StatusBar QLabel {{
        color: {TEXT_SECONDARY};
        padding: 4px 12px;
    }}
    """


def apply_theme(app: QApplication):
    app.setStyleSheet(build_qss())