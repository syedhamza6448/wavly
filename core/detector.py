import cv2
import mediapipe as mp
from utils.config_manager import resource_path

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

class HandDetector:
    def __init__(self, max_hands=2, detection_confidence=0.7, tracking_confidence=0.7):
        model_path = resource_path('assets/hand_landmarker.task')
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.IMAGE,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_confidence,
            min_hand_presence_confidence=tracking_confidence,
        )
        self.detector = HandLandmarker.create_from_options(options)

    def detect(self, frame, draw=True):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        detection_result = self.detector.detect(mp_image)

        all_hands = []
        h, w, _ = frame.shape

        for i, hand_landmarks in enumerate(detection_result.hand_landmarks):
            landmarks = []
            for lm in hand_landmarks:
                landmarks.append({
                    'x': int(lm.x * w),
                    'y': int(lm.y * h),
                    'z': lm.z
                })

            hand_label = detection_result.handedness[i][0].display_name

            all_hands.append({
                'landmarks': landmarks,
                'label': hand_label
            })

            if draw:
                for lm in landmarks:
                    cv2.circle(frame, (lm['x'], lm['y']), 5, (0, 255, 0), -1)
                connections = [
                    (0,1),(1,2),(2,3),(3,4),
                    (0,5),(5,6),(6,7),(7,8),
                    (0,9),(9,10),(10,11),(11,12),
                    (0,13),(13,14),(14,15),(15,16),
                    (0,17),(17,18),(18,19),(19,20),
                    (5,9),(9,13),(13,17)
                ]
                for start, end in connections:
                    cv2.line(
                        frame,
                        (landmarks[start]['x'], landmarks[start]['y']),
                        (landmarks[end]['x'], landmarks[end]['y']),
                        (0, 200, 200), 2
                    )

        return frame, all_hands