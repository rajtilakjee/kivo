from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEvent, QPoint, QSettings, Qt, QTimer, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QGuiApplication,
    QKeyEvent,
    QMouseEvent,
    QTextBlockFormat,
    QTextCharFormat,
    QTextCursor,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSizeGrip,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.capture import exclude_from_capture
from ui.selector import select_text_file
from ui.styles import STYLESHEET

MIN_WIDTH = 400
MIN_HEIGHT = 170
DEFAULT_WIDTH = 580
DEFAULT_HEIGHT = 250
SCROLL_INTERVAL_MS = 16
SCROLL_DELAY_MS = 3000
FILE_POLL_MS = 1000
DEFAULT_SPEED = 0.5
MIN_SPEED = 0.2
MAX_SPEED = 8.0
SPEED_STEP = 0.2
DEFAULT_FONT_SIZE = 16
MIN_FONT_SIZE = 12
MAX_FONT_SIZE = 36
FONT_STEP = 2
DEFAULT_OPACITY = 0.86
MIN_OPACITY = 0.35
OPACITY_STEP = 0.05
EDGE_MARGIN = 8
SKIP_STEP = 40


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


class SeekBar(QProgressBar):
    seeked = Signal(float)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._seek(event)
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._seek(event)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def _seek(self, event: QMouseEvent) -> None:
        ratio = event.position().x() / max(1, self.width())
        self.seeked.emit(min(1.0, max(0.0, ratio)))


