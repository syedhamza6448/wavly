import sys
import pyautogui
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QRect, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush

# ─────────────────────────────────────────
# KEYBOARD LAYOUT DEFINITION
# ─────────────────────────────────────────

FUNCTION_ROW = [
    'Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6',
    'F7', 'F8', 'F9', 'F10', 'F11', 'F12'
]

ROWS = [
    ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Back'],
    ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
    ['Caps', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'", 'Enter'],
    ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'Shift'],
    ['Ctrl', 'Win', 'Alt', 'Space', 'Alt', 'Ctrl']
]

# Keys that are wider than standard
WIDE_KEYS = {
    'Back': 1.8, 'Tab': 1.4, '\\': 1.4,
    'Caps': 1.6, 'Enter': 1.8,
    'Shift': 2.2, 'Space': 5.0,
    'Ctrl': 1.4, 'Win': 1.2, 'Alt': 1.2
}

# PyAutoGUI key name mapping
KEY_MAP = {
    'Back': 'backspace', 'Tab': 'tab', 'Caps': 'capslock',
    'Enter': 'enter', 'Shift': 'shift', 'Ctrl': 'ctrl',
    'Win': 'win', 'Alt': 'alt', 'Space': 'space',
    'Esc': 'escape', '\\': 'backslash', '`': 'grave',
    '-': 'minus', '=': 'equal', '[': 'bracketleft',
    ']': 'bracketright', ';': 'semicolon', "'": 'apostrophe',
    ',': 'comma', '.': 'period', '/': 'slash',
    'F1': 'f1', 'F2': 'f2', 'F3': 'f3', 'F4': 'f4',
    'F5': 'f5', 'F6': 'f6', 'F7': 'f7', 'F8': 'f8',
    'F9': 'f9', 'F10': 'f10', 'F11': 'f11', 'F12': 'f12',
}


class KeyboardOverlay(QWidget):
    # Signal emitted when a key is pressed via dwell
    key_pressed = pyqtSignal(str)

    def __init__(self, screen_w, screen_h, opacity=0.2):
        super().__init__()
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.opacity = opacity

        # Key size
        self.key_w = 58
        self.key_h = 48
        self.key_gap = 4

        # Fingertip dot positions {fingertip_id: (x, y)}
        self.fingertip_positions = {}

        # Dwell progress per fingertip {fingertip_id: (key_label, progress)}
        self.dwell_progress = {}

        # Currently hovered key per fingertip
        self.hovered_keys = {}

        # Built key rects for hit testing
        self.key_rects = []  # list of (QRect, key_label)

        self._setup_window()
        self._build_key_rects()

        # Repaint timer — 30fps
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(33)

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Calculate total keyboard height
        total_rows = 1 + len(ROWS)  # function row + main rows
        kb_h = total_rows * (self.key_h + self.key_gap) + self.key_gap + 20

        # Position at bottom of screen, full width
        self.setGeometry(0, self.screen_h - kb_h - 10, self.screen_w, kb_h)
        self.kb_h = kb_h

    def _build_key_rects(self):
        """Pre-calculates the QRect for every key for hit testing."""
        self.key_rects = []
        total_rows = 1 + len(ROWS)
        kb_h = total_rows * (self.key_h + self.key_gap) + self.key_gap + 20

        y = 10

        # Function row
        f_key_w = (self.screen_w - 20) // len(FUNCTION_ROW)
        for i, key in enumerate(FUNCTION_ROW):
            x = 10 + i * f_key_w
            rect = QRect(x, y, f_key_w - self.key_gap, self.key_h)
            self.key_rects.append((rect, key))

        y += self.key_h + self.key_gap

        # Main rows
        for row in ROWS:
            x = 10
            for key in row:
                multiplier = WIDE_KEYS.get(key, 1.0)
                w = int(self.key_w * multiplier)
                rect = QRect(x, y, w - self.key_gap, self.key_h)
                self.key_rects.append((rect, key))
                x += w + self.key_gap
            y += self.key_h + self.key_gap

    def get_key_at(self, x, y):
        """Returns key label at position (x, y) relative to widget, or None."""
        for rect, label in self.key_rects:
            if rect.contains(x, y):
                return label
        return None

    def update_fingertips(self, positions, dwell_progress):
        """
        Called every frame from main loop.
        positions: {fingertip_id: (screen_x, screen_y)}
        dwell_progress: {fingertip_id: (key_label, progress 0.0-1.0)}
        """
        # Convert screen coords to widget-local coords
        widget_y_offset = self.screen_h - self.kb_h - 10
        self.fingertip_positions = {
            fid: (sx, sy - widget_y_offset)
            for fid, (sx, sy) in positions.items()
        }
        self.dwell_progress = dwell_progress
        self.hovered_keys = {
            fid: self.get_key_at(lx, ly)
            for fid, (lx, ly) in self.fingertip_positions.items()
        }

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        font = QFont('Segoe UI', 10)
        painter.setFont(font)

        for rect, label in self.key_rects:
            self._draw_key(painter, rect, label)

        # Draw fingertip dots
        for fid, (lx, ly) in self.fingertip_positions.items():
            color = QColor(0, 220, 180, 220)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(lx - 8, ly - 8, 16, 16)

        painter.end()

    def _draw_key(self, painter, rect, label):
        # Check if any fingertip is hovering this key
        is_hovered = label in self.hovered_keys.values()

        # Get dwell progress for this key
        progress = 0.0
        for fid, (key_label, prog) in self.dwell_progress.items():
            if key_label == label:
                progress = prog
                break

        # Base key color
        if is_hovered:
            bg = QColor(255, 255, 255, int(self.opacity * 255 * 3))
        else:
            bg = QColor(255, 255, 255, int(self.opacity * 255))

        # Draw key background
        painter.setBrush(QBrush(bg))
        painter.setPen(QPen(QColor(255, 255, 255, 60), 1))
        painter.drawRoundedRect(rect, 6, 6)

        # Draw dwell progress fill (cyan fill from left)
        if progress > 0:
            fill_w = int(rect.width() * progress)
            fill_rect = QRect(rect.x(), rect.y(), fill_w, rect.height())
            painter.setBrush(QBrush(QColor(0, 220, 180, 120)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(fill_rect, 6, 6)

        # Draw key label
        if is_hovered:
            painter.setPen(QPen(QColor(255, 255, 255, 255)))
        else:
            painter.setPen(QPen(QColor(255, 255, 255, int(self.opacity * 255 * 6))))

        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, label)