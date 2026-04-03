from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QComboBox, QScrollArea,
    QFrame, QGridLayout, QSpinBox, QCheckBox,
    QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPen
from ui.fonts import load_fonts, FONT_DISPLAY, FONT_BODY

load_fonts()

BG_PRIMARY   = "#080c0c"
BG_SECONDARY = "#0d1515"
BG_CARD      = "#111d1d"
BG_CARD2     = "#0f1a1a"
BG_INPUT     = "#0d1f1f"
ACCENT       = "#00dcdc"
ACCENT_DIM   = "#007a7a"
ACCENT_GLOW  = "#00dcdc15"
TEXT_PRIMARY = "#e8f4f4"
TEXT_MUTED   = "#4a7070"
TEXT_DIM     = "#2a5050"
BORDER       = "#0d2a2a"
BORDER_ACC   = "#00dcdc33"
DANGER       = "#ff4f6a"
SUCCESS      = "#00dc8a"
WARNING      = "#f0a500"

STYLESHEET = f"""
    QWidget {{
        background-color: {BG_PRIMARY};
        color: {TEXT_PRIMARY};
        font-family: '{FONT_BODY}';
        font-size: 13px;
        border: none;
    }}
    QScrollArea {{
        border: none;
        background-color: {BG_PRIMARY};
    }}
    QScrollBar:vertical {{
        background: {BG_SECONDARY};
        width: 4px;
        border-radius: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {ACCENT_DIM};
        border-radius: 2px;
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{ height: 0px; }}
    QPushButton {{
        background-color: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 9px 18px;
        font-size: 13px;
        font-family: '{FONT_BODY}';
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
    QPushButton#accent_btn {{
        background-color: {ACCENT};
        color: {BG_PRIMARY};
        border: none;
        font-weight: 700;
        font-family: '{FONT_BODY}';
    }}
    QPushButton#accent_btn:hover {{
        background-color: #00f0f0;
    }}
    QPushButton#danger_btn {{
        background-color: transparent;
        color: {DANGER};
        border: 1px solid {DANGER}44;
    }}
    QPushButton#danger_btn:hover {{
        background-color: {DANGER}22;
        border-color: {DANGER};
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
        border-radius: 8px;
        padding: 7px 12px;
        min-width: 120px;
        font-family: '{FONT_BODY}';
    }}
    QComboBox:hover {{ border-color: {ACCENT}; }}
    QComboBox::drop-down {{ border: none; width: 24px; }}
    QComboBox QAbstractItemView {{
        background-color: {BG_CARD};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        selection-background-color: {ACCENT_DIM};
        font-family: '{FONT_BODY}';
    }}
    QCheckBox {{
        spacing: 8px;
        color: {TEXT_PRIMARY};
        font-family: '{FONT_BODY}';
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
    }}
    QSpinBox {{
        background-color: {BG_INPUT};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 7px 10px;
        font-family: '{FONT_BODY}';
    }}
    QSpinBox:hover {{ border-color: {ACCENT}; }}
    QFrame#card {{
        background-color: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
    }}
    QFrame#accent_card {{
        background-color: {BG_CARD2};
        border: 1px solid {BORDER_ACC};
        border-radius: 12px;
    }}
    QLabel#section_title {{
        color: {ACCENT};
        font-size: 10px;
        font-family: '{FONT_BODY}';
        letter-spacing: 2px;
    }}
    QLabel#value_label {{
        color: {ACCENT};
        font-size: 13px;
        font-family: '{FONT_DISPLAY}';
        min-width: 48px;
    }}
    QLabel#muted {{
        color: {TEXT_MUTED};
        font-size: 11px;
        font-family: '{FONT_BODY}';
    }}
    QLabel#page_title {{
        font-size: 22px;
        font-weight: 700;
        color: {TEXT_PRIMARY};
        font-family: '{FONT_DISPLAY}';
        letter-spacing: 1px;
    }}
"""

GESTURE_LABELS = {
    'cursor_move':     'Move cursor',
    'left_click':      'Left click',
    'right_click':     'Right click',
    'double_click':    'Double click',
    'drag':            'Click and drag',
    'scroll_up':       'Scroll up',
    'scroll_down':     'Scroll down',
    'switch_left':     'Switch desktop left',
    'switch_right':    'Switch desktop right',
    'enter':           'Press Enter',
    'fist':            'Freeze cursor',
    'open_palm':       'Pause tracking',
    'keyboard_toggle': 'Toggle keyboard',
}

