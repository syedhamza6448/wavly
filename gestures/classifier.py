import math
import time

class GestureClassifier:
    def __init__(self, config=None):
        self.config = config
        self.last_gesture_time = {}
        self.cooldown = config.get('gestures', 'cooldown', default=0.5) if config else 0.5
        self.swipe_start = {}
        self.swipe_threshold = config.get('gestures', 'swipe_threshold', default=50) if config else 50
        self.gesture_start_time = {}
        self.last_pinch_time = 0
        self.double_pinch_window = config.get('gestures', 'double_pinch_window', default=0.4) if config else 0.4
        self.pinch_threshold = config.get('gestures', 'pinch_threshold', default=40) if config else 40
        self.index_hold_duration = config.get('gestures', 'index_hold_duration', default=1.0) if config else 1.0
        self.drag_hold_duration = config.get('gestures', 'drag_hold_duration', default=0.5) if config else 0.5

    # ─────────────────────────────────────────
    # UTILITY METHODS
    # ─────────────────────────────────────────

    def distance(self, p1, p2):
        """Euclidean distance between two landmarks."""
        return math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)

    def is_finger_up(self, landmarks, finger_tip, finger_pip):
        """Returns True if a finger is extended."""
        return landmarks[finger_tip]['y'] < landmarks[finger_pip]['y']

    def get_extended_fingers(self, landmarks):
        """
        Returns [thumb, index, middle, ring, pinky].
        True = finger is extended.
        """
        fingers = []

        # Thumb — horizontal comparison
        if landmarks[4]['x'] < landmarks[3]['x']:
            fingers.append(True)
        else:
            fingers.append(False)

        # Index, Middle, Ring, Pinky
        tips = [8,  12, 16, 20]
        pips = [6,  10, 14, 18]
        for tip, pip in zip(tips, pips):
            fingers.append(self.is_finger_up(landmarks, tip, pip))

        return fingers  # [thumb, index, middle, ring, pinky]

    def on_cooldown(self, gesture_name):
        """Returns True if gesture is still in cooldown."""
        now  = time.time()
        last = self.last_gesture_time.get(gesture_name, 0)
        return (now - last) < self.cooldown

    def reset_cooldown(self, gesture_name):
        """Marks a gesture as just fired."""
        self.last_gesture_time[gesture_name] = time.time()

    def enabled(self, gesture_name):
        """Returns True if gesture is enabled in config."""
        if self.config:
            return self.config.is_gesture_enabled(gesture_name)
        return True

    # ─────────────────────────────────────────
    # GESTURE DETECTION METHODS
    # ─────────────────────────────────────────

    def is_pinch(self, landmarks, threshold=None):
        """Thumb tip (4) and index tip (8) are close together."""
        t = threshold or self.pinch_threshold
        return self.distance(landmarks[4], landmarks[8]) < t

    def is_right_click(self, landmarks, threshold=None):
        """Thumb tip (4) and middle tip (12) are close together."""
        t = threshold or self.pinch_threshold
        return self.distance(landmarks[4], landmarks[12]) < t

    def is_fist(self, landmarks):
        """All four fingers are down."""
        fingers = self.get_extended_fingers(landmarks)
        return not any(fingers[1:])

    def is_open_palm(self, landmarks):
        """All five fingers are extended."""
        fingers = self.get_extended_fingers(landmarks)
        return all(fingers)

    def is_three_fingers_up(self, landmarks):
        """Index, middle, ring up. Thumb and pinky down."""
        fingers = self.get_extended_fingers(landmarks)
        return (
            not fingers[0] and
            fingers[1] and
            fingers[2] and
            fingers[3] and
            not fingers[4]
        )

    def is_two_fingers_up(self, landmarks):
        """Index and middle up. Others down."""
        fingers = self.get_extended_fingers(landmarks)
        return (
            fingers[1] and
            fingers[2] and
            not fingers[3] and
            not fingers[4]
        )

    def is_four_fingers_up(self, landmarks):
        """Index, middle, ring, pinky up. Thumb down."""
        fingers = self.get_extended_fingers(landmarks)
        return (
            not fingers[0] and
            fingers[1] and
            fingers[2] and
            fingers[3] and
            fingers[4]
        )

    def is_index_only(self, landmarks):
        """Only index finger is up."""
        fingers = self.get_extended_fingers(landmarks)
        return (
            fingers[1] and
            not fingers[2] and
            not fingers[3] and
            not fingers[4]
        )

    def is_index_held(self, landmarks, duration=None):
        """Index finger held up for set duration. Triggers Enter."""
        duration = duration or self.index_hold_duration
        key = 'index_hold'
        if self.is_index_only(landmarks):
            if key not in self.gesture_start_time:
                self.gesture_start_time[key] = time.time()
            elif time.time() - self.gesture_start_time[key] >= duration:
                self.gesture_start_time.pop(key, None)
                return True
        else:
            self.gesture_start_time.pop(key, None)
        return False

    def is_pinch_held(self, landmarks, duration=None):
        """Pinch held for set duration. Triggers drag."""
        duration = duration or self.drag_hold_duration
        key = 'pinch_hold'
        if self.is_pinch(landmarks):
            if key not in self.gesture_start_time:
                self.gesture_start_time[key] = time.time()
            elif time.time() - self.gesture_start_time[key] >= duration:
                return True
        else:
            self.gesture_start_time.pop(key, None)
        return False

    def is_double_pinch(self, landmarks):
        """Two quick pinches within double_pinch_window seconds."""
        if self.is_pinch(landmarks):
            now = time.time()
            if now - self.last_pinch_time < self.double_pinch_window:
                self.last_pinch_time = 0
                return True
            self.last_pinch_time = now
        return False

    def is_pinky_only(self, landmarks):
        """Only pinky finger is up."""
        fingers = self.get_extended_fingers(landmarks)
        return (
            not fingers[1] and
            not fingers[2] and
            not fingers[3] and
            fingers[4]
        )

    # ─────────────────────────────────────────
    # SWIPE DETECTION
    # ─────────────────────────────────────────

    def get_swipe_direction(self, landmarks, hand_label):
        """Detects swipe direction from index fingertip movement."""
        tip = landmarks[8]
        key = f'swipe_{hand_label}'

        if key not in self.swipe_start:
            # First frame — record start position
            self.swipe_start[key] = {
                'x': tip['x'],
                'y': tip['y'],
                'frames': 0
            }
            return None

        self.swipe_start[key]['frames'] += 1

        dx = tip['x'] - self.swipe_start[key]['x']
        dy = tip['y'] - self.swipe_start[key]['y']

        # Need at least 3 frames of consistent movement
        if self.swipe_start[key]['frames'] < 3:
            return None

        if abs(dx) > self.swipe_threshold:
            self.swipe_start.pop(key, None)
            return 'right' if dx > 0 else 'left'

        if abs(dy) > self.swipe_threshold:
            self.swipe_start.pop(key, None)
            return 'down' if dy > 0 else 'up'

        return None

    def clear_swipe(self, hand_label):
        """Resets swipe tracking when gesture ends."""
        key = f'swipe_{hand_label}'
        self.swipe_start.pop(key, None)

    # ─────────────────────────────────────────
    # CONFIG HOT-RELOAD
    # ─────────────────────────────────────────

    def update_from_config(self, config):
        """Hot-reloads gesture thresholds from config."""
        self.cooldown            = config.get('gestures', 'cooldown',            default=0.5)
        self.swipe_threshold     = config.get('gestures', 'swipe_threshold',     default=50)
        self.double_pinch_window = config.get('gestures', 'double_pinch_window', default=0.4)
        self.pinch_threshold     = config.get('gestures', 'pinch_threshold',     default=40)
        self.index_hold_duration = config.get('gestures', 'index_hold_duration', default=1.0)
        self.drag_hold_duration  = config.get('gestures', 'drag_hold_duration',  default=0.5)

    # ─────────────────────────────────────────
    # MAIN CLASSIFY METHOD
    # ─────────────────────────────────────────

    def classify(self, landmarks, hand_label):
        """
        Returns detected gesture name as a string, or None.
        Priority order matters — specific before general.
        """

        # Pause all tracking
        if self.enabled('open_palm') and self.is_open_palm(landmarks):
            if not self.on_cooldown('open_palm'):
                self.reset_cooldown('open_palm')
                return 'open_palm'

        # Freeze cursor
        if self.enabled('fist') and self.is_fist(landmarks):
            if not self.on_cooldown('fist'):
                self.reset_cooldown('fist')
                return 'fist'

        # Toggle keyboard overlay
        if self.enabled('keyboard_toggle') and self.is_three_fingers_up(landmarks):
            if not self.on_cooldown('keyboard_toggle'):
                self.reset_cooldown('keyboard_toggle')
                return 'keyboard_toggle'

        # Double click
        if self.enabled('double_click') and self.is_double_pinch(landmarks):
            if not self.on_cooldown('double_click'):
                self.reset_cooldown('double_click')
                return 'double_click'

        # Click and drag
        if self.enabled('drag') and self.is_pinch_held(landmarks):
            return 'drag'

        # Left click
        if self.enabled('left_click') and self.is_pinch(landmarks):
            if not self.on_cooldown('left_click'):
                self.reset_cooldown('left_click')
                return 'left_click'

        # Right click
        if self.enabled('right_click') and self.is_right_click(landmarks):
            if not self.on_cooldown('right_click'):
                self.reset_cooldown('right_click')
                return 'right_click'

        # Enter key
        if self.enabled('enter') and self.is_index_held(landmarks):
            if not self.on_cooldown('enter'):
                self.reset_cooldown('enter')
                return 'enter'

        # Scroll (two fingers up — track swipe direction)
        if self.enabled('scroll_up') and self.is_two_fingers_up(landmarks):
            direction = self.get_swipe_direction(landmarks, hand_label)
            if direction == 'up':
                return 'scroll_up'
            elif direction == 'down':
                return 'scroll_down'
            else:
                # Holding position — waiting for swipe to accumulate
                return 'two_fingers_hold'

        # Desktop switch (four fingers up — track swipe direction)
        if self.enabled('switch_left') and self.is_four_fingers_up(landmarks):
            direction = self.get_swipe_direction(landmarks, hand_label)
            if direction == 'left':
                return 'switch_left'
            elif direction == 'right':
                return 'switch_right'
            else:
                # Holding position — waiting for swipe to accumulate
                return 'four_fingers_hold'

        # Cursor movement
        if self.enabled('cursor_move') and self.is_index_only(landmarks):
            return 'cursor_move'

        return None