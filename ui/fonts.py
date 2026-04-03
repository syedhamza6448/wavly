import os
from PyQt6.QtGui import QFontDatabase, QFont

_fonts_loaded = False

FONT_DISPLAY = "Orbitron"
FONT_BODY    = "Plus Jakarta Sans"

def load_fonts():
    global _fonts_loaded
    if _fonts_loaded:
        return

    fonts_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'assets', 'fonts'
    )

    for fname in os.listdir(fonts_dir):
        if fname.endswith('.ttf') or fname.endswith('.otf'):
            path = os.path.join(fonts_dir, fname)
            fid  = QFontDatabase.addApplicationFont(path)
            if fid == -1:
                print(f"Failed to load font: {fname}")
            else:
                families = QFontDatabase.applicationFontFamilies(fid)
                print(f"Loaded font: {families}")

    _fonts_loaded = True

def display_font(size=24, bold=True):
    f = QFont(FONT_DISPLAY, size)
    f.setBold(bold)
    return f

def body_font(size=13, bold=False):
    f = QFont(FONT_BODY, size)
    f.setBold(bold)
    return f