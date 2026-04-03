import traceback

tests = [
    ("PyQt6",      "from PyQt6.QtWidgets import QApplication"),
    ("Fonts",      "from ui.fonts import load_fonts; load_fonts()"),
    ("Dashboard",  "from ui.dashboard import DashboardWindow"),
    ("Settings",   "from ui.app import SettingsWindow"),
    ("Toolbar",    "from ui.toolbar import SlideToolbar"),
    ("Camera",     "from core.camera import Camera"),
    ("Detector",   "from core.detector import HandDetector"),
    ("Controller", "from core.controller import Controller"),
    ("Classifier", "from gestures.classifier import GestureClassifier"),
    ("Keyboard",   "from keyboard.overlay import KeyboardOverlay"),
    ("Dwell",      "from keyboard.dwell import DwellManager"),
    ("Config",     "from utils.config_manager import ConfigManager"),
    ("Tray",       "from ui.tray import TrayIcon"),
    ("Dashboard2", "from ui.dashboard import DashboardWindow"),
]

for name, code in tests:
    try:
        exec(code)
        print(f"OK     {name}")
    except Exception as e:
        print(f"FAIL   {name}: {e}")
        traceback.print_exc()
        print()

input("\nPress Enter to close...")