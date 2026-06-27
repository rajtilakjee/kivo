from PySide6.QtWidgets import QFileDialog


def select_text_file():
    filename, _ = QFileDialog.getOpenFileName(
        None,
        "Select a text file",
        "",
        "Text Files (*.txt);;All Files (*)"
    )

    return filename