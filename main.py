"""Kivo — a lightweight desktop teleprompter."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ui.mainwindow import MainWindow  # noqa: E402
from ui.selector import select_text_file  # noqa: E402


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Kivo")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("Kivo")
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))

    file_path = select_text_file()
    if not file_path:
        return

    window = MainWindow(file_path)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
