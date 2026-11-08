# main.py
import sys
from PySide6.QtWidgets import QApplication

from core.i18n import translator
from core.settings import settings
from core.theme import build_qss
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ScarlyPlayer")
    app.setOrganizationName("ScarlyPlayer")
    app.setStyleSheet(build_qss())

    # ★ подтягиваем сохранённый язык ещё до UI
    saved_lang = settings().get_language()
    translator().set_language(saved_lang) if saved_lang != translator().language else None
    # ↑ проще: напрямую задать
    # translator()._lang = saved_lang  # но лучше через сеттер:
    tr_obj = translator()
    if tr_obj.language != saved_lang:
        tr_obj.set_language(saved_lang)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()