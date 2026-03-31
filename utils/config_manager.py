import json
import os

CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'config', 'gestures.json'
)

class ConfigManager:
    def __init__(self):
        self.path = CONFIG_PATH
        self.config = {}
        self.load()
        
    def load(self):
        """Loads config from disk."""
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
        """Save current config to disk."""
        try:
            with open(self.path, 'w') as f:
                json.dump(self.config, f, indent=4)
            print("Config saved.")
        except Exception as e:
            print(f"Failed to save config: {e}")
            
    def get(self, *keys, default=None):
        """
        Gets a nested value using dot-style keys.
        Example: config.get('typing', 'dwell_time') -> 0.8
        """
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, *keys, value):
        """
        Sets a nested value and saves to disk.
        Example: config.set('typing', 'dwell_time', value=1.0)
        """
        d = self.config
        for key in keys[:-1]:
            if key not in d or not isinstance(d[key], dict):
                d[key] = {}
            d = d[key]
        d[keys[-1]] = value
        self.save()
        
    def is_gesture_enabled(self, gesture_name):
        """Returns True if a gesture is enabled in config."""
        return self.get('gesture_enabled', gesture_name, default=True)
    
    def toggle_gesture(self, gesture_name):
        """Flips a gesture's enabled state and saves."""
        current = self.is_gesture_enabled(gesture_name)
        self.set('gesture_enabled', gesture_name, value=not current)
        return not current
    
    def get_gesture_mapping(self, gesture_name):
        """Returns the action mapped to a gesture."""
        return self.get('gesture_mappings', gesture_name, default=gesture_name)
    
    def reload(self):
        """Reloads config from disk - useful after external edits."""
        self.load()
        
        