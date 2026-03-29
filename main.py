import cv2
from core.camera import Camera
from core.detector import HandDetector

def main():
    camera = Camera(index=0)
    detector = HandDetector(max_hands=2)

    print("Wavly starting... Press Q to quit.")

    while True:
        frame = camera.read()
        if frame is None:
            print("Camera not found.")
            break

        frame, hands = detector.detect(frame, draw=True)

        cv2.putText(
            frame,
            f"Hands: {len(hands)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        for hand in hands:
            label = hand['label']
            index_tip = hand['landmarks'][8]
            thumb_tip = hand['landmarks'][4]
            print(f"{label} hand - Index tip: {index_tip}, Thumb tip: {thumb_tip}")

        cv2.imshow("Wavly - Hand Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()