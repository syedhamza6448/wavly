from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush

# ─────────────────────────────────────────
# KEYBOARD LAYOUT
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

WIDE_KEYS = {
    'Back': 1.8, 'Tab': 1.4, '\\': 1.4,
    'Caps': 1.6, 'Enter': 1.8,
    'Shift': 2.2, 'Space': 5.0,
    'Ctrl': 1.4, 'Win': 1.2, 'Alt': 1.2
}

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
    def __init__(self, screen_w, screen_h, opacity=0.2):
        super().__init__()
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.opacity  = opacity

        self.key_h   = 52
        self.key_gap = 5
        self.padding = 8

        self.fingertip_positions = {}
        self.dwell_progress      = {}
        self.hovered_keys        = {}
        self.key_rects           = []

        self._setup_window()
        self._build_key_rects()

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

        total_rows    = 1 + len(ROWS)
        self.kb_h     = (
            total_rows * (self.key_h + self.key_gap)
            + self.key_gap
            + self.padding * 2
        )
        self._kb_y_offset = self.screen_h - self.kb_h
        self.setGeometry(
            0,
            self._kb_y_offset,
            self.screen_w,
            self.kb_h
        )

    def set_position(self, position='bottom'):
        """Moves the keyboard window based on position setting."""
        if position == 'top':
            y = 0
        elif position == 'center':
            y = (self.screen_h - self.kb_h) // 2
        else:
            y = self.screen_h - self.kb_h

        self._kb_y_offset = y
        self.setGeometry(0, y, self.screen_w, self.kb_h)
        self._build_key_rects()

    def _row_unit_width(self, row):
        return sum(WIDE_KEYS.get(k, 1.0) for k in row)

    def _build_key_rects(self):
        """
        Calculates key rects so every row fills exactly screen_w.
        Each row gets its own unit size so all rows are flush.
        """
        self.key_rects = []
        y = self.padding

        # Function row
        total_units = len(FUNCTION_ROW)
        total_gap   = self.key_gap * (len(FUNCTION_ROW) - 1)
        unit_w      = (
            self.screen_w - self.padding * 2 - total_gap
        ) / total_units

        x = self.padding
        for key in FUNCTION_ROW:
            w    = int(unit_w)
            rect = QRect(int(x), y, w - 1, self.key_h)
            self.key_rects.append((rect, key))
            x += unit_w + self.key_gap

        y += self.key_h + self.key_gap

        # Main rows
        for row in ROWS:
            total_units = self._row_unit_width(row)
            total_gap   = self.key_gap * (len(row) - 1)
            unit_w      = (
                self.screen_w - self.padding * 2 - total_gap
            ) / total_units

            x = self.padding
            for key in row:
                multiplier = WIDE_KEYS.get(key, 1.0)
                w          = int(unit_w * multiplier)
                rect       = QRect(int(x), y, w - 1, self.key_h)
                self.key_rects.append((rect, key))
                x += w + self.key_gap

            y += self.key_h + self.key_gap

    def get_key_at(self, x, y):
        for rect, label in self.key_rects:
            if rect.contains(int(x), int(y)):
                return label
        return None

    def update_fingertips(self, positions, dwell_progress):
        widget_y_offset = self._kb_y_offset
        self.fingertip_positions = {
            fid: (sx, sy - widget_y_offset)
            for fid, (sx, sy) in positions.items()
        }
        self.dwell_progress = dwell_progress
        self.hovered_keys   = {
            fid: self.get_key_at(lx, ly)
            for fid, (lx, ly) in self.fingertip_positions.items()
        }

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        font = QFont('Segoe UI', max(8, self.key_h // 4))
        painter.setFont(font)

        for rect, label in self.key_rects:
            self._draw_key(painter, rect, label)

        # Fingertip dots — always fully opaque
        for fid, (lx, ly) in self.fingertip_positions.items():
            painter.setBrush(QBrush(QColor(0, 220, 180, 230)))
            painter.setPen(QPen(QColor(255, 255, 255, 180), 2))
            painter.drawEllipse(int(lx) - 10, int(ly) - 10, 20, 20)

        painter.end()

    def _draw_key(self, painter, rect, label):
        is_hovered = label in self.hovered_keys.values()

        # Dwell progress for this key
        progress = 0.0
        for fid, (key_label, prog) in self.dwell_progress.items():
            if key_label == label:
                progress = prog
                break

        # Key background — opacity controlled
        bg_alpha = int(self.opacity * 255)
        if is_hovered:
            bg_color = QColor(255, 255, 255, min(255, bg_alpha * 4))
        else:
            bg_color = QColor(30, 30, 30, max(60, bg_alpha * 3))

        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        painter.drawRoundedRect(rect, 6, 6)

        # Dwell fill — cyan from left
        if progress > 0:
            fill_w    = int(rect.width() * progress)
            fill_rect = QRect(rect.x(), rect.y(), fill_w, rect.height())
            painter.setBrush(QBrush(QColor(0, 220, 180, 160)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(fill_rect, 6, 6)

        # Key label — ALWAYS fully opaque regardless of opacity setting
        if progress > 0.5:
            text_color = QColor(0, 0, 0, 255)
        elif is_hovered:
            text_color = QColor(0, 220, 180, 255)
        else:
            text_color = QColor(255, 255, 255, 255)

        painter.setPen(QPen(text_color))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, label)