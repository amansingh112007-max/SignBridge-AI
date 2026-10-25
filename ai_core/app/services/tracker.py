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

    @staticmethod
    def _norm_hand(lm):
        """Wrist-relative, hand-size-scaled vector. Missing hand -> zeros + flag 0."""
        if lm is None:
            return np.zeros(21 * 3, dtype=np.float32), 0.0
        wrist = lm[0]
        scale = np.mean(np.linalg.norm(lm - wrist, axis=1)) + 1e-6
        return ((lm - wrist) / scale).flatten().astype(np.float32), 1.0

    def process_frame(self, image):
        """Returns (normalized keypoints for the AI, raw landmarks for the UI overlay)."""
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.holistic.process(image_rgb)

        # Pose is the body anchor; hands: at least ONE is enough now
        if not results.pose_landmarks:
            return None, None
        lh_lm = np.array([[r.x, r.y, r.z] for r in results.left_hand_landmarks.landmark]) \
            if results.left_hand_landmarks else None
        rh_lm = np.array([[r.x, r.y, r.z] for r in results.right_hand_landmarks.landmark]) \
            if results.right_hand_landmarks else None
        if lh_lm is None and rh_lm is None:
            return None, None

        pose_lm = np.array([[r.x, r.y, r.z, r.visibility] for r in results.pose_landmarks.landmark])

        # Pose normalization: center = shoulder midpoint, scale = shoulder width
        center = (pose_lm[11, :3] + pose_lm[12, :3]) / 2.0
        scale = np.linalg.norm(pose_lm[11, :3] - pose_lm[12, :3]) + 1e-6
        pose_norm = pose_lm.copy()
        pose_norm[:, :3] = (pose_norm[:, :3] - center) / scale

        lh_vec, lh_present = self._norm_hand(lh_lm)
        rh_vec, rh_present = self._norm_hand(rh_lm)

        keypoints = np.concatenate([
            pose_norm.flatten().astype(np.float32),                   # 132
            lh_vec,                                                   # 63
            rh_vec,                                                   # 63
            np.array([lh_present, rh_present], dtype=np.float32),     # 2
        ])  # total 260

        # Raw (x, y) copies for the browser overlay; missing hand -> empty list
        display = {
            "pose": [[round(r.x, 3), round(r.y, 3)] for r in results.pose_landmarks.landmark],
            "leftHand": [[round(r.x, 3), round(r.y, 3)] for r in results.left_hand_landmarks.landmark]
                        if results.left_hand_landmarks else [],
            "rightHand": [[round(r.x, 3), round(r.y, 3)] for r in results.right_hand_landmarks.landmark]
                         if results.right_hand_landmarks else [],
        }
        return keypoints, display

    def get_keypoints(self, image):
        keypoints, _ = self.process_frame(image)
        return keypoints