FINGERTIP_LABELS = {
    4:  'Thumb',
    8:  'Index',
    12: 'Middle',
    16: 'Ring',
    20: 'Pinky',
}


# ─────────────────────────────────────────
# COMPONENTS
# ─────────────────────────────────────────

def make_card(accent=False):
    card = QFrame()
    card.setObjectName("accent_card" if accent else "card")
    layout = QVBoxLayout(card)
    layout.setContentsMargins(20, 16, 20, 16)
    layout.setSpacing(12)
    return card

def make_section_title(text):
    label = QLabel(text.upper())
    label.setObjectName("section_title")
    return label

def make_divider():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(
        f"background: {BORDER}; max-height: 1px; border: none;"
    )
    return line

def make_slider_row(label_text, min_val, max_val, current, scale=1.0, suffix=""):
    container = QWidget()
    layout    = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(14)

    label = QLabel(label_text)
    label.setMinimumWidth(180)
    label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-family: '{FONT_BODY}';")

    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setMinimum(min_val)
    slider.setMaximum(max_val)
    slider.setValue(int(current * scale))
    slider.setFixedHeight(20)

    display_val = current if scale == 1.0 else round(current, 2)
    value_label = QLabel(f"{display_val}{suffix}")
    value_label.setObjectName("value_label")
    value_label.setMinimumWidth(52)
    value_label.setAlignment(Qt.AlignmentFlag.AlignRight)

    layout.addWidget(label)
    layout.addWidget(slider, 1)
    layout.addWidget(value_label)

    return container, slider, value_label


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
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        track_color = QColor(ACCENT) if self._checked else QColor(BORDER)
        painter.setBrush(track_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 4, 44, 16, 8, 8)
        knob_x = 22 if self._checked else 2
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(knob_x, 2, 20, 20)
        painter.end()


# ─────────────────────────────────────────
# SETTINGS WINDOW
# ─────────────────────────────────────────

