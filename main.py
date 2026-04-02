import sys
import time
import cv2
import pyautogui
from PyQt6.QtWidgets import QApplication
from core.camera import Camera
from core.detector import HandDetector
from core.controller import Controller
from gestures.classifier import GestureClassifier
from keyboard.overlay import KeyboardOverlay, KEY_MAP
from keyboard.dwell import DwellManager
from utils.config_manager import ConfigManager
from ui.app import SettingsWindow
from ui.tray import TrayIcon
from ui.dashboard import DashboardWindow

app = QApplication.instance() or QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)
_screen = app.primaryScreen().size()
SCREEN_W = _screen.width()
SCREEN_H = _screen.height()

GESTURE_GUIDE = [
    ("Index finger",   "Move cursor"),
    ("Pinch",          "Left click"),
    ("Pinch + hold",   "Drag"),
    ("Double pinch",   "Double click"),
    ("Thumb + middle", "Right click"),
    ("Two fingers",    "Scroll"),
    ("Four fingers",   "Switch desktop"),
    ("Index held 1s",  "Enter key"),
    ("Three fingers",  "Toggle keyboard"),
    ("Fist",           "Freeze cursor"),
    ("Open palm",      "Pause tracking"),
    ("Pinky only",     "Toggle guide"),
]

def is_pinky_only(landmarks):
    def finger_up(tip, pip):
        return landmarks[tip]['y'] < landmarks[pip]['y']
    return (
        not finger_up(8, 6) and
        not finger_up(12, 10) and
        not finger_up(16, 14) and
        finger_up(20, 18)
    )

