from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont
from ui.fonts import FONT_DISPLAY, FONT_BODY

BG_PRIMARY    = "#080c0c"
BG_SECONDARY  = "#0d1515"
BG_CARD       = "#111d1d"
BG_CARD2      = "#0f1a1a"
ACCENT        = "#00dcdc"
ACCENT_DIM    = "#007a7a"
ACCENT_GLOW   = "#00dcdc22"
TEXT_PRIMARY  = "#e8f4f4"
TEXT_MUTED    = "#4a7070"
TEXT_DIM      = "#2a5050"
BORDER        = "#0d2a2a"
BORDER_ACCENT = "#00dcdc33"
SUCCESS       = "#00dc8a"
DANGER        = "#ff4f6a"
WARNING       = "#f0a500"

STYLESHEET = f"""
    QWidget {{
        background-color: {BG_PRIMARY};
        color: {TEXT_PRIMARY};
        font-family: '{FONT_BODY}';
        font-size: 13px;
        border: none;
        outline: none;
    }}
    QWidget#root {{
        background-color: {BG_PRIMARY};
    }}
    QPushButton {{
        background-color: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 13px;
        font-family: '{FONT_BODY}';
        text-align: left;
    }}
    QPushButton:hover {{
        border-color: {ACCENT};
        color: {ACCENT};
        background-color: {ACCENT_GLOW};
    }}
    QPushButton:pressed {{
        background-color: {ACCENT_DIM};
        color: {BG_PRIMARY};
    }}
    QPushButton#primary_btn {{
        background-color: {ACCENT};
        color: {BG_PRIMARY};
        border: none;
        font-weight: 700;
        text-align: center;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 14px;
        font-family: '{FONT_BODY}';
    }}
    QPushButton#primary_btn:hover {{
        background-color: #00f0f0;
    }}
    QPushButton#danger_btn {{
        background-color: transparent;
        color: {DANGER};
        border: 1px solid {DANGER}44;
        text-align: center;
        font-family: '{FONT_BODY}';
    }}
    QPushButton#danger_btn:hover {{
        background-color: {DANGER}22;
        border-color: {DANGER};
    }}
    QPushButton#ghost_btn {{
        background-color: transparent;
        color: {TEXT_MUTED};
        border: 1px solid {BORDER};
        text-align: center;
        font-size: 12px;
        padding: 8px 16px;
        font-family: '{FONT_BODY}';
    }}
    QPushButton#ghost_btn:hover {{
        color: {ACCENT};
        border-color: {ACCENT}44;
    }}
    QFrame#card {{
        background-color: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
    }}
    QFrame#accent_card {{
        background-color: {BG_CARD2};
        border: 1px solid {BORDER_ACCENT};
        border-radius: 12px;
    }}
    QFrame#divider {{
        background-color: {BORDER};
        max-height: 1px;
        border: none;
    }}
    QLabel#heading {{
        font-size: 28px;
        font-weight: 700;
        color: {ACCENT};
        font-family: '{FONT_DISPLAY}';
        letter-spacing: 2px;
    }}
    QLabel#subheading {{
        font-size: 10px;
        color: {TEXT_MUTED};
        font-family: '{FONT_BODY}';
        letter-spacing: 3px;
    }}
    QLabel#stat_value {{
        font-size: 32px;
        font-weight: 700;
        color: {TEXT_PRIMARY};
        font-family: '{FONT_DISPLAY}';
    }}
    QLabel#stat_label {{
        font-size: 10px;
        color: {TEXT_MUTED};
        letter-spacing: 2px;
        font-family: '{FONT_BODY}';
    }}
    QLabel#gesture_value {{
        font-size: 16px;
        font-weight: 600;
        color: {ACCENT};
        font-family: '{FONT_BODY}';
    }}
    QLabel#muted {{
        color: {TEXT_MUTED};
        font-size: 12px;
        font-family: '{FONT_BODY}';
    }}
    QLabel#version {{
        color: {TEXT_DIM};
        font-size: 10px;
        letter-spacing: 2px;
        font-family: '{FONT_BODY}';
    }}
    QLabel#nav_btn_label {{
        color: {TEXT_MUTED};
        font-size: 12px;
        font-family: '{FONT_BODY}';
        padding: 10px 12px;
        border-radius: 8px;
    }}
"""


