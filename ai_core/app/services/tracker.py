import cv2
import mediapipe as mp
import numpy as np

class KeypointTracker:
    def __init__(self):
        # Initialize MediaPipe Holistic model
        self.mp_holistic = mp.solutions.holistic
        self.holistic = self.mp_holistic.Holistic(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def get_keypoints(self, image):
        # MediaPipe expects RGB images, but OpenCV uses BGR
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image to find landmarks
        results = self.holistic.process(image_rgb)
        
        # Check if we found all necessary landmarks
        if (results.pose_landmarks and results.left_hand_landmarks and 
            results.right_hand_landmarks and results.face_landmarks):
            
            # Extract coordinates and flatten them into a 1D array
            pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten()
            lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten()
            rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten()
            face = np.array([[res.x, res.y, res.z] for res in results.face_landmarks.landmark]).flatten()
            
            # Combine all keypoints (Total: 1662 points)
            all_keypoints = np.concatenate([pose, lh, rh, face])
            return all_keypoints
            
        return None