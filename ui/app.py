from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QComboBox, QScrollArea,
    QFrame, QGridLayout, QSpinBox, QCheckBox,
    QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon

# ─────────────────────────────────────────
# STYLE CONSTANTS
# ─────────────────────────────────────────

BG_PRIMARY   = "#0d0d0d"
BG_SECONDARY = "#161616"
BG_CARD      = "#1e1e1e"
BG_INPUT     = "#252525"
ACCENT       = "#00dcdc"
ACCENT_DIM   = "#007a7a"
TEXT_PRIMARY = "#f0f0f0"
TEXT_MUTED   = "#888888"
BORDER       = "#2a2a2a"
DANGER       = "#ff4f4f"
SUCCESS      = "#00dc8a"

STYLESHEET = f"""
    QWidget {{
        background-color: {BG_PRIMARY};
        color: {TEXT_PRIMARY};
        font-family: 'Segoe UI';
        font-size: 13px;
    }}
    QScrollArea {{
        border: none;
        background-color: {BG_PRIMARY};
    }}
    QScrollBar:vertical {{
        background: {BG_SECONDARY};
        width: 6px;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical {{
        background: {ACCENT_DIM};
        border-radius: 3px;
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QPushButton {{
        background-color: {BG_INPUT};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 13px;
    }}
    QPushButton:hover {{
        border-color: {ACCENT};
        color: {ACCENT};
    }}
    QPushButton:pressed {{
        background-color: {ACCENT_DIM};
        color: {BG_PRIMARY};
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
    QPushButton#danger_btn {{
        background-color: transparent;
        color: {DANGER};
        border: 1px solid {DANGER};
    }}
    QPushButton#danger_btn:hover {{
        background-color: {DANGER};
        color: {BG_PRIMARY};
    }}
    QSlider::groove:horizontal {{
        background: {BG_INPUT};
        height: 4px;
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {ACCENT};
        width: 14px;
        height: 14px;
        margin: -5px 0;
        border-radius: 7px;
    }}
    QSlider::sub-page:horizontal {{
        background: {ACCENT};
        border-radius: 2px;
    }}
    QComboBox {{
        background-color: {BG_INPUT};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px 12px;
        min-width: 120px;
    }}
    QComboBox:hover {{
        border-color: {ACCENT};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        selection-background-color: {ACCENT_DIM};
    }}
    QCheckBox {{
        spacing: 8px;
        color: {TEXT_PRIMARY};
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1px solid {BORDER};
        background: {BG_INPUT};
    }}
    QCheckBox::indicator:checked {{
        background-color: {ACCENT};
        border-color: {ACCENT};
        image: none;
    }}
    QSpinBox {{
        background-color: {BG_INPUT};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px 10px;
    }}
    QSpinBox:hover {{
        border-color: {ACCENT};
    }}
    QFrame#card {{
        background-color: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 10px;
    }}
    QLabel#section_title {{
        color: {ACCENT};
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1px;
    }}
    QLabel#value_label {{
        color: {ACCENT};
        font-size: 12px;
        min-width: 40px;
    }}
    QLabel#muted {{
        color: {TEXT_MUTED};
        font-size: 12px;
    }}
"""

# All gesture names and their readable labels
GESTURE_LABELS = {
    'cursor_move':      'Move cursor',
    'left_click':       'Left click',
    'right_click':      'Right click',
    'double_click':     'Double click',
    'drag':             'Click and drag',
    'scroll_up':        'Scroll up',
    'scroll_down':      'Scroll down',
    'switch_left':      'Switch desktop left',
    'switch_right':     'Switch desktop right',
    'enter':            'Press Enter',
    'fist':             'Freeze cursor',
    'open_palm':        'Pause tracking',
    'keyboard_toggle':  'Toggle keyboard',
}

# Fingertip landmark index to readable name
FINGERTIP_LABELS = {
    4:  'Thumb tip',
    8:  'Index tip',
    12: 'Middle tip',
    16: 'Ring tip',
    20: 'Pinky tip',
}


# ─────────────────────────────────────────
# REUSABLE COMPONENTS
# ─────────────────────────────────────────

def make_card():
    """Returns a styled card QFrame."""
    card = QFrame()
    card.setObjectName("card")
    card.setLayout(QVBoxLayout())
    card.layout().setContentsMargins(16, 14, 16, 14)
    card.layout().setSpacing(10)
    return card

