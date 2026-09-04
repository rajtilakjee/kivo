from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QFileDialog, QWidget


def select_text_file(parent: QWidget | None = None) -> str:
    settings = QSettings()
    start_dir = str(settings.value("last_dir", "", type=str) or "")

    filename, _ = QFileDialog.getOpenFileName(
        parent,
        "Open a script",
        start_dir,
        "Text Files (*.txt *.md);;All Files (*)",
    )

    if filename:
        settings.setValue("last_dir", str(Path(filename).parent))
        settings.setValue("last_file", filename)

    return filename
