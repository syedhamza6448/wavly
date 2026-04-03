import pyautogui
import pynput.keyboard as kb
import time

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

class Controller:
    def __init__(self, screen_w, screen_h, cam_w=640, cam_h=480, config=None):
        self.screen_w   = screen_w
        self.screen_h   = screen_h
        self.cam_w      = cam_w
        self.cam_h      = cam_h
        self.smoothing  = config.get('cursor', 'smoothing',    default=5)   if config else 5
        self.sensitivity= config.get('cursor', 'sensitivity',  default=1.0) if config else 1.0
        self.margin     = config.get('cursor', 'margin',       default=30)  if config else 30
        self.prev_x     = 0
        self.prev_y     = 0
        self.is_dragging     = False
        self.tracking_paused = False
        self.keyboard        = kb.Controller()

    def map_to_screen(self, x, y):
        margin   = self.margin
        x        = max(margin, min(self.cam_w - margin, x))
        y        = max(margin, min(self.cam_h - margin, y))
        screen_x = (x - margin) / (self.cam_w - 2 * margin) * self.screen_w * self.sensitivity
        screen_y = (y - margin) / (self.cam_h - 2 * margin) * self.screen_h * self.sensitivity
        screen_x = max(0, min(self.screen_w, int(screen_x)))
        screen_y = max(0, min(self.screen_h, int(screen_y)))
        return screen_x, screen_y

    def smooth(self, target_x, target_y):
        smooth_x     = self.prev_x + (target_x - self.prev_x) / self.smoothing
        smooth_y     = self.prev_y + (target_y - self.prev_y) / self.smoothing
        self.prev_x  = smooth_x
        self.prev_y  = smooth_y
        return int(smooth_x), int(smooth_y)

    def move_cursor(self, landmark):
        if self.tracking_paused:
            return
        screen_x, screen_y = self.map_to_screen(landmark['x'], landmark['y'])
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
        self.tracking_paused = not self.tracking_paused
        state = "PAUSED" if self.tracking_paused else "RESUMED"
        print(f"Tracking {state}")
        if self.tracking_paused:
            self.stop_drag()

    def update_from_config(self, config):
        self.smoothing   = config.get('cursor', 'smoothing',   default=5)
        self.sensitivity = config.get('cursor', 'sensitivity', default=1.0)
        self.margin      = config.get('cursor', 'margin',      default=30)