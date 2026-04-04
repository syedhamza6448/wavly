from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient

# Hand landmark connections
CONNECTIONS = [
    (0, 1),  (1, 2),   (2, 3),   (3, 4),
    (0, 5),  (5, 6),   (6, 7),   (7, 8),
    (0, 9),  (9, 10),  (10, 11), (11, 12),
    (0, 13), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20),
    (5, 9),  (9, 13),  (13, 17)
]

# Fingertip landmark indices
FINGERTIPS = [4, 8, 12, 16, 20]

ACCENT = "#00dcdc"
SUCCESS = "#00dc8a"


class HandOverlay(QWidget):
    """
    A full-screen transparent overlay that draws
    hand skeleton outlines with very low opacity.
    No camera feed — just the hand structure.
    """
    def __init__(self, screen_w, screen_h):
        super().__init__()
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.cam_w    = 640
        self.cam_h    = 480

        # hands: list of {landmarks, label}
        self._hands   = []
        self._visible = True
        self._opacity = 0.15  # very low by default

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setGeometry(0, 0, screen_w, screen_h)

        # Repaint at 30fps
        self._timer = QTimer()
        self._timer.timeout.connect(self.update)
        self._timer.start(33)

    def set_hands(self, hands):
        """Called every frame from main loop."""
        self._hands = hands

    def set_visible_overlay(self, visible):
        """Show or hide the hand outline."""
        self._visible = visible
        self.update()

    def set_opacity_level(self, opacity):
        """0.0 - 1.0"""
        self._opacity = opacity
        self.update()

    def _to_screen(self, lm):
        """Converts landmark camera coords to screen coords."""
        sx = int(lm['x'] / self.cam_w * self.screen_w)
        sy = int(lm['y'] / self.cam_h * self.screen_h)
        return sx, sy

    def paintEvent(self, event):
        if not self._visible or not self._hands:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for hand in self._hands:
            landmarks = hand['landmarks']
            label     = hand['label']

            # Color per hand
            color_str = ACCENT if label == 'Right' else SUCCESS
            color     = QColor(color_str)

            # ── Draw connections ──
            line_alpha = int(self._opacity * 180)
            line_color = QColor(color)
            line_color.setAlpha(line_alpha)
            pen = QPen(line_color, 2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            for start_idx, end_idx in CONNECTIONS:
                if start_idx < len(landmarks) and end_idx < len(landmarks):
                    sx, sy = self._to_screen(landmarks[start_idx])
                    ex, ey = self._to_screen(landmarks[end_idx])
                    painter.drawLine(sx, sy, ex, ey)

            # ── Draw joint dots ──
            joint_alpha = int(self._opacity * 200)
            joint_color = QColor(color)
            joint_color.setAlpha(joint_alpha)

            for i, lm in enumerate(landmarks):
                sx, sy = self._to_screen(lm)

                if i in FINGERTIPS:
                    # Fingertips — slightly larger with glow
                    glow = QColor(color)
                    glow.setAlpha(int(self._opacity * 80))
                    painter.setBrush(QBrush(glow))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(sx - 8, sy - 8, 16, 16)

                    painter.setBrush(QBrush(joint_color))
                    painter.drawEllipse(sx - 5, sy - 5, 10, 10)
                else:
                    # Regular joints
                    painter.setBrush(QBrush(joint_color))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(sx - 3, sy - 3, 6, 6)

        painter.end()