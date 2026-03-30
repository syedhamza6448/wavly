import math
import time

class GestureClassifier:
    def __init__(self):
        self.last_gesture_time = {}
        self.cooldown = 0.5
        
        self.swipe_start = {}
        self.swipe_threshold = 80
        
        self.gesture_start_time = {}
        
        self.last_pinch_time = 0
        self.double_pinch_window = 0.4
        
    def distance(self, p1, p2):
        """Euclidean distance between two landmarks."""
        return math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)
    
    def is_finger_up(self, landmarks, finger_tip, finger_pip):
        """
        Return True if a finger is extended (pointing up).
        Compares tip y position to PIP joint y position.
        Lower y = higher on screen.
        """
        return landmarks[finger_tip]['y'] < landmarks[finger_pip]['y']
    
    def get_extended_fingers(self, landmarks):
        """
        Returns a list of booleans [thumb, index, middle, ring, pinky].
        True = finger is extended/up.
        """
        fingers = []
        
        if landmarks[4]['x'] < landmarks[3]['x']:
            fingers.append(True)
        else:
            fingers.append(False)
            
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        for tip, pip in zip(tips, pips):
            fingers.append(self.is_finger_up(landmarks, tip, pip))
            
        return fingers
    
    def on_cooldown(self, gesture_name):
        """Returns True if gesture is still in cooldown period."""
        now = time.time()
        last = self.last_gesture_time.get(gesture_name, 0)
        return (now - last) < self.cooldown
    
    def reset_cooldown(self, gesture_name):
        """Marks a gesture as just fired."""
        self.last_gesture_time[gesture_name] = time.time()
        
        
    #GESTURE DETECTION METHODS
    
    def is_pinch(self, landmarks, threshold=40):
        """
        Thumb tip (4) and index tip (8) are close together.
        """
        
        return self.distance(landmarks[4], landmarks[8]) < threshold
    
    def is_right_click(self, landmarks, threshold=40):
        """
        Thumb tip (4) and middle tip (12) are close together.
        """
        return self.distance(landmarks[4], landmarks[12]) < threshold
    
    def is_fist(self, landmarks):
        """
        All your fingers are down (not extended).
        """
        fingers = self.get_extended_fingers(landmarks)
        return not any(fingers[1:])
    
    def is_open_palm(self, landmarks):
        """
        All five fingers are extended.
        """
        fingers = self.get_extended_fingers(landmarks)
        return all(fingers)
    
    def is_three_fingers_up(self, landmarks):
        """
        Index, middle, and ring are up. Thumb and pinky are down.
        Used to toggle the keyboard overlay.
        """
        fingers = self.get_extended_fingers(landmarks)
        return (
            not fingers[0] and
            fingers[1] and
            fingers[2] and
            fingers[3] and
            not fingers[4]
        )
        
    def is_two_fingers_up(self, landmarks):
        """
        Index and middle are up. Others are down.
        Used for scrolling.
        """
        fingers = self.get_extended_fingers(landmarks)
        return (
            fingers[1] and
            fingers[2] and
            not fingers[3] and
            not fingers[4]
        )
        
    def is_four_fingers_up(self, landmarks):
        """
        Index, middle, ring, pinky are up. Thumb down.
        Used for desktop switch / ALt+Tab.
        """
        fingers = self.get_extended_fingers(landmarks)
        return (
            not fingers[0] and
            fingers[1] and
            fingers[2] and
            fingers[3] and
            fingers[4]
        )
        
    def is_index_only(self, landmarks):
        """
        Only index finger is up. Used for cursor movement.
        """
        fingers = self.get_extended_fingers(landmarks)
        return (
            fingers[1] and 
            not fingers[2] and
            not fingers[3] and
            not fingers[4]
        )
        
    def is_index_held(self, landmarks, duration=1.0):
        """
        Index finger held up for a set duration.
        Used to trigger Enter key.
        """
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
        
    def is_pinch_held(self, landmarks, duration=0.5):
        """
        Pinch held for a set duration.
        Used for click and drag.
        """
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
        """
        Two quick pinches in succession within 0.4 seconds.
        Used for double click.
        """
        if self.is_pinch(landmarks):
            now = time.time()
            if now - self.last_pinch_time < self.double_pinch_window:
                self.last_pinch_time = 0
                return True
            self.last_pinch_time = now
        return False
    
    def get_swipe_direction(self, landmarks, hand_label):
        """
        Detects swipe left OR right using index fingertip movement.
        Returns 'left', 'right', 'up', 'down', or None.
        """
        tip = landmarks[8]
        key = f'swipe_{hand_label}'
        
        if key not in self.swipe_start:
            self.swipe_start[key] = {'x': tip['x'], 'y': tip['y']}
            return None
        
        dx = tip['x'] - self.swipe_start[key]['x']
        dy = tip['y'] - self.swipe_start[key]['y']
        
        if abs(dx) > self.swipe_threshold:
            self.swipe_start.pop(key, None)
            return 'down' if dy > 0 else 'up'
        
        return None
    
    #MAIN CLASSIFY METHOD
    
    def classify(self, landmarks, hand_label):
        """
        Takes landmarks and hand label, returns the detected gesture name as a string, or None if no gesture is detected.
        """
        
        if self.is_open_palm(landmarks):
            if not self.on_cooldown('open_palm'):
                self.reset_cooldown('open_palm')
                return 'open_palm'
            
        if self.is_fist(landmarks):
            if not self.on_cooldown('keyboard_toggle'):
                self.reset_cooldown('keyboard_toggle')
                return 'keyboard_toggle'
            
        if self.is_double_pinch(landmarks):
            if not self.on_cooldown('double_click'):
                self.reset_cooldown('double_click')
                return 'double_click'
            
        if self.is_pinch_held(landmarks):
            return 'drag'
        
        
        if self.is_pinch(landmarks):
            if not self.on_cooldown('left_click'):
                self.reset_cooldown('left_click')
                return 'left_click'
            
        if self.is_right_click(landmarks):
            if not self.on_cooldown('right_click'):
                self.reset_cooldown('right_click')
                return 'right_click'
            
        if self.is_index_held(landmarks):
            if not self.on_cooldown('enter'):
                self.reset_cooldown('enter')
                return 'enter'
            
        if self.is_two_fingers_up(landmarks):
            direction = self.get_swipe_direction(landmarks, hand_label)
            if direction in ('up', 'down'):
                return f'scroll_{direction}'
            
        if self.is_four_fingers_up(landmarks):
            direction = self.get_swipe_direction(landmarks, hand_label)
            if direction in ('left', 'right'):
                return f'switch_{direction}'
            
        if self.is_index_only(landmarks):
            return 'cursor_move'
        
        return None
        
        
        
        
        
        
        
        
        
        
        
        
        
         