class SettingsWindow(QWidget):
    settings_saved = pyqtSignal()

    def __init__(self, config, controller, classifier):
        super().__init__()
        self.config     = config
        self.controller = controller
        self.classifier = classifier

        self.setWindowTitle("Wavly — Settings")
        self.setMinimumSize(960, 640)
        self.setStyleSheet(STYLESHEET)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint
        )

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
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(20, 36, 20, 24)
        sb.setSpacing(0)

        logo = QLabel("WAVLY")
        logo.setStyleSheet(
            f"font-size: 22px; font-weight: 700; color: {ACCENT};"
            f"font-family: '{FONT_DISPLAY}'; letter-spacing: 2px;"
        )
        sub = QLabel("SETTINGS")
        sub.setStyleSheet(
            f"font-size: 10px; color: {TEXT_MUTED};"
            f"font-family: '{FONT_BODY}'; letter-spacing: 3px;"
        )
        sb.addWidget(logo)
        sb.addSpacing(4)
        sb.addWidget(sub)
        sb.addSpacing(40)

        # Section nav buttons
        self._nav_btns = {}
        sections = [
            ("cursor",    "  🖱   Cursor"),
            ("keyboard",  "  ⌨   Keyboard"),
            ("camera",    "  📷   Camera"),
            ("gestures",  "  ✋   Gestures"),
            ("fingertips","  👆   Fingertips"),
        ]

        for key, label in sections:
            btn = QPushButton(label)
            btn.setFixedHeight(44)
            btn.clicked.connect(
                lambda _, k=key: self._scroll_to(k)
            )
            self._nav_btns[key] = btn
            sb.addWidget(btn)
            sb.addSpacing(4)

        sb.addStretch()

        save_btn = QPushButton("Save & Apply")
        save_btn.setObjectName("accent_btn")
        save_btn.setFixedHeight(44)
        save_btn.clicked.connect(self._save)
        sb.addWidget(save_btn)
        sb.addSpacing(8)

        reset_btn = QPushButton("Reset Defaults")
        reset_btn.setObjectName("danger_btn")
        reset_btn.setFixedHeight(44)
        reset_btn.clicked.connect(self._reset_defaults)
        sb.addWidget(reset_btn)
        sb.addSpacing(16)

        version = QLabel("WAVLY  ·  IT VISION  ·  V1.0")
        version.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 10px;"
            f"font-family: '{FONT_BODY}'; letter-spacing: 1px;"
        )
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sb.addWidget(version)

        root.addWidget(sidebar)

        # ── Content ──
        content_wrapper = QWidget()
        cw_layout = QVBoxLayout(content_wrapper)
        cw_layout.setContentsMargins(0, 0, 0, 0)
        cw_layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(72)
        header.setStyleSheet(
            f"background-color: {BG_SECONDARY};"
            f"border-bottom: 1px solid {BORDER};"
        )
        hl = QHBoxLayout(header)
        hl.setContentsMargins(36, 0, 36, 0)

        page_title = QLabel("Settings")
        page_title.setObjectName("page_title")

        status_lbl = QLabel("Changes apply instantly after saving")
        status_lbl.setObjectName("muted")

        hl.addWidget(page_title)
        hl.addStretch()
        hl.addWidget(status_lbl)

        cw_layout.addWidget(header)

        # Scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(36, 32, 36, 32)
        self._content_layout.setSpacing(20)

        # Section anchors
        self._section_widgets = {}

        self._add_section("cursor",     "Cursor",           self._build_cursor_section())
        self._add_section("keyboard",   "Keyboard Overlay", self._build_keyboard_section())
        self._add_section("camera",     "Camera",           self._build_camera_section())
        self._add_section("gestures",   "Gesture Toggles",  self._build_gestures_section())
        self._add_section("fingertips", "Typing Fingertips",self._build_fingertip_section())

        self._content_layout.addSpacerItem(
            QSpacerItem(
                0, 40,
                QSizePolicy.Policy.Minimum,
                QSizePolicy.Policy.Expanding
            )
        )

        self._scroll.setWidget(self._content)
        cw_layout.addWidget(self._scroll)

        root.addWidget(content_wrapper)

    def _add_section(self, key, title, widget):
        """Adds a titled section with an anchor for nav."""
        wrapper = QWidget()
        wl = QVBoxLayout(wrapper)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(10)

        title_label = QLabel(title.upper())
        title_label.setStyleSheet(
            f"font-size: 10px; color: {ACCENT};"
            f"font-family: '{FONT_BODY}'; letter-spacing: 2px;"
        )
        wl.addWidget(title_label)
        wl.addWidget(widget)

        self._section_widgets[key] = wrapper
        self._content_layout.addWidget(wrapper)

    def _scroll_to(self, key):
        widget = self._section_widgets.get(key)
        if widget:
            self._scroll.ensureWidgetVisible(widget)

    # ─────────────────────────────────────────
    # SECTION BUILDERS
    # ─────────────────────────────────────────

    def _build_cursor_section(self):
        card = make_card()

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

        row, self.smoothing_slider, self.smoothing_label = make_slider_row(
            "Smoothing", 1, 20,
            self.config.get('cursor', 'smoothing', default=5),
            scale=1, suffix=""
        )
        self.smoothing_slider.valueChanged.connect(
            lambda v: self.smoothing_label.setText(str(v))
        )
        hint = QLabel("Higher = smoother but slightly more lag")
        hint.setObjectName("muted")
        card.layout().addWidget(row)
        card.layout().addWidget(hint)
        return card

    def _build_keyboard_section(self):
        card = make_card()

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

        pos_row = QWidget()
        pl = QHBoxLayout(pos_row)
        pl.setContentsMargins(0, 0, 0, 0)
        pl.setSpacing(14)

        pos_label = QLabel("Keyboard position")
        pos_label.setMinimumWidth(180)
        pos_label.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-family: '{FONT_BODY}';"
        )

        self.position_combo = QComboBox()
        self.position_combo.addItems(["bottom", "top", "center"])
        self.position_combo.setCurrentText(
            self.config.get('typing', 'keyboard_position', default='bottom')
        )

        pl.addWidget(pos_label)
        pl.addWidget(self.position_combo)
        pl.addStretch()
        card.layout().addWidget(pos_row)
        return card

    def _build_camera_section(self):
        card = make_card()

        cam_row = QWidget()
        cl = QHBoxLayout(cam_row)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(14)

        cam_label = QLabel("Camera index")
        cam_label.setMinimumWidth(180)
        cam_label.setStyleSheet(
            f"color: {TEXT_PRIMARY}; font-family: '{FONT_BODY}';"
        )

        self.camera_spin = QSpinBox()
        self.camera_spin.setMinimum(0)
        self.camera_spin.setMaximum(5)
        self.camera_spin.setValue(
            self.config.get('app', 'camera_index', default=0)
        )
        self.camera_spin.setFixedWidth(80)

        hint = QLabel("0 = default webcam, 1+ = external cameras")
        hint.setObjectName("muted")

        cl.addWidget(cam_label)
        cl.addWidget(self.camera_spin)
        cl.addWidget(hint)
        cl.addStretch()
        card.layout().addWidget(cam_row)
        card.layout().addWidget(make_divider())

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

        hint = QLabel(
            "Disable gestures you don't use to reduce false triggers"
        )
        hint.setObjectName("muted")
        card.layout().addWidget(hint)

        self.gesture_toggles = {}
        grid        = QWidget()
        grid_layout = QGridLayout(grid)
        grid_layout.setContentsMargins(0, 4, 0, 0)
        grid_layout.setSpacing(10)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(3, 1)

        items = list(GESTURE_LABELS.items())
        for i, (key, label) in enumerate(items):
            row        = i // 2
            col_offset = (i % 2) * 2
            enabled    = self.config.is_gesture_enabled(key)
            toggle     = ToggleSwitch(checked=enabled)
            self.gesture_toggles[key] = toggle

            name_label = QLabel(label)
            name_label.setStyleSheet(
                f"color: {TEXT_PRIMARY}; font-family: '{FONT_BODY}';"
            )

            grid_layout.addWidget(toggle, row, col_offset)
            grid_layout.addWidget(name_label, row, col_offset + 1)

        card.layout().addWidget(grid)
        return card

    def _build_fingertip_section(self):
        card = make_card()

        hint = QLabel("Select which fingertips are used for keyboard typing")
        hint.setObjectName("muted")
        card.layout().addWidget(hint)

        current_tips        = self.config.get('typing', 'fingertips', default=[8])
        self.fingertip_checks = {}

        tips_row = QWidget()
        tl       = QHBoxLayout(tips_row)
        tl.setContentsMargins(0, 4, 0, 0)
        tl.setSpacing(24)

        for landmark_id, label in FINGERTIP_LABELS.items():
            cb = QCheckBox(label)
            cb.setChecked(landmark_id in current_tips)
            cb.setStyleSheet(
                f"color: {TEXT_PRIMARY}; font-family: '{FONT_BODY}';"
            )
            self.fingertip_checks[landmark_id] = cb
            tl.addWidget(cb)

        tl.addStretch()
        card.layout().addWidget(tips_row)
        return card

    # ─────────────────────────────────────────
    # SAVE & RESET
    # ─────────────────────────────────────────

    def _save(self):
        self.config.set('cursor', 'sensitivity',
            value=round(self.sensitivity_slider.value() / 10, 1))
        self.config.set('cursor', 'smoothing',
            value=self.smoothing_slider.value())
        self.config.set('typing', 'keyboard_opacity',
            value=round(self.opacity_slider.value() / 100, 2))
        self.config.set('typing', 'dwell_time',
            value=round(self.dwell_slider.value() / 10, 1))
        self.config.set('typing', 'keyboard_position',
            value=self.position_combo.currentText())
        self.config.set('app', 'camera_index',
            value=self.camera_spin.value())
        self.config.set('gestures', 'pinch_threshold',
            value=self.pinch_slider.value())

        for key, toggle in self.gesture_toggles.items():
            self.config.set('gesture_enabled', key,
                value=toggle.is_checked())

        selected_tips = [
            lid for lid, cb in self.fingertip_checks.items()
            if cb.isChecked()
        ]
        if not selected_tips:
            selected_tips = [8]
        self.config.set('typing', 'fingertips', value=selected_tips)

        self.controller.update_from_config(self.config)
        self.classifier.update_from_config(self.config)
        self.settings_saved.emit()
        print("Settings saved and applied.")

    def _reset_defaults(self):
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