def make_section_title(text):
    """Returns a small uppercase cyan section label."""
    label = QLabel(text.upper())
    label.setObjectName("section_title")
    return label

def make_divider():
    """Returns a thin horizontal divider line."""
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(f"color: {BORDER}; background: {BORDER}; max-height: 1px;")
    return line

def make_slider_row(label_text, min_val, max_val, current, scale=1.0, suffix=""):
    """
    Returns (container_widget, slider, value_label).
    scale: divide slider int value by this to get display value (e.g. 10 for 0.1 steps)
    """
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(12)

    label = QLabel(label_text)
    label.setMinimumWidth(160)

    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setMinimum(min_val)
    slider.setMaximum(max_val)
    slider.setValue(int(current * scale))
    slider.setFixedHeight(20)

    display_val = current if scale == 1.0 else round(current, 2)
    value_label = QLabel(f"{display_val}{suffix}")
    value_label.setObjectName("value_label")
    value_label.setMinimumWidth(48)
    value_label.setAlignment(Qt.AlignmentFlag.AlignRight)

    layout.addWidget(label)
    layout.addWidget(slider, 1)
    layout.addWidget(value_label)

    return container, slider, value_label


# ─────────────────────────────────────────
# TOGGLE SWITCH WIDGET
# ─────────────────────────────────────────

class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, checked=True):
        super().__init__()
        self.setFixedSize(QSize(44, 24))
        self._checked = checked

    def is_checked(self):
        return self._checked

    def set_checked(self, value):
        self._checked = value
        self.update()

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self.toggled.emit(self._checked)
        self.update()

    def paintEvent(self, event):
        from PyQt6.QtGui import QPainter, QColor, QPen
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Track
        track_color = QColor(ACCENT) if self._checked else QColor(BORDER)
        painter.setBrush(track_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 4, 44, 16, 8, 8)

        # Knob
        knob_x = 22 if self._checked else 2
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(knob_x, 2, 20, 20)

        painter.end()


# ─────────────────────────────────────────
# MAIN SETTINGS WINDOW
# ─────────────────────────────────────────

