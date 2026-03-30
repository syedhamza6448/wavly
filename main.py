import time
import cv2
from core.camera import Camera
from core.detector import HandDetector
from core.controller import Controller
from gestures.classifier import GestureClassifier

try:
    from PyQt6.QtWidgets import QApplication
    import sys
    _app = QApplication.instance() or QApplication(sys.argv)
    _screen = _app.primaryScreen().size()
    SCREEN_W = _screen.width()
    SCREEN_H = _screen.height()
except Exception:
    import pyautogui
    SCREEN_W, SCREEN_H = pyautogui.size()

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
    ("Pinky only",     "Toggle this guide"),
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

    # Paused banner
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
    row_h = 22
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
    camera = Camera(index=0)
    detector = HandDetector(max_hands=2)
    classifier = GestureClassifier()
    controller = Controller(
        screen_w=SCREEN_W,
        screen_h=SCREEN_H,
        cam_w=640,
        cam_h=480
    )

    guide_visible = True
    guide_cooldown = 0

    print(f"Wavly starting... Screen: {SCREEN_W}x{SCREEN_H} | Press Q to quit.")

    try:
        while True:
            frame = camera.read()
            if frame is None:
                print("Camera not found.")
                break

            frame, hands = detector.detect(frame, draw=True)
            now = time.time()

            for hand in hands:
                label = hand['label']
                landmarks = hand['landmarks']

                # Guide toggle — pinky only
                if is_pinky_only(landmarks) and now - guide_cooldown > 1.0:
                    guide_visible = not guide_visible
                    guide_cooldown = now
                    continue

                gesture = classifier.classify(landmarks, label)

                if not gesture:
                    # Release drag if no gesture detected
                    controller.stop_drag()
                    continue

                print(f"{label}: {gesture}")

                cv2.putText(
                    frame,
                    f"{label}: {gesture}",
                    (10, 60 if label == 'Right' else 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (255, 255, 0), 2
                )

                # Wire gestures to controller actions
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
                    # Fist freezes cursor — do nothing
                    controller.stop_drag()

                elif gesture == 'open_palm':
                    controller.toggle_tracking()

                elif gesture == 'keyboard_toggle':
                    # Placeholder — wired in Phase 4
                    print("Keyboard overlay coming in Phase 4")

            cv2.putText(
                frame,
                f"Hands: {len(hands)}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 0), 2
            )

            draw_guide(frame, guide_visible, controller.tracking_paused)

            cv2.imshow("Wavly - Gesture Control", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nWavly stopped.")

    finally:
        controller.stop_drag()
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()