class PulsingDot(QWidget):
    def __init__(self, color=SUCCESS, size=10):
        super().__init__()
        self._color  = color
        self._size   = size
        self._pulse  = 0.0
        self._active = True
        self._step   = 0
        self.setFixedSize(size + 10, size + 10)

        self._timer = QTimer()
        self._timer.timeout.connect(self._animate)
        self._timer.start(50)

    def set_color(self, color, active=True):
        self._color  = color
        self._active = active
        self.update()

    def _animate(self):
        if self._active:
            self._step  = (self._step + 1) % 40
            self._pulse = abs(20 - self._step) / 20.0
        else:
            self._pulse = 0.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx = self.width()  // 2
        cy = self.height() // 2

        if self._active and self._pulse > 0:
            ring_size  = int(self._size * (1 + self._pulse * 0.8))
            c          = QColor(self._color)
            c.setAlpha(int(self._pulse * 60))
            painter.setPen(QPen(c, 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(
                cx - ring_size // 2, cy - ring_size // 2,
                ring_size, ring_size
            )

        painter.setBrush(QBrush(QColor(self._color)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            cx - self._size // 2, cy - self._size // 2,
            self._size, self._size
        )
        painter.end()


def make_card(accent=False):
    card = QFrame()
    card.setObjectName("accent_card" if accent else "card")
    layout = QVBoxLayout(card)
    layout.setContentsMargins(20, 18, 20, 18)
    layout.setSpacing(10)
    return card


def make_divider():
    d = QFrame()
    d.setObjectName("divider")
    d.setFixedHeight(1)
    return d


class DashboardWindow(QWidget):
    open_settings   = pyqtSignal()
    toggle_tracking = pyqtSignal()
    toggle_debug    = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wavly")
        self.setMinimumSize(960, 600)
        self.setStyleSheet(STYLESHEET)
        self.setObjectName("root")
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint
        )

        self._tracking     = True
        self._hands        = 0
        self._last_gesture = "None"
        self._fps          = 0
        self._debug        = False

        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ──
        sidebar = QWidget()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(
            f"background-color: {BG_SECONDARY};"
            f"border-right: 1px solid {BORDER};"
        )
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(20, 36, 20, 24)
        sb_layout.setSpacing(0)

        # Logo
        logo = QLabel("WAVLY")
        logo.setObjectName("heading")
        tagline = QLabel("GESTURE CONTROL SYSTEM")
        tagline.setObjectName("subheading")

        sb_layout.addWidget(logo)
        sb_layout.addSpacing(6)
        sb_layout.addWidget(tagline)
        sb_layout.addSpacing(48)

        # Nav items
        def nav_btn(icon, text, slot):
            btn = QPushButton(f"  {icon}   {text}")
            btn.setFixedHeight(44)
            btn.clicked.connect(slot)
            return btn

        self.settings_btn = nav_btn("⚙", "Settings", self.open_settings.emit)
        self.debug_btn    = nav_btn("◉", "Debug Feed", self._on_toggle_debug)

        sb_layout.addWidget(self.settings_btn)
        sb_layout.addSpacing(8)
        sb_layout.addWidget(self.debug_btn)
        sb_layout.addStretch()

        # Pause btn
        self.pause_btn = QPushButton("Pause Tracking")
        self.pause_btn.setObjectName("danger_btn")
        self.pause_btn.setFixedHeight(44)
        self.pause_btn.clicked.connect(self._on_toggle_tracking)
        sb_layout.addWidget(self.pause_btn)
        sb_layout.addSpacing(16)

        version = QLabel("WAVLY  ·  IT VISION  ·  V1.0")
        version.setObjectName("version")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sb_layout.addWidget(version)

        root.addWidget(sidebar)

        # ── Main content ──
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(36, 36, 36, 36)
        cl.setSpacing(20)

        # Top stat row
        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        # Status card
        status_card = make_card(accent=True)
        status_card.setFixedHeight(150)
        status_card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        s_top = QHBoxLayout()
        s_title = QLabel("TRACKING STATUS")
        s_title.setObjectName("stat_label")
        self.status_dot = PulsingDot(SUCCESS, size=10)
        s_top.addWidget(s_title)
        s_top.addStretch()
        s_top.addWidget(self.status_dot)

        self.status_value = QLabel("Active")
        self.status_value.setStyleSheet(
            f"font-size: 28px; font-weight: 700;"
            f"color: {SUCCESS}; font-family: '{FONT_DISPLAY}';"
        )
        self.status_sub = QLabel("Gesture tracking is running")
        self.status_sub.setObjectName("muted")

        status_card.layout().addLayout(s_top)
        status_card.layout().addWidget(self.status_value)
        status_card.layout().addWidget(self.status_sub)
        status_card.layout().addStretch()
        top_row.addWidget(status_card, 3)

        # Hands card
        hands_card = make_card()
        hands_card.setFixedHeight(150)
        hands_card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        h_title = QLabel("HANDS")
        h_title.setObjectName("stat_label")
        self.hands_value = QLabel("0")
        self.hands_value.setObjectName("stat_value")
        h_sub = QLabel("detected")
        h_sub.setObjectName("muted")
        hands_card.layout().addWidget(h_title)
        hands_card.layout().addWidget(self.hands_value)
        hands_card.layout().addWidget(h_sub)
        hands_card.layout().addStretch()
        top_row.addWidget(hands_card, 1)

        # FPS card
        fps_card = make_card()
        fps_card.setFixedHeight(150)
        fps_card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        f_title = QLabel("FPS")
        f_title.setObjectName("stat_label")
        self.fps_value = QLabel("0")
        self.fps_value.setObjectName("stat_value")
        f_sub = QLabel("frames / sec")
        f_sub.setObjectName("muted")
        fps_card.layout().addWidget(f_title)
        fps_card.layout().addWidget(self.fps_value)
        fps_card.layout().addWidget(f_sub)
        fps_card.layout().addStretch()
        top_row.addWidget(fps_card, 1)

        cl.addLayout(top_row)

        # Last gesture card
        gesture_card = make_card(accent=True)
        gesture_card.setFixedHeight(90)
        g_top = QHBoxLayout()
        g_title = QLabel("LAST GESTURE")
        g_title.setObjectName("stat_label")
        g_top.addWidget(g_title)
        g_top.addStretch()
        self.gesture_value = QLabel("None")
        self.gesture_value.setObjectName("gesture_value")
        gesture_card.layout().addLayout(g_top)
        gesture_card.layout().addWidget(self.gesture_value)
        gesture_card.layout().addStretch()
        cl.addWidget(gesture_card)

        # Gesture reference grid
        ref_card = make_card()
        ref_top = QLabel("GESTURE REFERENCE")
        ref_top.setObjectName("stat_label")
        ref_card.layout().addWidget(ref_top)
        ref_card.layout().addWidget(make_divider())

        gestures = [
            ("Index finger",   "Move cursor",         ACCENT),
            ("Pinch",          "Left click",          SUCCESS),
            ("Pinch + hold",   "Drag",                SUCCESS),
            ("Double pinch",   "Double click",        SUCCESS),
            ("Thumb + middle", "Right click",         WARNING),
            ("Two fingers",    "Scroll up / down",    ACCENT),
            ("Four fingers",   "Alt+Tab",             ACCENT),
            ("Index held 1s",  "Press Enter",         TEXT_MUTED),
            ("Three fingers",  "Toggle keyboard",     WARNING),
            ("Fist",           "Freeze cursor",       DANGER),
            ("Open palm",      "Pause tracking",      DANGER),
            ("Pinky only",     "Toggle guide",        TEXT_MUTED),
        ]

        grid_widget  = QWidget()
        grid_layout  = QHBoxLayout(grid_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(12)

        col_count = 3
        per_col   = (len(gestures) + col_count - 1) // col_count

        for col_i in range(col_count):
            col_w  = QWidget()
            col_l  = QVBoxLayout(col_w)
            col_l.setContentsMargins(0, 0, 0, 0)
            col_l.setSpacing(5)

            start = col_i * per_col
            end   = min(start + per_col, len(gestures))

            for gesture, action, color in gestures[start:end]:
                row = QWidget()
                row.setStyleSheet(
                    f"background: {BG_SECONDARY}; border-radius: 6px;"
                )
                rl = QHBoxLayout(row)
                rl.setContentsMargins(10, 7, 10, 7)
                rl.setSpacing(10)

                dot = QLabel("●")
                dot.setStyleSheet(
                    f"color: {color}; font-size: 8px;"
                    f"background: transparent;"
                )
                dot.setFixedWidth(12)

                g_lbl = QLabel(gesture)
                g_lbl.setStyleSheet(
                    f"color: {TEXT_PRIMARY}; font-size: 12px;"
                    f"font-family: '{FONT_BODY}'; background: transparent;"
                )

                a_lbl = QLabel(action)
                a_lbl.setStyleSheet(
                    f"color: {TEXT_MUTED}; font-size: 12px;"
                    f"font-family: '{FONT_BODY}'; background: transparent;"
                )
                a_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)

                rl.addWidget(dot)
                rl.addWidget(g_lbl)
                rl.addStretch()
                rl.addWidget(a_lbl)
                col_l.addWidget(row)

            col_l.addStretch()
            grid_layout.addWidget(col_w)

        ref_card.layout().addWidget(grid_widget)
        cl.addWidget(ref_card, 1)

        root.addWidget(content)

    def update_status(self, tracking, hands, last_gesture, fps):
        self._tracking     = tracking
        self._hands        = hands
        self._last_gesture = last_gesture
        self._fps          = fps

        if tracking:
            self.status_dot.set_color(SUCCESS, active=True)
            self.status_value.setText("Active")
            self.status_value.setStyleSheet(
                f"font-size: 28px; font-weight: 700;"
                f"color: {SUCCESS}; font-family: '{FONT_DISPLAY}';"
            )
            self.status_sub.setText("Gesture tracking is running")
            self.pause_btn.setText("Pause Tracking")
            self.pause_btn.setObjectName("danger_btn")
        else:
            self.status_dot.set_color(DANGER, active=False)
            self.status_value.setText("Paused")
            self.status_value.setStyleSheet(
                f"font-size: 28px; font-weight: 700;"
                f"color: {DANGER}; font-family: '{FONT_DISPLAY}';"
            )
            self.status_sub.setText("Open palm gesture to resume")
            self.pause_btn.setText("Resume Tracking")
            self.pause_btn.setObjectName("primary_btn")

        self.pause_btn.style().unpolish(self.pause_btn)
        self.pause_btn.style().polish(self.pause_btn)
        self.hands_value.setText(str(hands))
        self.fps_value.setText(str(fps))
        self.gesture_value.setText(last_gesture or "None")

    def _on_toggle_tracking(self):
        self.toggle_tracking.emit()

    def _on_toggle_debug(self):
        self._debug = not self._debug
        self.debug_btn.setText(
            "  ◉   Hide Camera Feed" if self._debug
            else "  ◉   Camera Feed"
        )
        self.toggle_debug.emit()