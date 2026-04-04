import pyautogui
import pynput.keyboard as kb
import time

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

class Controller:
    def __init__(self, screen_w, screen_h, cam_w=640, cam_h=480, config=None):
        self.screen_w    = screen_w
        self.screen_h    = screen_h
        self.cam_w       = cam_w
        self.cam_h       = cam_h
        self.smoothing   = config.get('cursor', 'smoothing',    default=5)   if config else 5
        self.sensitivity = config.get('cursor', 'sensitivity',  default=1.0) if config else 1.0
        self.margin      = config.get('cursor', 'margin',       default=20)  if config else 20
        self.prev_x      = 0
        self.prev_y      = 0
        self.is_dragging     = False
        self.tracking_paused = False
        self.keyboard        = kb.Controller()

    def map_to_screen(self, x, y):
        """
        Maps camera coords to screen coords.
        Uses a reduced active zone so the cursor
        can reach all screen corners comfortably.
        """
        margin = self.margin

        # Active camera zone — inner portion of frame
        active_w = self.cam_w - 2 * margin
        active_h = self.cam_h - 2 * margin

        # Clamp to active zone
        x = max(margin, min(self.cam_w - margin, x))
        y = max(margin, min(self.cam_h - margin, y))

        # Normalize to 0.0 - 1.0
        nx = (x - margin) / active_w
        ny = (y - margin) / active_h

        # Apply sensitivity — stretch beyond 1.0 so corners are reachable
        nx = (nx - 0.5) * self.sensitivity + 0.5
        ny = (ny - 0.5) * self.sensitivity + 0.5

        # Map to screen
        screen_x = nx * self.screen_w
        screen_y = ny * self.screen_h

        # Clamp to screen
        screen_x = max(0, min(self.screen_w - 1, int(screen_x)))
        screen_y = max(0, min(self.screen_h - 1, int(screen_y)))

        return screen_x, screen_y

    def smooth(self, target_x, target_y):
        smooth_x    = self.prev_x + (target_x - self.prev_x) / self.smoothing
        smooth_y    = self.prev_y + (target_y - self.prev_y) / self.smoothing
        self.prev_x = smooth_x
        self.prev_y = smooth_y
        return int(smooth_x), int(smooth_y)

    def move_cursor(self, landmark):
        if self.tracking_paused:
            return
        screen_x, screen_y = self.map_to_screen(
            landmark['x'], landmark['y']
        )
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
        amount = 3
        if direction == 'up':
            pyautogui.scroll(amount)
        elif direction == 'down':
            pyautogui.scroll(-amount)

    def switch_desktop(self, direction):
        """Alt+Tab (right) or Alt+Shift+Tab (left)."""
        if self.tracking_paused:
            return
        if direction == 'right':
            with self.keyboard.pressed(kb.Key.alt):
                self.keyboard.press(kb.Key.tab)
                self.keyboard.release(kb.Key.tab)
        elif direction == 'left':
            with self.keyboard.pressed(kb.Key.alt):
                with self.keyboard.pressed(kb.Key.shift):
                    self.keyboard.press(kb.Key.tab)
                    self.keyboard.release(kb.Key.tab)

    def press_enter(self):
        if self.tracking_paused:
            return
        pyautogui.press('enter')

    def toggle_tracking(self):
        self.tracking_paused = not self.tracking_paused
        state = "PAUSED" if self.tracking_paused else "RESUMED"
        print(f"Tracking {state}")
        if self.tracking_paused:
            self.stop_drag()

    def update_from_config(self, config):
        self.smoothing   = config.get('cursor', 'smoothing',   default=5)
        self.sensitivity = config.get('cursor', 'sensitivity', default=1.0)
        self.margin      = config.get('cursor', 'margin',      default=20)