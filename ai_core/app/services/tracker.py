import cv2
import mediapipe as mp
import numpy as np

class KeypointTracker:
    def __init__(self):
        self.mp_holistic = mp.solutions.holistic
        self.holistic = self.mp_holistic.Holistic(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def process_frame(self, image):
        """Returns (flat keypoints for the AI, display landmarks for the UI overlay)."""
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.holistic.process(image_rgb)

        # Require pose + both hands. Face is optional (dataset images often crop it).
        if not (results.pose_landmarks and results.left_hand_landmarks
                and results.right_hand_landmarks):
            return None, None

        # 258-value vector: pose(33*4) + left hand(21*3) + right hand(21*3)
        pose = np.array([[r.x, r.y, r.z, r.visibility] for r in results.pose_landmarks.landmark]).flatten()
        lh = np.array([[r.x, r.y, r.z] for r in results.left_hand_landmarks.landmark]).flatten()
        rh = np.array([[r.x, r.y, r.z] for r in results.right_hand_landmarks.landmark]).flatten()
        keypoints = np.concatenate([pose, lh, rh])

        # Tiny (x, y) copy so the browser can draw the skeleton preview
        display = {
            "pose": [[round(r.x, 3), round(r.y, 3)] for r in results.pose_landmarks.landmark],
            "leftHand": [[round(r.x, 3), round(r.y, 3)] for r in results.left_hand_landmarks.landmark],
            "rightHand": [[round(r.x, 3), round(r.y, 3)] for r in results.right_hand_landmarks.landmark],
        }
        return keypoints, display

    def get_keypoints(self, image):
        # Kept so the Part-1 test script still works
        keypoints, _ = self.process_frame(image)
        return keypoints