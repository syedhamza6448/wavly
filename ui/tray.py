from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen
from PyQt6.QtCore import Qt, pyqtSignal, QObject


def generate_tray_icon():
    """
    Generates a simple circular cyan icon programmatically.
    Replace with a real .ico file in assets/ later if needed.
    """
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Outer circle — cyan
    painter.setBrush(QBrush(QColor("#00dcdc")))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(4, 4, 56, 56)

    # Inner circle — dark
    painter.setBrush(QBrush(QColor("#0d0d0d")))
    painter.drawEllipse(16, 16, 32, 32)

    # Center dot — cyan
    painter.setBrush(QBrush(QColor("#00dcdc")))
    painter.drawEllipse(26, 26, 12, 12)

    painter.end()

    return QIcon(pixmap)


class TrayIcon(QObject):
    # Signals emitted to main loop
    open_settings = pyqtSignal()
    toggle_tracking = pyqtSignal()
    toggle_keyboard = pyqtSignal()
    quit_app = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.icon = QSystemTrayIcon()
        self.icon.setIcon(generate_tray_icon())
        self.icon.setToolTip("Wavly — Gesture Control")

        self._tracking_paused = False
        self._keyboard_visible = False

        self._build_menu()

        # Single click on tray icon opens settings
        self.icon.activated.connect(self._on_activated)

        self.icon.show()

    def _build_menu(self):
        self.menu = QMenu()
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e1e;
                color: #f0f0f0;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
                padding: 4px;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #252525;
                color: #00dcdc;
            }
            QMenu::separator {
                height: 1px;
                background: #2a2a2a;
                margin: 4px 8px;
            }
        """)

        # App name header — not clickable
        self.header_action = self.menu.addAction("Wavly")
        self.header_action.setEnabled(False)
        self.menu.addSeparator()

        # Tracking toggle
        self.tracking_action = self.menu.addAction("Pause Tracking")
        self.tracking_action.triggered.connect(self._on_toggle_tracking)

        # Keyboard toggle
        self.keyboard_action = self.menu.addAction("Show Keyboard")
        self.keyboard_action.triggered.connect(self._on_toggle_keyboard)

        self.menu.addSeparator()

        # Settings
        settings_action = self.menu.addAction("Settings  (S)")
        settings_action.triggered.connect(self.open_settings.emit)

        self.menu.addSeparator()

        # Quit
        quit_action = self.menu.addAction("Quit Wavly")
        quit_action.triggered.connect(self.quit_app.emit)

        self.icon.setContextMenu(self.menu)

    def _on_activated(self, reason):
        """Single click on tray icon opens settings."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.open_settings.emit()

    def _on_toggle_tracking(self):
        self._tracking_paused = not self._tracking_paused
        self.tracking_action.setText(
            "Resume Tracking" if self._tracking_paused else "Pause Tracking"
        )
        self.toggle_tracking.emit()

    def _on_toggle_keyboard(self):
        self._keyboard_visible = not self._keyboard_visible
        self.keyboard_action.setText(
            "Hide Keyboard" if self._keyboard_visible else "Show Keyboard"
        )
        self.toggle_keyboard.emit()

    def update_tracking_state(self, paused):
        """Called from main loop to keep tray menu in sync."""
        self._tracking_paused = paused
        self.tracking_action.setText(
            "Resume Tracking" if paused else "Pause Tracking"
        )

    def update_keyboard_state(self, visible):
        """Called from main loop to keep tray menu in sync."""
        self._keyboard_visible = visible
        self.keyboard_action.setText(
            "Hide Keyboard" if visible else "Show Keyboard"
        )

    def show_notification(self, title, message, duration=2000):
        """Shows a Windows tray notification bubble."""
        self.icon.showMessage(
            title, message,
            QSystemTrayIcon.MessageIcon.Information,
            duration
        )

    def hide(self):
        self.icon.hide()