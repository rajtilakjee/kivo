import sys

from PySide6.QtWidgets import QApplication

from ui.selector import select_text_file
from ui.mainwindow import MainWindow


def main():
    app = QApplication(sys.argv)

    file_path = select_text_file()

    if not file_path:
        return

    window = MainWindow(file_path)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()