from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication, QKeyEvent, QMouseEvent, QColor
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QMainWindow,
    QTextEdit,
    QWidget,
    QVBoxLayout,
)

from ctypes import windll

WDA_EXCLUDEFROMCAPTURE = 0x11

class MainWindow(QMainWindow):
    def __init__(self, file_path):
        super().__init__()

        self.file_path = file_path

        # Delay before scrolling starts (milliseconds)
        self.scroll_delay = 3000
        self.is_paused = False

        # Transparent window
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Frameless & always on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        self.resize(500, 200)

        self.setStyleSheet("""
            #container {
                background-color: rgba(20, 25, 35, 180);
                border-radius: 18px;
                border: 1px solid rgba(255,255,255,35);
            }

            QTextEdit {
                background: transparent;
                color: white;
                border: none;
                font-size: 12px;
                padding: 16px;
            }
        """)

        #
        # Text editor
        #
        self.editor = QTextEdit()
        self.editor.setReadOnly(True)
        self.editor.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.editor.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.editor.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        #
        # Rounded container
        #
        container = QWidget()
        container.setObjectName("container")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.editor)

        #
        # Shadow
        #
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(35)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 160))

        container.setGraphicsEffect(shadow)

        self.setCentralWidget(container)

        #
        # Position near top-center
        #
        screen = QGuiApplication.primaryScreen()
        geometry = screen.availableGeometry()

        x = geometry.x() + (geometry.width() - self.width()) // 2
        y = geometry.y() + 10

        self.move(x, y)

        #
        # Dragging
        #
        self._drag_pos = None

        #
        # Text handling
        #
        self._last_text = ""

        #
        # Teleprompter
        #
        self.scroll_speed = 0.5
        self.scroll_position = 0.0

        #
        # Scroll timer (~60 FPS)
        #
        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self.auto_scroll)

        #
        # Delay timer before scrolling begins
        #
        self.start_scroll_timer = QTimer(self)
        self.start_scroll_timer.setSingleShot(True)
        self.start_scroll_timer.timeout.connect(
            lambda: self.scroll_timer.start(16)
        )

        #
        # Load initial text
        #
        self.load_text()

        #
        # Reload file every second
        #
        self.reload_timer = QTimer(self)
        self.reload_timer.timeout.connect(self.load_text)
        self.reload_timer.start(1000)

        #
        # Keyboard focus
        #
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    def showEvent(self, event):
        super().showEvent(event)

        hwnd = int(self.winId())
        windll.user32.SetWindowDisplayAffinity(
            hwnd,
            WDA_EXCLUDEFROMCAPTURE
        )

        self.activateWindow()
        self.raise_()
        self.setFocus()

    def load_text(self):
        path = Path(self.file_path)

        if not path.exists():
            return

        text = path.read_text(encoding="utf-8")

        if text == self._last_text:
            return

        self._last_text = text

        self.editor.setPlainText(text)

        # Restart from the top
        self.scroll_position = 0
        self.editor.verticalScrollBar().setValue(0)

        self.is_paused = False
        # Stop scrolling while loading new content
        self.scroll_timer.stop()

        # Restart the delay timer
        self.start_scroll_timer.start(self.scroll_delay)

    def auto_scroll(self):
        scrollbar = self.editor.verticalScrollBar()

        if scrollbar.maximum() == 0:
            return

        if self.scroll_position < scrollbar.maximum():
            self.scroll_position += self.scroll_speed
            scrollbar.setValue(int(self.scroll_position))

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

        elif event.key() == Qt.Key.Key_Space:
            self.is_paused = not self.is_paused

            if self.is_paused:
                # Pause everything
                self.scroll_timer.stop()
                self.start_scroll_timer.stop()
            else:
                # Resume
                scrollbar = self.editor.verticalScrollBar()

                if scrollbar.value() == 0:
                    # We're still at the beginning, so honor the initial delay
                    self.start_scroll_timer.start(self.scroll_delay)
                else:
                    # We were already scrolling, continue immediately
                    self.scroll_timer.start(16)

        elif event.key() == Qt.Key.Key_Up:
            self.scroll_speed += 0.2
            print(f"Speed: {self.scroll_speed:.1f}")

        elif event.key() == Qt.Key.Key_Down:
            self.scroll_speed = max(0.2, self.scroll_speed - 0.2)
            print(f"Speed: {self.scroll_speed:.1f}")

        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if (
            self._drag_pos is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.move(
                event.globalPosition().toPoint() - self._drag_pos
            )
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None
        event.accept()