class SettingsWindow(QWidget):
    # Emitted when user saves — main loop listens to this
    settings_saved = pyqtSignal()

    def __init__(self, config, controller, classifier):
        super().__init__()
        self.config = config
        self.controller = controller
        self.classifier = classifier

        self.setWindowTitle("Wavly — Settings")
        self.setMinimumSize(600, 700)
        self.setMaximumWidth(760)
        self.setStyleSheet(STYLESHEET)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint
        )

        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ──
        header = QWidget()
        header.setStyleSheet(f"background-color: {BG_SECONDARY}; border-bottom: 1px solid {BORDER};")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 16, 24, 16)

        title = QLabel("Wavly Settings")
        title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {TEXT_PRIMARY};")

        subtitle = QLabel("Customize gestures, cursor, and keyboard")
        subtitle.setObjectName("muted")

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        save_btn = QPushButton("Save & Apply")
        save_btn.setObjectName("accent_btn")
        save_btn.setFixedWidth(130)
        save_btn.clicked.connect(self._save)

        header_layout.addLayout(title_col)
        header_layout.addStretch()
        header_layout.addWidget(save_btn)

        root.addWidget(header)

        # ── Scrollable content ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(16)

        # Add all sections
        content_layout.addWidget(self._build_cursor_section())
        content_layout.addWidget(self._build_keyboard_section())
        content_layout.addWidget(self._build_camera_section())
        content_layout.addWidget(self._build_gestures_section())
        content_layout.addWidget(self._build_fingertip_section())
        content_layout.addSpacerItem(
            QSpacerItem(0, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        scroll.setWidget(content)
        root.addWidget(scroll)

        # ── Footer ──
        footer = QWidget()
        footer.setStyleSheet(f"background-color: {BG_SECONDARY}; border-top: 1px solid {BORDER};")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(24, 12, 24, 12)

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setObjectName("danger_btn")
        reset_btn.clicked.connect(self._reset_defaults)

        status = QLabel("Changes apply instantly after saving")
        status.setObjectName("muted")

        footer_layout.addWidget(reset_btn)
        footer_layout.addStretch()
        footer_layout.addWidget(status)

        root.addWidget(footer)

    # ─────────────────────────────────────────
    # SECTION BUILDERS
    # ─────────────────────────────────────────

    def _build_cursor_section(self):
        card = make_card()
        card.layout().addWidget(make_section_title("Cursor"))

        # Sensitivity
        row, self.sensitivity_slider, self.sensitivity_label = make_slider_row(
            "Sensitivity", 1, 30,
            self.config.get('cursor', 'sensitivity', default=1.0),
            scale=10, suffix="x"
        )
        self.sensitivity_slider.valueChanged.connect(
            lambda v: self.sensitivity_label.setText(f"{v/10:.1f}x")
        )
        card.layout().addWidget(row)

        card.layout().addWidget(make_divider())

        # Smoothing
        row, self.smoothing_slider, self.smoothing_label = make_slider_row(
            "Smoothing", 1, 20,
            self.config.get('cursor', 'smoothing', default=5),
            scale=1, suffix=""
        )
        self.smoothing_slider.valueChanged.connect(
            lambda v: self.smoothing_label.setText(str(v))
        )
        hint = QLabel("Higher = smoother but more lag")
        hint.setObjectName("muted")
        card.layout().addWidget(row)
        card.layout().addWidget(hint)

        return card

    def _build_keyboard_section(self):
        card = make_card()
        card.layout().addWidget(make_section_title("Keyboard Overlay"))

        # Opacity
        row, self.opacity_slider, self.opacity_label = make_slider_row(
            "Opacity", 5, 90,
            int(self.config.get('typing', 'keyboard_opacity', default=0.2) * 100),
            scale=1, suffix="%"
        )
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )
        card.layout().addWidget(row)

        card.layout().addWidget(make_divider())

        # Dwell time
        row, self.dwell_slider, self.dwell_label = make_slider_row(
            "Dwell time (key press delay)", 3, 20,
            int(self.config.get('typing', 'dwell_time', default=0.8) * 10),
            scale=1, suffix="s"
        )
        self.dwell_slider.valueChanged.connect(
            lambda v: self.dwell_label.setText(f"{v/10:.1f}s")
        )
        card.layout().addWidget(row)

        card.layout().addWidget(make_divider())

        # Keyboard position
        pos_row = QWidget()
        pos_layout = QHBoxLayout(pos_row)
        pos_layout.setContentsMargins(0, 0, 0, 0)
        pos_layout.setSpacing(12)

        pos_label = QLabel("Keyboard position")
        pos_label.setMinimumWidth(160)

        self.position_combo = QComboBox()
        self.position_combo.addItems(["bottom", "top", "center"])
        current_pos = self.config.get('typing', 'keyboard_position', default='bottom')
        self.position_combo.setCurrentText(current_pos)

        pos_layout.addWidget(pos_label)
        pos_layout.addWidget(self.position_combo)
        pos_layout.addStretch()

        card.layout().addWidget(pos_row)

        return card

    def _build_camera_section(self):
        card = make_card()
        card.layout().addWidget(make_section_title("Camera"))

        cam_row = QWidget()
        cam_layout = QHBoxLayout(cam_row)
        cam_layout.setContentsMargins(0, 0, 0, 0)
        cam_layout.setSpacing(12)

        cam_label = QLabel("Camera index")
        cam_label.setMinimumWidth(160)

        self.camera_spin = QSpinBox()
        self.camera_spin.setMinimum(0)
        self.camera_spin.setMaximum(5)
        self.camera_spin.setValue(
            self.config.get('app', 'camera_index', default=0)
        )
        self.camera_spin.setFixedWidth(80)

        hint = QLabel("0 = default webcam, 1+ = external cameras")
        hint.setObjectName("muted")

        cam_layout.addWidget(cam_label)
        cam_layout.addWidget(self.camera_spin)
        cam_layout.addWidget(hint)
        cam_layout.addStretch()

        card.layout().addWidget(cam_row)

        card.layout().addWidget(make_divider())

        # Pinch threshold
        row, self.pinch_slider, self.pinch_label = make_slider_row(
            "Pinch sensitivity", 10, 80,
            self.config.get('gestures', 'pinch_threshold', default=40),
            scale=1, suffix="px"
        )
        self.pinch_slider.valueChanged.connect(
            lambda v: self.pinch_label.setText(f"{v}px")
        )
        hint2 = QLabel("Lower = tighter pinch needed to click")
        hint2.setObjectName("muted")
        card.layout().addWidget(row)
        card.layout().addWidget(hint2)

        return card

    def _build_gestures_section(self):
        card = make_card()
        card.layout().addWidget(make_section_title("Gesture Toggles"))

        hint = QLabel("Disable gestures you don't use to reduce false triggers")
        hint.setObjectName("muted")
        card.layout().addWidget(hint)

        self.gesture_toggles = {}

        grid = QWidget()
        grid_layout = QGridLayout(grid)
        grid_layout.setContentsMargins(0, 4, 0, 0)
        grid_layout.setSpacing(10)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(3, 1)

        items = list(GESTURE_LABELS.items())
        for i, (key, label) in enumerate(items):
            row = i // 2
            col_offset = (i % 2) * 2

            enabled = self.config.is_gesture_enabled(key)
            toggle = ToggleSwitch(checked=enabled)
            self.gesture_toggles[key] = toggle

            name_label = QLabel(label)

            grid_layout.addWidget(toggle, row, col_offset)
            grid_layout.addWidget(name_label, row, col_offset + 1)

        card.layout().addWidget(grid)
        return card

    def _build_fingertip_section(self):
        card = make_card()
        card.layout().addWidget(make_section_title("Typing Fingertips"))

        hint = QLabel("Select which fingertips are used for keyboard typing")
        hint.setObjectName("muted")
        card.layout().addWidget(hint)

        current_tips = self.config.get('typing', 'fingertips', default=[8])
        self.fingertip_checks = {}

        tips_row = QWidget()
        tips_layout = QHBoxLayout(tips_row)
        tips_layout.setContentsMargins(0, 4, 0, 0)
        tips_layout.setSpacing(20)

        for landmark_id, label in FINGERTIP_LABELS.items():
            cb = QCheckBox(label)
            cb.setChecked(landmark_id in current_tips)
            self.fingertip_checks[landmark_id] = cb
            tips_layout.addWidget(cb)

        tips_layout.addStretch()
        card.layout().addWidget(tips_row)

        return card

    # ─────────────────────────────────────────
    # SAVE & RESET
    # ─────────────────────────────────────────

    def _save(self):
        # Cursor
        self.config.set('cursor', 'sensitivity',
            value=round(self.sensitivity_slider.value() / 10, 1))
        self.config.set('cursor', 'smoothing',
            value=self.smoothing_slider.value())

        # Keyboard
        self.config.set('typing', 'keyboard_opacity',
            value=round(self.opacity_slider.value() / 100, 2))
        self.config.set('typing', 'dwell_time',
            value=round(self.dwell_slider.value() / 10, 1))
        self.config.set('typing', 'keyboard_position',
            value=self.position_combo.currentText())

        # Camera
        self.config.set('app', 'camera_index',
            value=self.camera_spin.value())

        # Pinch threshold
        self.config.set('gestures', 'pinch_threshold',
            value=self.pinch_slider.value())

        # Gesture toggles
        for key, toggle in self.gesture_toggles.items():
            self.config.set('gesture_enabled', key,
                value=toggle.is_checked())

        # Typing fingertips
        selected_tips = [
            lid for lid, cb in self.fingertip_checks.items()
            if cb.isChecked()
        ]
        # Always keep at least one fingertip selected
        if not selected_tips:
            selected_tips = [8]
        self.config.set('typing', 'fingertips', value=selected_tips)

        # Hot-reload into running components
        self.controller.update_from_config(self.config)
        self.classifier.update_from_config(self.config)

        # Notify main loop
        self.settings_saved.emit()

        print("Settings saved and applied.")

    def _reset_defaults(self):
        """Resets all UI controls to default values without saving."""
        self.sensitivity_slider.setValue(10)
        self.smoothing_slider.setValue(5)
        self.opacity_slider.setValue(20)
        self.dwell_slider.setValue(8)
        self.position_combo.setCurrentText("bottom")
        self.camera_spin.setValue(0)
        self.pinch_slider.setValue(40)

        for key, toggle in self.gesture_toggles.items():
            toggle.set_checked(True)

        for lid, cb in self.fingertip_checks.items():
            cb.setChecked(lid == 8)

        print("Reset to defaults. Press Save & Apply to confirm.")