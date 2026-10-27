import os
import json
import torch
import torch.nn as nn
import numpy as np

# Where train.py saves the finished model
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'models')


class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        out, _ = self.lstm(x, (h0, c0))
        return self.fc(out[:, -1, :])


class GestureModel: 
    """Stateless per connection: sequence buffers live in the caller (session)."""

    def __init__(self):
        self.input_size = 260          # pose(132) + hands(126) + 2 hand-presence flags
        self.hidden_size = 64
        self.num_layers = 2
        self.sequence_length = 30

        classes_path = os.path.join(MODELS_DIR, 'classes.json')
        if os.path.exists(classes_path):
            with open(classes_path) as f:
                self.gesture_classes = json.load(f)
        else:
            self.gesture_classes = ["Hello", "Thank You", "Yes", "No", "Please",
                                    "Help", "Water", "Food", "Bathroom", "None"]

        self.model = LSTMModel(self.input_size, self.hidden_size,
                               self.num_layers, len(self.gesture_classes))

        weights_path = os.path.join(MODELS_DIR, 'signbridge_lstm.pth')
        if os.path.exists(weights_path):
            self.model.load_state_dict(torch.load(weights_path, map_location='cpu'))
            print(f'🧠 Loaded TRAINED weights ({len(self.gesture_classes)} classes)')
        else:
            print('⚠️ No trained weights found - running with random init')
        self.model.eval()

    def step(self, buffer, keypoints):
        """Feed one frame; returns (gesture, confidence, new_buffer)."""
        buffer = buffer + [keypoints]
        if len(buffer) > self.sequence_length:
            buffer = buffer[-self.sequence_length:]

        if len(buffer) == self.sequence_length:
            seq = torch.tensor(np.array(buffer), dtype=torch.float32).unsqueeze(0)
            with torch.no_grad():
                probs = torch.softmax(self.model(seq), dim=1)
                conf, pred = torch.max(probs, 1)
            label = self.gesture_classes[pred.item()]
            return label, round(float(conf) * 100, 1), []   # window consumed
        return "None", 0.0, buffer