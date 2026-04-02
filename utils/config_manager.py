import json
import sys
import os

def resource_path(relative_path):
    """
    Gets the correct path to a resource whether running
    as a script or as a PyInstaller bundled .exe.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

CONFIG_PATH = resource_path('config/gestures.json')

class ConfigManager:
    def __init__(self):
        self.path = CONFIG_PATH
        self.config = {}
        self.load()

    def load(self):
        try:
            with open(self.path, 'r') as f:
                self.config = json.load(f)
            print("Config loaded.")
        except FileNotFoundError:
            print(f"Config not found at {self.path}. Using defaults.")
            self.config = {}
        except json.JSONDecodeError as e:
            print(f"Config file is corrupted: {e}. Using defaults.")
            self.config = {}

    def save(self):
        try:
            with open(self.path, 'w') as f:
                json.dump(self.config, f, indent=4)
            print("Config saved.")
        except Exception as e:
            print(f"Failed to save config: {e}")

    def get(self, *keys, default=None):
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, *keys, value):
        d = self.config
        for key in keys[:-1]:
            if key not in d or not isinstance(d[key], dict):
                d[key] = {}
            d = d[key]
        d[keys[-1]] = value
        self.save()

    def is_gesture_enabled(self, gesture_name):
        return self.get('gesture_enabled', gesture_name, default=True)

    def toggle_gesture(self, gesture_name):
        current = self.is_gesture_enabled(gesture_name)
        self.set('gesture_enabled', gesture_name, value=not current)
        return not current

    def get_gesture_mapping(self, gesture_name):
        return self.get('gesture_mappings', gesture_name, default=gesture_name)

    def reload(self):
        self.load()