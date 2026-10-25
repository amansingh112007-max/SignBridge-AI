import numpy as np
import torch

from app.services.model import LSTMModel, GestureModel

D = 260   # current keypoint dimension


def test_lstm_output_shape():
    model = LSTMModel(input_size=D, hidden_size=64, num_layers=2, num_classes=29)
    x = torch.randn(4, 30, D)
    out = model(x)
    assert out.shape == (4, 29)


def test_step_window_and_reset():
    gm = GestureModel()
    buffer = []
    label, conf, buffer = gm.step(buffer, np.zeros(D, dtype=np.float32))
    assert label == "None" and conf == 0.0 and len(buffer) == 1

    for _ in range(29):
        label, conf, buffer = gm.step(buffer, np.zeros(D, dtype=np.float32))

    assert label in gm.gesture_classes
    assert 0.0 <= conf <= 100.0
    assert buffer == []