def draw_guide(frame, visible, paused=False):
    h, w, _ = frame.shape

    if paused:
        cv2.putText(
            frame, "TRACKING PAUSED",
            (10, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (0, 0, 255), 2
        )

    if not visible:
        cv2.putText(
            frame, "Pinky up = show guide",
            (w - 240, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5, (180, 180, 180), 1
        )
        return

    panel_w = 280
    row_h   = 22
    padding = 10
    panel_h = len(GESTURE_GUIDE) * row_h + padding * 2 + 24
    x = w - panel_w - 10
    y = 10

    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + panel_w, y + panel_h), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    cv2.rectangle(frame, (x, y), (x + panel_w, y + panel_h), (80, 80, 80), 1)

    cv2.putText(frame, "Gesture Guide",
        (x + padding, y + padding + 12),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 220), 1)
    cv2.line(frame,
        (x + padding, y + padding + 20),
        (x + panel_w - padding, y + padding + 20),
        (80, 80, 80), 1)

    for i, (gesture, action) in enumerate(GESTURE_GUIDE):
        row_y = y + padding + 24 + i * row_h + 12
        cv2.putText(frame, gesture,
            (x + padding, row_y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1)
        cv2.putText(frame, "->",
            (x + 138, row_y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (100, 100, 100), 1)
        cv2.putText(frame, action,
            (x + 158, row_y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 220, 180), 1)


def main():
    config = ConfigManager()

    camera = Camera(
        index=config.get('app', 'camera_index', default=0)
    )
    detector = HandDetector(
        max_hands=config.get('app', 'max_hands', default=2),
        detection_confidence=config.get('app', 'detection_confidence', default=0.7),
        tracking_confidence=config.get('app', 'tracking_confidence', default=0.7)
    )
    classifier = GestureClassifier(config=config)
    controller = Controller(
        screen_w=SCREEN_W,
        screen_h=SCREEN_H,
        cam_w=640,
        cam_h=480,
        config=config
    )
    keyboard = KeyboardOverlay(
        SCREEN_W, SCREEN_H,
        opacity=config.get('typing', 'keyboard_opacity', default=0.2)
    )
    # Apply saved position on startup
    keyboard.set_position(
        config.get('typing', 'keyboard_position', default='bottom')
    )

    dwell = DwellManager(
        dwell_time=config.get('typing', 'dwell_time', default=0.8)
    )
    keyboard_visible = False

    # UI
    dashboard = DashboardWindow()
    settings  = SettingsWindow(config, controller, classifier)
    tray      = TrayIcon()

    # Debug mode
    debug_mode = [False]

    # FPS tracking
    fps_counter = [0]
    fps_timer   = [time.time()]
    current_fps = [0]

    # Last gesture for dashboard
    last_gesture_label = ["None"]

    # Quit flag
    quit_requested = [False]

    # ── Signal connections ──

    def on_settings_saved():
        # Dwell time
        dwell.dwell_time = config.get('typing', 'dwell_time', default=0.8)

        # Keyboard opacity
        keyboard.opacity = config.get(
            'typing', 'keyboard_opacity', default=0.2
        )

        # Keyboard position — actually move the window
        new_position = config.get(
            'typing', 'keyboard_position', default='bottom'
        )
        keyboard.set_position(new_position)

        # Force repaint
        keyboard.update()
        keyboard.repaint()

        # Controller and classifier
        controller.update_from_config(config)
        classifier.update_from_config(config)

        tray.show_notification("Wavly", "Settings saved and applied.")
        print(
            f"Settings applied — "
            f"opacity: {keyboard.opacity}, "
            f"position: {new_position}"
        )

    def on_toggle_tracking():
        controller.toggle_tracking()
        tray.update_tracking_state(controller.tracking_paused)

    def on_toggle_keyboard():
        nonlocal keyboard_visible
        keyboard_visible = not keyboard_visible
        if keyboard_visible:
            keyboard.show()
            dwell.clear()
        else:
            keyboard.hide()
        tray.update_keyboard_state(keyboard_visible)

    def on_toggle_debug():
        debug_mode[0] = not debug_mode[0]
        if not debug_mode[0]:
            cv2.destroyAllWindows()

    def open_settings():
        settings.show()
        settings.raise_()

    def open_dashboard():
        dashboard.show()
        dashboard.raise_()

    settings.settings_saved.connect(on_settings_saved)

    dashboard.open_settings.connect(open_settings)
    dashboard.toggle_tracking.connect(on_toggle_tracking)
    dashboard.toggle_debug.connect(on_toggle_debug)

    tray.open_settings.connect(open_dashboard)
    tray.toggle_tracking.connect(on_toggle_tracking)
    tray.toggle_keyboard.connect(on_toggle_keyboard)
    tray.quit_app.connect(
        lambda: quit_requested.__setitem__(0, True)
    )

    guide_visible  = config.get('app', 'show_guide', default=True)
    guide_cooldown = 0

    # Show dashboard on launch
    dashboard.show()
    tray.show_notification(
        "Wavly", "Wavly is running. Click the tray icon to open."
    )
    print(f"Wavly started. Screen: {SCREEN_W}x{SCREEN_H}")

    try:
        while True:

            if quit_requested[0]:
                break

            frame = camera.read()
            if frame is None:
                print("Camera not found.")
                break

            frame, hands = detector.detect(frame, draw=debug_mode[0])
            now = time.time()

            # FPS calculation
            fps_counter[0] += 1
            if now - fps_timer[0] >= 1.0:
                current_fps[0] = fps_counter[0]
                fps_counter[0] = 0
                fps_timer[0]   = now

            fingertip_screen_positions = {}
            dwell_progress_map         = {}

            for hand in hands:
                label     = hand['label']
                landmarks = hand['landmarks']

                # Guide toggle — debug only
                if debug_mode[0]:
                    if is_pinky_only(landmarks) and now - guide_cooldown > 1.0:
                        guide_visible  = not guide_visible
                        guide_cooldown = now
                        config.set('app', 'show_guide', value=guide_visible)
                        continue

                gesture = classifier.classify(landmarks, label)

                if gesture:
                    last_gesture_label[0] = gesture.replace('_', ' ').title()

                # Keyboard toggle
                if gesture == 'keyboard_toggle':
                    keyboard_visible = not keyboard_visible
                    if keyboard_visible:
                        keyboard.show()
                        dwell.clear()
                    else:
                        keyboard.hide()
                    tray.update_keyboard_state(keyboard_visible)
                    continue

                # Keyboard visible — typing mode
                if keyboard_visible:
                    # Read fingertips fresh from config every frame
                    TYPING_FINGERTIPS = config.get(
                        'typing', 'fingertips', default=[8]
                    )
                    for fid in TYPING_FINGERTIPS:
                        tip      = landmarks[fid]
                        screen_x, screen_y = controller.map_to_screen(
                            tip['x'], tip['y']
                        )
                        fingertip_screen_positions[fid] = (screen_x, screen_y)

                        local_x   = screen_x
                        local_y   = screen_y - keyboard._kb_y_offset
                        key_label = keyboard.get_key_at(local_x, local_y)

                        fired_key = dwell.update(fid, key_label)
                        progress  = dwell.get_progress(fid)

                        if key_label:
                            dwell_progress_map[fid] = (key_label, progress)

                        if fired_key:
                            key_to_press = KEY_MAP.get(
                                fired_key, fired_key.lower()
                            )
                            pyautogui.press(key_to_press)
                            last_gesture_label[0] = f"Typed: {fired_key}"
                            print(f"Typed: {fired_key}")

                    keyboard.update_fingertips(
                        fingertip_screen_positions,
                        dwell_progress_map
                    )
                    app.processEvents()
                    continue

                # Normal gesture control
                if not gesture:
                    controller.stop_drag()
                    continue

                if gesture == 'cursor_move':
                    controller.move_cursor(landmarks[8])
                elif gesture == 'left_click':
                    controller.left_click()
                elif gesture == 'right_click':
                    controller.right_click()
                elif gesture == 'double_click':
                    controller.double_click()
                elif gesture == 'drag':
                    controller.move_cursor(landmarks[8])
                    controller.start_drag()
                elif gesture == 'scroll_up':
                    controller.scroll('up')
                elif gesture == 'scroll_down':
                    controller.scroll('down')
                elif gesture == 'switch_left':
                    controller.switch_desktop('left')
                elif gesture == 'switch_right':
                    controller.switch_desktop('right')
                elif gesture == 'enter':
                    controller.press_enter()
                elif gesture == 'fist':
                    controller.stop_drag()
                elif gesture == 'open_palm':
                    controller.toggle_tracking()
                    tray.update_tracking_state(controller.tracking_paused)

            # Update dashboard every frame
            dashboard.update_status(
                tracking     = not controller.tracking_paused,
                hands        = len(hands),
                last_gesture = last_gesture_label[0],
                fps          = current_fps[0]
            )

            # Debug camera window
            if debug_mode[0]:
                draw_guide(frame, guide_visible, controller.tracking_paused)
                if keyboard_visible:
                    cv2.putText(
                        frame,
                        "KEYBOARD ON — Three fingers to hide",
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 220, 180), 2
                    )
                cv2.putText(
                    frame,
                    f"Hands: {len(hands)}  FPS: {current_fps[0]}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (0, 255, 0), 2
                )
                cv2.imshow("Wavly - Debug", frame)

            app.processEvents()

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                settings.show()
                settings.raise_()

    except KeyboardInterrupt:
        print("\nWavly stopped.")

    finally:
        controller.stop_drag()
        keyboard.hide()
        settings.hide()
        dashboard.hide()
        tray.hide()
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()