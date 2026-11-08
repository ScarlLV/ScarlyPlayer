# core/theme.py
"""Централизованная тема ScarlyPlayer (v1.0)."""

ACCENT        = "#E53935"   # основной красный
ACCENT_HOVER  = "#FF5252"
ACCENT_PRESS  = "#C62828"

BG_DARK       = "#0F0F12"
BG_PANEL      = "#17171C"
BG_ELEVATED   = "#1F1F26"
BG_HOVER      = "#2A2A33"

TEXT_PRIMARY   = "#F5F5F7"
TEXT_SECONDARY = "#A0A0AB"
TEXT_DISABLED  = "#5A5A66"

BORDER        = "#2A2A33"
RADIUS        = 12


def build_qss() -> str:
    """Собирает глобальный стиль приложения."""
    return f"""
    QWidget {{
        background: {BG_DARK};
        color: {TEXT_PRIMARY};
        font-family: "Segoe UI", "SF Pro Display", "Inter", sans-serif;
        font-size: 13px;
    }}

    /* ===== Title bar ===== */
    #TitleBar {{
        background: {BG_PANEL};
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

    /* ===== Кнопки окна ===== */
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
        background: {ACCENT};
        color: white;
    }}

    /* ===== Sidebar ===== */
    #Sidebar {{
        background: {BG_PANEL};
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
        background: {ACCENT};
        color: white;
        font-weight: 600;
    }}

    /* ===== Видео-область ===== */
    #VideoContainer {{
        background: #000000;
        border-radius: {RADIUS}px;
    }}

    /* ===== Control panel ===== */
    #ControlPanel {{
        background: {BG_PANEL};
        border-top: 1px solid {BORDER};
        border-bottom-left-radius: {RADIUS}px;
        border-bottom-right-radius: {RADIUS}px;
    }}

    QPushButton#CtrlBtn {{
        background: {BG_ELEVATED};
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
        background: {ACCENT};
        border: none;
        color: white;
        border-radius: {RADIUS}px;
        padding: 12px 22px;
        font-weight: 700;
        font-size: 14px;
    }}
    QPushButton#PlayBtn:hover  {{ background: {ACCENT_HOVER}; }}
    QPushButton#PlayBtn:pressed{{ background: {ACCENT_PRESS}; }}

    /* ===== Слайдеры ===== */
    QSlider::groove:horizontal {{
        height: 4px;
        background: {BG_ELEVATED};
        border-radius: 2px;
    }}
    QSlider::sub-page:horizontal {{
        background: {ACCENT};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {TEXT_PRIMARY};
        width: 14px; height: 14px;
        margin: -5px 0;
        border-radius: 7px;
    }}
    QSlider::handle:horizontal:hover {{
        background: {ACCENT_HOVER};
    }}

    /* ===== Метки ===== */
    #TimeLabel {{
        color: {TEXT_SECONDARY};
        font-family: "Consolas", monospace;
        font-size: 12px;
    }}

    /* ===== Tooltip ===== */
    QToolTip {{
        background: {BG_ELEVATED};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px;
    }}
    """