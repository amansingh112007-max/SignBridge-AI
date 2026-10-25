import numpy as np

from app.services.tracker import KeypointTracker


def test_blank_frame_returns_none():
    tracker = KeypointTracker()
    blank = np.zeros((480, 640, 3), dtype=np.uint8)   # no person, no hands
    keypoints, display = tracker.process_frame(blank)
    assert keypoints is None
    assert display is None