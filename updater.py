# core/updater.py
"""Проверка обновлений через GitHub API (без серверов)."""

from __future__ import annotations
import json
import ssl
import urllib.request
import urllib.error

from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool
from PySide6.QtWidgets import QMessageBox

from core.i18n import APP_VERSION, APP_REPO, tr


class UpdateCheckerSignals(QObject):
    finished = Signal(str, str)  # latest_version, download_url
    error    = Signal(str)


class _UpdateWorker(QRunnable):
    def __init__(self, signals: UpdateCheckerSignals):
        super().__init__()
        self.signals = signals

    def run(self):
        try:
            # https://github.com/user/repo → user/repo
            repo = APP_REPO.rstrip("/").split("github.com/")[-1]
            api_url = f"https://api.github.com/repos/{repo}/releases/latest"

            req = urllib.request.Request(
                api_url,
                headers={
                    "User-Agent": "ScarlyPlayer-UpdateChecker/1.0",
                    "Accept": "application/vnd.github+json",
                },
            )

            # SSL-контекст (иногда на Windows проблемы с сертификатами)
            ctx = ssl.create_default_context()

            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            latest = (data.get("tag_name") or "").lstrip("v")
            url = data.get("html_url") or APP_REPO

            if not latest:
                self.signals.error.emit("Пустой tag_name в ответе GitHub")
                return

            self.signals.finished.emit(latest, url)

        except urllib.error.HTTPError as e:
            if e.code == 404:
                msg = f"Репозиторий не найден: {APP_REPO}\nПроверь APP_REPO в core/i18n.py"
            elif e.code == 403:
                msg = "GitHub API временно заблокировал запрос (rate limit). Попробуй позже."
            else:
                msg = f"HTTP {e.code}: {e.reason}"
            print(f"[Updater] HTTPError: {msg}")
            self.signals.error.emit(msg)

        except urllib.error.URLError as e:
            msg = f"Нет соединения: {e.reason}"
            print(f"[Updater] URLError: {msg}")
            self.signals.error.emit(msg)

        except Exception as e:
            msg = f"{type(e).__name__}: {e}"
            print(f"[Updater] Exception: {msg}")
            self.signals.error.emit(msg)


class UpdateChecker(QObject):
    def __init__(self, parent_widget):
        super().__init__()
        self.parent_widget = parent_widget
        self.signals = UpdateCheckerSignals()
        self.signals.finished.connect(self._on_finished)
        self.signals.error.connect(self._on_error)

    def check(self):
        worker = _UpdateWorker(self.signals)
        QThreadPool.globalInstance().start(worker)

    def _on_finished(self, latest: str, url: str):
        if self._is_newer(latest, APP_VERSION):
            ans = QMessageBox.question(
                self.parent_widget,
                tr("settings.check_updates"),
                tr("settings.check_updates.available").format(v=latest)
                + f"\n\nТекущая: {APP_VERSION}\nОткрыть страницу релиза?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if ans == QMessageBox.Yes:
                from PySide6.QtGui import QDesktopServices
                from PySide6.QtCore import QUrl
                QDesktopServices.openUrl(QUrl(url))
        else:
            QMessageBox.information(
                self.parent_widget,
                tr("settings.check_updates"),
                tr("settings.check_updates.up_to_date")
                + f"\n\nТекущая: {APP_VERSION}\nПоследняя: {latest}",
            )

    def _on_error(self, err: str):
        QMessageBox.warning(
            self.parent_widget,
            tr("settings.check_updates"),
            tr("settings.check_updates.error") + f"\n\n{err}",
        )

    @staticmethod
    def _is_newer(latest: str, current: str) -> bool:
        try:
            l = tuple(int(x) for x in latest.split("."))
            c = tuple(int(x) for x in current.split("."))
            return l > c
        except Exception:
            # Если версии не парсятся как числа — считаем, что обновление есть
            return latest != current