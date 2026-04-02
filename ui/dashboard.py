from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPen

BG_PRIMARY = "#0d0d0d"
BG_SECONDARY = "#161616"
BG_CARD = "#1e1e1e"
ACCENT = "#00dcdc"
ACCENT_DIM = "#007a7a"
TEXT_PRIMARY = "#f0f0f0"
TEXT_MUTED = "#888888"
BORDER = "#2a2a2a"
SUCCESS = "#00dc8a"
DANGER = "#ff4f4f"
WARNING = "#f0a500"

STYLESHEET = f"""
    QWidget {{
        background-color: {BG_PRIMARY};
        color: {TEXT_PRIMARY};
        font-family: 'Segoe UI';
        font-size: 13px;
    }}
    QPushButton {{
        background-color: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 8px 16px;
    }}
    QPushButton:hover {{
        border-color: {ACCENT};
        color: {ACCENT};
    }}
    QPushButton#accent_btn {{
        background-color: {ACCENT};
        color: {BG_PRIMARY};
        border: none;
        font-weight: 600;
    }}
    QPushButton#accent_btn:hover {{
        background-color: {ACCENT_DIM};
    }}
    QFrame#card {{
        background-color: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 10px;
    }}
"""

class StatusDot(QWidget):
    """A simple colored circle indicating status."""
    def __init__(self, color=SUCCESS, size=12):
        super().__init__()
        self._color = color
        self._size = size
        self.setFixedSize(size, size)
        
    def set_color(self, color):
        self._color = color
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(self._color)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, self._size, self._size)
        painter.end()
        
def make_card():
    card = QFrame()
    card.setObjectName("card")
    layout = QVBoxLayout(card)
    layout.setContentsMargins(16, 14, 16, 14)
    layout.setSpacing(10)
    return card

class DashboardWindow(QWidget):
    open_settings = pyqtSignal()
    toggle_tracking = pyqtSignal()
    toggle_debug = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wavly")
        self.setFixedSize(380, 420)
        self.setStyleSheet(STYLESHEET)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint
        )
        
        self._tracking = True
        self._hands = 0
        self._last_gesture = "None"
        self._fps = 0
        self._debug = False
        
        self._build_ui()
        
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        
        header = QWidget()
        header.setStyleSheet(
            f"background-color: {BG_SECONDARY};"
            f"border-bottom: 1px solid {BORDER};"
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 16)
        
        title = QLabel("Wavly")
        title.setStyleSheet(
            f"font-size: 20px; font-weight: 700; color: {ACCENT};"
        )
        subtitle = QLabel("Gesture Control")
        subtitle.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        
        header_layout.addLayout(title_col)
        header_layout.addStretch()
        
        root.addWidget(header)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(12)
        
        status_card = make_card()
        
        tracking_row = QHBoxLayout()
        tracking_label = QLabel("Tracking")
        tracking_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        self.tracking_dot = StatusDot(SUCCESS)   
        self.tracking_status = QLabel("Active")
        self.tracking_status.setStyleSheet(f"color: {SUCCESS}; font-weight: 600;")
        
        tracking_row.addWidget(tracking_label)
        tracking_row.addStretch()
        tracking_row.addWidget(self.tracking_dot)
        tracking_row.addSpacing(6)
        tracking_row.addWidget(self.tracking_status)
        
        hands_row = QHBoxLayout()
        hands_label = QLabel("Hands detected")
        hands_label. setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        self.hands_value = QLabel("0")
        self.hands_value.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-weight: 600;"
        )
        
        hands_row.addWidget(hands_label)
        hands_row.addStretch()
        hands_row.addWidget(self.hands_value)
        
        fps_row = QHBoxLayout()
        fps_label = QLabel("FPS")
        fps_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        self.fps_value = QLabel("0")
        self.fps_value.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-weight: 600;"
        )
        
        fps_row.addWidget(fps_label)
        fps_row.addStretch()
        fps_row.addWidget(self.fps_value)
        
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(
            f"color: {BORDER}; background: {BORDER}; max-height: 1px;"
        )
        
         # Last gesture row
        gesture_row = QHBoxLayout()
        gesture_label = QLabel("Last gesture")
        gesture_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        self.gesture_value = QLabel("None")
        self.gesture_value.setStyleSheet(
            f"color: {ACCENT}; font-weight: 600;"
        )

        gesture_row.addWidget(gesture_label)
        gesture_row.addStretch()
        gesture_row.addWidget(self.gesture_value)

        status_card.layout().addLayout(tracking_row)
        status_card.layout().addLayout(hands_row)
        status_card.layout().addLayout(fps_row)
        status_card.layout().addWidget(divider)
        status_card.layout().addLayout(gesture_row)

        content_layout.addWidget(status_card)

        # ── Buttons ──
        self.pause_btn = QPushButton("Pause Tracking")
        self.pause_btn.setObjectName("accent_btn")
        self.pause_btn.clicked.connect(self._on_toggle_tracking)

        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.open_settings.emit)

        self.debug_btn = QPushButton("Show Camera Feed  (debug)")
        self.debug_btn.clicked.connect(self._on_toggle_debug)

        content_layout.addWidget(self.pause_btn)
        content_layout.addWidget(settings_btn)
        content_layout.addWidget(self.debug_btn)
        content_layout.addStretch()

        # Version label
        version = QLabel("Wavly v1.0  —  IT Vision Project")
        version.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(version)

        root.addWidget(content)

    # ─────────────────────────────────────────
    # PUBLIC UPDATE METHODS
    # ─────────────────────────────────────────

    def update_status(self, tracking, hands, last_gesture, fps):
        """Called every frame from main loop to refresh displayed values."""
        self._tracking = tracking
        self._hands = hands
        self._last_gesture = last_gesture
        self._fps = fps

        if tracking:
            self.tracking_dot.set_color(SUCCESS)
            self.tracking_status.setText("Active")
            self.tracking_status.setStyleSheet(
                f"color: {SUCCESS}; font-weight: 600;"
            )
            self.pause_btn.setText("Pause Tracking")
        else:
            self.tracking_dot.set_color(DANGER)
            self.tracking_status.setText("Paused")
            self.tracking_status.setStyleSheet(
                f"color: {DANGER}; font-weight: 600;"
            )
            self.pause_btn.setText("Resume Tracking")

        self.hands_value.setText(str(hands))
        self.gesture_value.setText(last_gesture or "None")
        self.fps_value.setText(str(fps))

    def _on_toggle_tracking(self):
        self.toggle_tracking.emit()

    def _on_toggle_debug(self):
        self._debug = not self._debug
        self.debug_btn.setText(
            "Hide Camera Feed  (debug)" if self._debug
            else "Show Camera Feed  (debug)"
        )
        self.toggle_debug.emit()