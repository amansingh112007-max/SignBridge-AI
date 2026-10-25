import numpy as np
import torch

from app.services.model import LSTMModel, GestureModel


def test_lstm_output_shape():
    model = LSTMModel(input_size=258, hidden_size=64, num_layers=2, num_classes=29)
    x = torch.randn(4, 30, 258)      # batch=4, 30 frames, 258 keypoints
    out = model(x)
    assert out.shape == (4, 29)       # one logit per class per sample


def test_step_window_and_reset():
    gm = GestureModel()
    buffer = []
    label, conf, buffer = gm.step(buffer, np.zeros(258, dtype=np.float32))
    assert label == "None" and conf == 0.0 and len(buffer) == 1   # window not full

    for _ in range(29):
        label, conf, buffer = gm.step(buffer, np.zeros(258, dtype=np.float32))

    # 30th frame completes the window -> real label, confidence in range, buffer cleared
    assert label in gm.gesture_classes
    assert 0.0 <= conf <= 100.0
    assert buffer == []