import pyautogui
import pynput.keyboard as kb
import time

# Safety — stops pyautogui from throwing errors at screen edges
pyautogui.FAILSAFE = False
# Removes the default 0.1s delay between pyautogui actions
pyautogui.PAUSE = 0

class Controller:
    def __init__(self, screen_w, screen_h, cam_w=640, cam_h=480):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.cam_w = cam_w
        self.cam_h = cam_h

        # Smoothing — previous cursor position
        self.prev_x = 0
        self.prev_y = 0
        self.smoothing = 5  # higher = smoother but slower

        # Drag state
        self.is_dragging = False

        # Tracking paused state
        self.tracking_paused = False

        # Keyboard controller
        self.keyboard = kb.Controller()

    # ─────────────────────────────────────────
    # COORDINATE MAPPING
    # ─────────────────────────────────────────

    def map_to_screen(self, x, y):
        """
        Maps camera coordinates to screen coordinates.
        Adds a dead zone on camera edges so cursor
        doesn't get stuck at screen edges.
        """
        margin = 60  # pixels to ignore at camera edges

        # Clamp to safe zone
        x = max(margin, min(self.cam_w - margin, x))
        y = max(margin, min(self.cam_h - margin, y))

        # Map to screen
        screen_x = (x - margin) / (self.cam_w - 2 * margin) * self.screen_w
        screen_y = (y - margin) / (self.cam_h - 2 * margin) * self.screen_h

        return int(screen_x), int(screen_y)

    def smooth(self, target_x, target_y):
        """
        Smooths cursor movement by interpolating between
        current and previous position.
        """
        smooth_x = self.prev_x + (target_x - self.prev_x) / self.smoothing
        smooth_y = self.prev_y + (target_y - self.prev_y) / self.smoothing
        self.prev_x = smooth_x
        self.prev_y = smooth_y
        return int(smooth_x), int(smooth_y)

    # ─────────────────────────────────────────
    # ACTIONS
    # ─────────────────────────────────────────

    def move_cursor(self, landmark):
        """Moves cursor to mapped position of index fingertip."""
        if self.tracking_paused:
            return
        raw_x = landmark['x']
        raw_y = landmark['y']
        screen_x, screen_y = self.map_to_screen(raw_x, raw_y)
        smooth_x, smooth_y = self.smooth(screen_x, screen_y)
        pyautogui.moveTo(smooth_x, smooth_y)

    def left_click(self):
        if self.tracking_paused:
            return
        if self.is_dragging:
            self.stop_drag()
        pyautogui.click()

    def right_click(self):
        if self.tracking_paused:
            return
        pyautogui.rightClick()

    def double_click(self):
        if self.tracking_paused:
            return
        pyautogui.doubleClick()

    def start_drag(self):
        if self.tracking_paused:
            return
        if not self.is_dragging:
            pyautogui.mouseDown()
            self.is_dragging = True

    def stop_drag(self):
        if self.is_dragging:
            pyautogui.mouseUp()
            self.is_dragging = False

    def scroll(self, direction):
        if self.tracking_paused:
            return
        amount = 3  # scroll units per gesture
        if direction == 'up':
            pyautogui.scroll(amount)
        elif direction == 'down':
            pyautogui.scroll(-amount)

    def switch_desktop(self, direction):
        """
        Switches virtual desktop using Win + Ctrl + Arrow.
        Windows 10/11 only.
        """
        if self.tracking_paused:
            return
        key = kb.Key.right if direction == 'right' else kb.Key.left
        with self.keyboard.pressed(kb.Key.ctrl):
            with self.keyboard.pressed(kb.Key.cmd):
                self.keyboard.press(key)
                self.keyboard.release(key)

    def press_enter(self):
        if self.tracking_paused:
            return
        pyautogui.press('enter')

    def toggle_tracking(self):
        """Pauses or resumes all tracking."""
        self.tracking_paused = not self.tracking_paused
        state = "PAUSED" if self.tracking_paused else "RESUMED"
        print(f"Tracking {state}")
        # Make sure drag is released if tracking pauses mid-drag
        if self.tracking_paused:
            self.stop_drag()