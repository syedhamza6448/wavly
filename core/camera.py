import cv2

class Camera:
    def __init__(self, index=0):
        self.cap = cv2.VideoCapture(index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def read(self):
        success, frame = self.cap.read()
        if not success:
            return None
        frame = cv2.flip(frame, 1)
        return frame
    
    def release(self):
        self.cap.release()