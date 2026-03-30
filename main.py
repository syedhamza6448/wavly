import cv2
from core.camera import Camera
from core.detector import HandDetector
from gestures.classifier import GestureClassifier

# All gestures and their descriptions
GESTURE_GUIDE = [
    ("Index finger",     "Move cursor"),
    ("Pinch",            "Left click"),
    ("Pinch + hold",     "Drag"),
    ("Double pinch",     "Double click"),
    ("Thumb + middle",   "Right click"),
    ("Two fingers",      "Scroll"),
    ("Four fingers",     "Switch desktop"),
    ("Index held 1s",    "Enter key"),
    ("Three fingers",    "Toggle keyboard"),
    ("Fist",             "Freeze cursor"),
    ("Open palm",        "Pause tracking"),
    ("Pinky only",       "Toggle this guide"),
]

def is_pinky_only(landmarks):
    """Only pinky finger is up — used to toggle the guide."""
    def finger_up(tip, pip):
        return landmarks[tip]['y'] < landmarks[pip]['y']
    return (
        not finger_up(8, 6) and    # index down
        not finger_up(12, 10) and  # middle down
        not finger_up(16, 14) and  # ring down
        finger_up(20, 18)          # pinky up
    )

def draw_guide(frame, visible):
    """Draws the gesture guide panel on the top-right of the frame."""
    if not visible:
        # Draw a small hint so user knows the guide is hidden
        h, w, _ = frame.shape
        cv2.putText(
            frame,
            "Pinky up = show guide",
            (w - 240, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (180, 180, 180),
            1
        )
        return

    h, w, _ = frame.shape

    panel_w = 280
    row_h = 22
    padding = 10
    panel_h = len(GESTURE_GUIDE) * row_h + padding * 2 + 24
    x = w - panel_w - 10
    y = 10

    # Semi-transparent dark background
    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + panel_w, y + panel_h), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    # Panel border
    cv2.rectangle(frame, (x, y), (x + panel_w, y + panel_h), (80, 80, 80), 1)

    # Title
    cv2.putText(
        frame,
        "Gesture Guide",
        (x + padding, y + padding + 12),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 220, 220),
        1
    )

    # Divider line
    cv2.line(
        frame,
        (x + padding, y + padding + 20),
        (x + panel_w - padding, y + padding + 20),
        (80, 80, 80), 1
    )

    # Each gesture row
    for i, (gesture, action) in enumerate(GESTURE_GUIDE):
        row_y = y + padding + 24 + i * row_h + 12
        # Gesture name (left, dim white)
        cv2.putText(
            frame,
            gesture,
            (x + padding, row_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (200, 200, 200),
            1
        )
        # Arrow
        cv2.putText(
            frame,
            "->",
            (x + 138, row_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (100, 100, 100),
            1
        )
        # Action (right, cyan)
        cv2.putText(
            frame,
            action,
            (x + 158, row_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (0, 220, 180),
            1
        )

def main():
    camera = Camera(index=0)
    detector = HandDetector(max_hands=2)
    classifier = GestureClassifier()

    guide_visible = True
    guide_cooldown = 0

    print("Wavly starting... Press Q to quit.")

    try:
        while True:
            frame = camera.read()
            if frame is None:
                print("Camera not found.")
                break

            frame, hands = detector.detect(frame, draw=True)

            import time
            now = time.time()

            for hand in hands:
                label = hand['label']
                landmarks = hand['landmarks']

                # Check pinky toggle (independent of classifier)
                if is_pinky_only(landmarks) and now - guide_cooldown > 1.0:
                    guide_visible = not guide_visible
                    guide_cooldown = now

                gesture = classifier.classify(landmarks, label)

                if gesture:
                    print(f"{label} hand — Gesture: {gesture}")
                    cv2.putText(
                        frame,
                        f"{label}: {gesture}",
                        (10, 60 if label == 'Right' else 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (255, 255, 0),
                        2
                    )

            cv2.putText(
                frame,
                f"Hands: {len(hands)}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            draw_guide(frame, guide_visible)

            cv2.imshow("Wavly - Gesture Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nWavly stopped.")

    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()