from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation,
    QEasingCurve, QRect, pyqtSignal
)
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont
import pyautogui
import pynput.keyboard as kb
from ui.fonts import FONT_DISPLAY, FONT_BODY

BG        = "#0d1515"
ACCENT    = "#00dcdc"
ACCENT_DIM= "#007a7a"
BORDER    = "#0d2a2a"
TEXT      = "#e8f4f4"
TEXT_MUTED= "#4a7070"
HOVER_BG  = "#00dcdc15"

STYLESHEET = f"""
    QWidget {{
        background-color: {BG};
        border: none;
        font-family: '{FONT_BODY}';
    }}
    QWidget#toolbar_root {{
        background-color: {BG};
        border-left: 1px solid {BORDER};
        border-top: 1px solid {BORDER};
        border-bottom: 1px solid {BORDER};
        border-top-left-radius: 16px;
        border-bottom-left-radius: 16px;
    }}
    QPushButton#tool_btn {{
        background-color: transparent;
        color: {TEXT};
        border: none;
        border-radius: 10px;
        font-size: 18px;
        font-family: '{FONT_BODY}';
        padding: 0px;
    }}
    QPushButton#tool_btn:hover {{
        background-color: {HOVER_BG};
        color: {ACCENT};
    }}
    QPushButton#tool_btn:pressed {{
        background-color: {ACCENT_DIM};
        color: #000;
    }}
"""

# Toolbar buttons — (emoji, tooltip, action_name)
TOOLS = [
    ("📷", "Screenshot",    "screenshot"),
    ("🔇", "Mute / Unmute", "mute"),
    ("🔊", "Volume Up",     "vol_up"),
    ("🔉", "Volume Down",   "vol_down"),
    ("⏮",  "Previous",      "media_prev"),
    ("⏯",  "Play / Pause",  "media_play"),
    ("⏭",  "Next",          "media_next"),
]


class ToolButton(QPushButton):
    def __init__(self, emoji, tooltip, action_name, callback):
        super().__init__(emoji)
        self.setObjectName("tool_btn")
        self.setToolTip(tooltip)
        self.setFixedSize(48, 48)
        self.action_name = action_name
        self.clicked.connect(lambda: callback(action_name))


class SlideToolbar(QWidget):
    """
    A hidden toolbar that slides in from the right edge on hover.
    Sits always on top, spanning the vertical center of the screen.
    """
    action_triggered = pyqtSignal(str)

    def __init__(self, screen_w, screen_h):
        super().__init__()
        self.screen_w  = screen_w
        self.screen_h  = screen_h

        self.btn_size  = 48
        self.padding   = 12
        self.gap       = 6
        self.tab_w     = 18   # visible tab width when hidden
        self.panel_w   = self.btn_size + self.padding * 2 + self.tab_w

        total_h = (
            len(TOOLS) * (self.btn_size + self.gap)
            - self.gap
            + self.padding * 2
        )
        self.panel_h = total_h

        # Position center-right
        self.pos_y = (screen_h - self.panel_h) // 2

        # Start fully hidden (only tab visible)
        self._expanded = False
        self._hovered  = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setMouseTracking(True)
        self.setStyleSheet(STYLESHEET)

        # Geometry — hidden: only tab_w visible on right edge
        self._hidden_x   = screen_w - self.tab_w
        self._visible_x  = screen_w - self.panel_w
        self.setGeometry(
            self._hidden_x, self.pos_y,
            self.panel_w, self.panel_h
        )

        self._build_ui()
        self._setup_animation()

        # Hover check timer
        self._hover_timer = QTimer()
        self._hover_timer.timeout.connect(self._check_hover)
        self._hover_timer.start(50)

        self._keyboard = kb.Controller()

    def _build_ui(self):
        root = QWidget(self)
        root.setObjectName("toolbar_root")
        root.setGeometry(
            self.tab_w, 0,
            self.panel_w - self.tab_w,
            self.panel_h
        )

        layout = QVBoxLayout(root)
        layout.setContentsMargins(
            self.padding, self.padding,
            self.padding, self.padding
        )
        layout.setSpacing(self.gap)

        for emoji, tooltip, action in TOOLS:
            btn = ToolButton(emoji, tooltip, action, self._on_action)
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

    def _setup_animation(self):
        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _slide_in(self):
        if self._expanded:
            return
        self._expanded = True
        start = QRect(
            self._hidden_x, self.pos_y,
            self.panel_w, self.panel_h
        )
        end = QRect(
            self._visible_x, self.pos_y,
            self.panel_w, self.panel_h
        )
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.start()

    def _slide_out(self):
        if not self._expanded:
            return
        self._expanded = False
        start = QRect(
            self._visible_x, self.pos_y,
            self.panel_w, self.panel_h
        )
        end = QRect(
            self._hidden_x, self.pos_y,
            self.panel_w, self.panel_h
        )
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.start()

    def _check_hover(self):
        from PyQt6.QtGui import QCursor
        cursor = QCursor.pos()
        cx, cy = cursor.x(), cursor.y()

        # Trigger zone — rightmost 24px of screen, centered vertically
        in_trigger = (
            cx >= self.screen_w - 24 and
            self.pos_y <= cy <= self.pos_y + self.panel_h
        )

        # Also keep open if cursor is over the panel itself
        in_panel = (
            self._visible_x <= cx <= self.screen_w and
            self.pos_y <= cy <= self.pos_y + self.panel_h
        ) if self._expanded else False

        if in_trigger or in_panel:
            self._slide_in()
        else:
            self._slide_out()

    def paintEvent(self, event):
        """Draw the visible tab on the left edge of the widget."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Tab background
        tab_color = QColor(ACCENT) if self._expanded else QColor("#0d2a2a")
        painter.setBrush(QBrush(tab_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(
            0, self.panel_h // 2 - 30,
            self.tab_w, 60, 4, 4
        )

        # Tab arrow indicator
        arrow_color = QColor("#000") if self._expanded else QColor(ACCENT)
        painter.setPen(QPen(arrow_color, 2))
        cx = self.tab_w // 2
        cy = self.panel_h // 2
        if self._expanded:
            # Arrow pointing right (close)
            painter.drawLine(cx - 3, cy - 5, cx + 3, cy)
            painter.drawLine(cx + 3, cy, cx - 3, cy + 5)
        else:
            # Arrow pointing left (open)
            painter.drawLine(cx + 3, cy - 5, cx - 3, cy)
            painter.drawLine(cx - 3, cy, cx + 3, cy + 5)

        painter.end()

    def _on_action(self, action_name):
        """Execute the toolbar action."""
        if action_name == "screenshot":
            import datetime, os
            ts       = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path     = os.path.join(
                os.path.expanduser("~"), "Pictures",
                f"Wavly_Screenshot_{ts}.png"
            )
            screenshot = pyautogui.screenshot()
            screenshot.save(path)
            print(f"Screenshot saved: {path}")

        elif action_name == "mute":
            pyautogui.press("volumemute")

        elif action_name == "vol_up":
            for _ in range(3):
                pyautogui.press("volumeup")

        elif action_name == "vol_down":
            for _ in range(3):
                pyautogui.press("volumedown")

        elif action_name == "media_prev":
            pyautogui.press("prevtrack")

        elif action_name == "media_play":
            pyautogui.press("playpause")

        elif action_name == "media_next":
            pyautogui.press("nexttrack")

        self.action_triggered.emit(action_name)