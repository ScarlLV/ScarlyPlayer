# main.py
import sys
from PySide6.QtWidgets import QApplication
from core.i18n import translator
from core.settings import settings
from core.theme import apply_theme
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ScarlyPlayer")
    app.setOrganizationName("ScarlyPlayer")
    
    # 1. Язык
    saved_lang = settings().get_language()
    translator().set_language(saved_lang)
    
    # 2. Тема (динамическая)
    apply_theme(app)

    # 3. Окно
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()