class PromptView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.editor = QTextEdit(self)
        self.editor.setReadOnly(True)
        self.editor.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.editor.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.editor.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.editor.document().setDocumentMargin(6)

        font = QFont()
        font.setFamilies(
            [
                "Segoe UI Variable Display",
                "Segoe UI",
                "SF Pro Text",
                "Helvetica Neue",
                "sans-serif",
            ]
        )
        font.setPixelSize(DEFAULT_FONT_SIZE)
        font.setWeight(QFont.Weight.Medium)
        self.editor.setFont(font)
        self.editor.document().setDefaultFont(font)
        self._font_size = DEFAULT_FONT_SIZE

        self.top_fade = QWidget(self)
        self.top_fade.setObjectName("topFade")
        self.top_fade.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.bottom_fade = QWidget(self)
        self.bottom_fade.setObjectName("bottomFade")
        self.bottom_fade.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.pause_badge = QLabel("PAUSED", self)
        self.pause_badge.setObjectName("pauseBadge")
        self.pause_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pause_badge.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.pause_badge.hide()

        self.hint = QLabel("Press ? for controls", self)
        self.hint.setObjectName("hint")
        self.hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.toast = QLabel("", self)
        self.toast.setObjectName("toast")
        self.toast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.toast.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.toast.hide()

        self.help_card = QLabel(
            "<b>Controls</b><br>"
            "↑ ↓&nbsp;&nbsp;Speed<br>"
            "← →&nbsp;&nbsp;Skip<br>"
            "+ −&nbsp;&nbsp;Font size<br>"
            "[ ]&nbsp;&nbsp;Opacity<br>"
            "Space&nbsp;&nbsp;Pause<br>"
            "R&nbsp;&nbsp;Restart<br>"
            "Ctrl+O&nbsp;&nbsp;Open file<br>"
            "?&nbsp;&nbsp;Hide this<br>"
            "Esc&nbsp;&nbsp;Close Kivo",
            self,
        )
        self.help_card.setObjectName("helpCard")
        self.help_card.setTextFormat(Qt.TextFormat.RichText)
        self.help_card.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.help_card.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.help_card.hide()

        self._toast_timer = QTimer(self)
        self._toast_timer.setSingleShot(True)
        self._toast_timer.timeout.connect(self.toast.hide)

        QTimer.singleShot(4500, self.hint.hide)

    def set_font_size(self, size: int) -> None:
        self._font_size = size
        font = self.editor.font()
        font.setPixelSize(size)
        self.editor.setFont(font)
        self.editor.document().setDefaultFont(font)

        scrollbar = self.editor.verticalScrollBar()
        maximum = scrollbar.maximum()
        ratio = scrollbar.value() / maximum if maximum else 0.0

        cursor = self.editor.textCursor()
        saved = cursor.position()
        cursor.select(QTextCursor.SelectionType.Document)
        char_format = QTextCharFormat()
        char_format.setFont(font)
        cursor.mergeCharFormat(char_format)
        cursor.setPosition(saved)
        self.editor.setTextCursor(cursor)

        self._apply_line_height()

        new_max = scrollbar.maximum()
        scrollbar.setValue(int(ratio * new_max))

    def apply_text(self, text: str) -> None:
        self.editor.setPlainText(text)
        self.set_font_size(self._font_size)

    def set_paused(self, paused: bool) -> None:
        self.pause_badge.setVisible(paused)
        self._layout_overlays()

    def show_toast(self, message: str) -> None:
        self.hint.hide()
        self.help_card.hide()
        self.toast.setText(message)
        self.toast.adjustSize()
        self.toast.show()
        self._layout_overlays()
        self._toast_timer.start(1400)

    def hide_hint(self) -> None:
        self.hint.hide()

    def is_help_visible(self) -> bool:
        return self.help_card.isVisible()

    def toggle_help(self) -> None:
        self.hint.hide()
        self.toast.hide()
        self.help_card.setVisible(not self.help_card.isVisible())
        self._layout_overlays()

    def hide_help(self) -> None:
        self.help_card.hide()

    def _apply_line_height(self) -> None:
        cursor = self.editor.textCursor()
        saved = cursor.position()
        cursor.select(QTextCursor.SelectionType.Document)
        block_format = QTextBlockFormat()
        block_format.setLineHeight(
            148,
            QTextBlockFormat.LineHeightTypes.ProportionalHeight.value,
        )
        cursor.mergeBlockFormat(block_format)
        cursor.setPosition(saved)
        self.editor.setTextCursor(cursor)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.editor.setGeometry(self.rect())
        self._layout_overlays()

    def _layout_overlays(self) -> None:
        width = self.width()
        height = self.height()
        fade = max(28, min(48, height // 5))

        self.top_fade.setGeometry(0, 0, width, fade)
        self.bottom_fade.setGeometry(0, height - fade, width, fade)
        self.top_fade.setStyleSheet(
            """
            #topFade {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(10, 14, 22, 140),
                    stop:1 rgba(10, 14, 22, 0)
                );
            }
            """
        )
        self.bottom_fade.setStyleSheet(
            """
            #bottomFade {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(10, 14, 22, 0),
                    stop:1 rgba(10, 14, 22, 140)
                );
            }
            """
        )

        self.pause_badge.adjustSize()
        self.pause_badge.move(
            (width - self.pause_badge.width()) // 2,
            (height - self.pause_badge.height()) // 2,
        )

        self.hint.adjustSize()
        self.hint.move(
            (width - self.hint.width()) // 2,
            height - self.hint.height() - 10,
        )

        self.toast.adjustSize()
        self.toast.move(
            (width - self.toast.width()) // 2,
            height - self.toast.height() - 10,
        )

        self.help_card.adjustSize()
        self.help_card.move(
            (width - self.help_card.width()) // 2,
            (height - self.help_card.height()) // 2,
        )

        self.top_fade.raise_()
        self.bottom_fade.raise_()
        self.pause_badge.raise_()
        self.hint.raise_()
        self.toast.raise_()
        self.help_card.raise_()


class MainWindow(QMainWindow):
    def __init__(self, file_path: str) -> None:
        super().__init__()

        self.file_path = Path(file_path)
        self.scroll_delay = SCROLL_DELAY_MS
        self.is_paused = False
        self.scroll_speed = DEFAULT_SPEED
        self.scroll_position = 0.0
        self.font_size = DEFAULT_FONT_SIZE
        self._last_text = ""
        self._last_mtime: float | None = None
        self._drag_pos: QPoint | None = None
        self._resize_edges = ""
        self._resize_origin: tuple[int, int, int, int] | None = None
        self._resize_cursor: QPoint | None = None

        self.setWindowTitle("Kivo")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        self.resize(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        self.setStyleSheet(STYLESHEET)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._build_ui()
        self._restore_settings()
        self._position_default()
        self._setup_timers()
        self.load_text(force=True)
        self.setFocus()

    def _build_ui(self) -> None:
        self.brand = QLabel("KIVO")
        self.brand.setObjectName("brand")

        self.filename_label = QLabel(self.file_path.name)
        self.filename_label.setObjectName("filename")
        self.filename_label.setToolTip(str(self.file_path))
        self.filename_label.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Preferred,
        )

        self.status_chip = QLabel("LIVE")
        self.status_chip.setObjectName("chip")

        self.speed_chip = QLabel(self._speed_label())
        self.speed_chip.setObjectName("chip")

        help_button = QPushButton("?")
        help_button.setObjectName("helpButton")
        help_button.setFixedSize(24, 24)
        help_button.setCursor(Qt.CursorShape.PointingHandCursor)
        help_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        help_button.setToolTip("Show controls")

        close_button = QPushButton("✕")
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(24, 24)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        close_button.clicked.connect(self.close)

        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(40)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 6, 10, 6)
        header_layout.setSpacing(10)
        header_layout.addWidget(self.brand)
        header_layout.addWidget(self.filename_label, 1)
        header_layout.addWidget(self.status_chip)
        header_layout.addWidget(self.speed_chip)
        header_layout.addWidget(help_button)
        header_layout.addWidget(close_button)

        self.prompt = PromptView()
        self.prompt.installEventFilter(self)
        self.prompt.editor.installEventFilter(self)
        help_button.clicked.connect(self.prompt.toggle_help)

        self.seek_bar = SeekBar()
        self.seek_bar.setObjectName("seekBar")
        self.seek_bar.setTextVisible(False)
        self.seek_bar.setRange(0, 1000)
        self.seek_bar.setValue(0)
        self.seek_bar.seeked.connect(self._seek_to)

        footer = QWidget()
        footer.setObjectName("footer")
        footer.setFixedHeight(18)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 4, 6, 6)
        footer_layout.setSpacing(6)
        footer_layout.addWidget(self.seek_bar, 1)
        footer_layout.addWidget(QSizeGrip(footer))

        container = QWidget()
        container.setObjectName("container")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(header)
        layout.addWidget(self.prompt, 1)
        layout.addWidget(footer)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(22)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 70))
        container.setGraphicsEffect(shadow)

        self._container = container
        self.setCentralWidget(container)

    def _setup_timers(self) -> None:
        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self.auto_scroll)

        self.start_scroll_timer = QTimer(self)
        self.start_scroll_timer.setSingleShot(True)
        self.start_scroll_timer.timeout.connect(
            lambda: self.scroll_timer.start(SCROLL_INTERVAL_MS)
        )

        self.reload_timer = QTimer(self)
        self.reload_timer.timeout.connect(self.load_text)
        self.reload_timer.start(FILE_POLL_MS)

    def _restore_settings(self) -> None:
        settings = QSettings()
        geometry = settings.value("geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)

        speed = settings.value("speed", DEFAULT_SPEED)
        try:
            self.scroll_speed = min(MAX_SPEED, max(MIN_SPEED, float(speed)))
        except (TypeError, ValueError):
            self.scroll_speed = DEFAULT_SPEED
        self.speed_chip.setText(self._speed_label())

        font_size = settings.value("font_size", DEFAULT_FONT_SIZE)
        try:
            self.font_size = min(MAX_FONT_SIZE, max(MIN_FONT_SIZE, int(font_size)))
        except (TypeError, ValueError):
            self.font_size = DEFAULT_FONT_SIZE
        self.prompt.set_font_size(self.font_size)

        opacity = settings.value("opacity", DEFAULT_OPACITY)
        try:
            opacity = float(opacity)
            # Old default was fully opaque; pick up the new glass look.
            if opacity >= 0.995:
                opacity = DEFAULT_OPACITY
            self.setWindowOpacity(min(1.0, max(MIN_OPACITY, opacity)))
        except (TypeError, ValueError):
            self.setWindowOpacity(DEFAULT_OPACITY)

    def _position_default(self) -> None:
        settings = QSettings()
        if settings.value("geometry") is not None:
            return

        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return

        geometry = screen.availableGeometry()
        x = geometry.x() + (geometry.width() - self.width()) // 2
        y = geometry.y() + 16
        self.move(x, y)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._apply_capture_exclusion()
        for delay in (100, 400, 1200):
            QTimer.singleShot(delay, self._apply_capture_exclusion)
        self.activateWindow()
        self.raise_()
        self.setFocus()

    def changeEvent(self, event: QEvent) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.WinIdChange:
            self._apply_capture_exclusion()

    def _apply_capture_exclusion(self) -> None:
        hwnd = int(self.winId())
        exclude_from_capture(hwnd)
        window = self.windowHandle()
        if window is not None:
            native = int(window.winId())
            if native != hwnd:
                exclude_from_capture(native)

    def closeEvent(self, event) -> None:
        settings = QSettings()
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("speed", self.scroll_speed)
        settings.setValue("font_size", self.font_size)
        settings.setValue("opacity", self.windowOpacity())
        super().closeEvent(event)

    def load_text(self, force: bool = False) -> None:
        path = self.file_path
        if not path.exists():
            return

        try:
            mtime = path.stat().st_mtime
            if not force and mtime == self._last_mtime:
                return
            text = _read_text(path)
        except OSError:
            return

        if not force and text == self._last_text:
            self._last_mtime = mtime
            return

        self._last_mtime = mtime
        self._last_text = text
        self.prompt.apply_text(text)
        self.filename_label.setText(path.name)
        self.filename_label.setToolTip(str(path))

        self.scroll_position = 0
        self.prompt.editor.verticalScrollBar().setValue(0)
        self._update_progress()
        self._set_paused(False)

        self.scroll_timer.stop()
        self.start_scroll_timer.start(self.scroll_delay)

    def auto_scroll(self) -> None:
        scrollbar = self.prompt.editor.verticalScrollBar()
        if scrollbar.maximum() == 0:
            self._update_progress()
            return

        if self.scroll_position < scrollbar.maximum():
            self.scroll_position += self.scroll_speed
            scrollbar.setValue(int(self.scroll_position))

        self._update_progress()

    def _seek_to(self, ratio: float) -> None:
        scrollbar = self.prompt.editor.verticalScrollBar()
        self.scroll_position = ratio * scrollbar.maximum()
        scrollbar.setValue(int(self.scroll_position))
        self._update_progress()

    def _update_progress(self) -> None:
        scrollbar = self.prompt.editor.verticalScrollBar()
        maximum = scrollbar.maximum()
        if maximum <= 0:
            self.seek_bar.setValue(0)
            return
        self.seek_bar.setValue(int((scrollbar.value() / maximum) * 1000))

    def _set_paused(self, paused: bool) -> None:
        self.is_paused = paused
        self.status_chip.setText("PAUSED" if paused else "LIVE")
        self.status_chip.setProperty("state", "paused" if paused else "")
        self.status_chip.style().unpolish(self.status_chip)
        self.status_chip.style().polish(self.status_chip)
        self._container.setProperty("paused", "true" if paused else "false")
        self._container.style().unpolish(self._container)
        self._container.style().polish(self._container)
        self.prompt.set_paused(paused)

    def _toggle_pause(self) -> None:
        if self.is_paused:
            self._set_paused(False)
            scrollbar = self.prompt.editor.verticalScrollBar()
            if scrollbar.value() == 0:
                self.start_scroll_timer.start(self.scroll_delay)
            else:
                self.scroll_timer.start(SCROLL_INTERVAL_MS)
            return

        self._set_paused(True)
        self.scroll_timer.stop()
        self.start_scroll_timer.stop()

    def _adjust_speed(self, delta: float) -> None:
        self.scroll_speed = min(MAX_SPEED, max(MIN_SPEED, self.scroll_speed + delta))
        self.speed_chip.setText(self._speed_label())
        self.prompt.show_toast(self._speed_label())

    def _adjust_font(self, delta: int) -> None:
        self.font_size = min(MAX_FONT_SIZE, max(MIN_FONT_SIZE, self.font_size + delta))
        self.prompt.set_font_size(self.font_size)
        self.scroll_position = float(self.prompt.editor.verticalScrollBar().value())
        self._update_progress()
        self.prompt.show_toast(f"Font {self.font_size}px")

    def _adjust_opacity(self, delta: float) -> None:
        opacity = min(1.0, max(MIN_OPACITY, self.windowOpacity() + delta))
        self.setWindowOpacity(opacity)
        self.prompt.show_toast(f"Opacity {int(opacity * 100)}%")

    def _nudge_scroll(self, amount: int) -> None:
        scrollbar = self.prompt.editor.verticalScrollBar()
        self.scroll_position = min(
            scrollbar.maximum(),
            max(0.0, float(scrollbar.value() + amount)),
        )
        scrollbar.setValue(int(self.scroll_position))
        self._update_progress()

    def _restart(self) -> None:
        self.scroll_position = 0
        self.prompt.editor.verticalScrollBar().setValue(0)
        self._update_progress()
        self._set_paused(False)
        self.scroll_timer.stop()
        self.start_scroll_timer.start(self.scroll_delay)
        self.prompt.show_toast("Restarted")

    def _open_file(self) -> None:
        filename = select_text_file(self)
        if not filename:
            return
        self.file_path = Path(filename)
        self._last_text = ""
        self._last_mtime = None
        self.load_text(force=True)
        self.prompt.show_toast(self.file_path.name)

    def _speed_label(self) -> str:
        return f"{self.scroll_speed:.1f}×"

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        modifiers = event.modifiers()

        if key in (
            Qt.Key.Key_Question,
            Qt.Key.Key_Slash,
            Qt.Key.Key_F1,
        ) or (
            key == Qt.Key.Key_H and not modifiers & Qt.KeyboardModifier.ControlModifier
        ):
            self.prompt.toggle_help()
            return

        self.prompt.hide_hint()
        if key != Qt.Key.Key_Escape:
            self.prompt.hide_help()

        if key == Qt.Key.Key_Escape:
            if self.prompt.is_help_visible():
                self.prompt.hide_help()
            else:
                self.close()
        elif key == Qt.Key.Key_Space:
            self._toggle_pause()
        elif key == Qt.Key.Key_Up:
            self._adjust_speed(SPEED_STEP)
        elif key == Qt.Key.Key_Down:
            self._adjust_speed(-SPEED_STEP)
        elif key == Qt.Key.Key_Left:
            self._nudge_scroll(-SKIP_STEP)
        elif key == Qt.Key.Key_Right:
            self._nudge_scroll(SKIP_STEP)
        elif key in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
            self._adjust_font(FONT_STEP)
        elif key == Qt.Key.Key_Minus:
            self._adjust_font(-FONT_STEP)
        elif key == Qt.Key.Key_BracketLeft:
            self._adjust_opacity(-OPACITY_STEP)
        elif key == Qt.Key.Key_BracketRight:
            self._adjust_opacity(OPACITY_STEP)
        elif key == Qt.Key.Key_R and not (
            modifiers & Qt.KeyboardModifier.ControlModifier
        ):
            self._restart()
        elif key == Qt.Key.Key_O and (modifiers & Qt.KeyboardModifier.ControlModifier):
            self._open_file()
        else:
            super().keyPressEvent(event)

    def eventFilter(self, watched, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Wheel and isinstance(event, QWheelEvent):
            self.wheelEvent(event)
            return True
        return super().eventFilter(watched, event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        delta = event.angleDelta().y()
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self._adjust_font(FONT_STEP if delta > 0 else -FONT_STEP)
        else:
            self._nudge_scroll(-SKIP_STEP if delta > 0 else SKIP_STEP)
        event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return

        edges = self._edges_at(event.position().toPoint())
        if edges:
            self._resize_edges = edges
            self._resize_origin = (
                self.x(),
                self.y(),
                self.width(),
                self.height(),
            )
            self._resize_cursor = event.globalPosition().toPoint()
        else:
            self._drag_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = event.position().toPoint()

        if self._resize_edges and self._resize_origin and self._resize_cursor:
            self._apply_resize(event.globalPosition().toPoint())
            event.accept()
            return

        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
            return

        self._update_resize_cursor(self._edges_at(pos))
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_pos = None
        self._resize_edges = ""
        self._resize_origin = None
        self._resize_cursor = None
        self._update_resize_cursor(self._edges_at(event.position().toPoint()))
        event.accept()

    def _edges_at(self, pos: QPoint) -> str:
        rect = self.rect()
        edges = ""
        if pos.x() <= EDGE_MARGIN:
            edges += "L"
        elif pos.x() >= rect.width() - EDGE_MARGIN:
            edges += "R"
        if pos.y() <= EDGE_MARGIN:
            edges += "T"
        elif pos.y() >= rect.height() - EDGE_MARGIN:
            edges += "B"
        return edges

    def _update_resize_cursor(self, edges: str) -> None:
        cursors = {
            "L": Qt.CursorShape.SizeHorCursor,
            "R": Qt.CursorShape.SizeHorCursor,
            "T": Qt.CursorShape.SizeVerCursor,
            "B": Qt.CursorShape.SizeVerCursor,
            "LT": Qt.CursorShape.SizeFDiagCursor,
            "RB": Qt.CursorShape.SizeFDiagCursor,
            "RT": Qt.CursorShape.SizeBDiagCursor,
            "LB": Qt.CursorShape.SizeBDiagCursor,
        }
        self.setCursor(cursors.get(edges, Qt.CursorShape.ArrowCursor))

    def _apply_resize(self, global_pos: QPoint) -> None:
        if not self._resize_origin or not self._resize_cursor:
            return

        x, y, width, height = self._resize_origin
        delta = global_pos - self._resize_cursor

        if "L" in self._resize_edges:
            x += delta.x()
            width -= delta.x()
        if "R" in self._resize_edges:
            width += delta.x()
        if "T" in self._resize_edges:
            y += delta.y()
            height -= delta.y()
        if "B" in self._resize_edges:
            height += delta.y()

        width = max(MIN_WIDTH, width)
        height = max(MIN_HEIGHT, height)
        self.setGeometry(x, y, width, height)
