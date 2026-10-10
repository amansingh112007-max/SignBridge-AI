import os
import json
import torch
import torch.nn as nn
import numpy as np

# Where train.py saves the finished model
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'models')


class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out


class GestureModel:
    def __init__(self):
        self.input_size = 258          # pose(132) + left hand(63) + right hand(63)
        self.hidden_size = 64
        self.num_layers = 2
        self.sequence_length = 30

        # Trained classes if we have them, otherwise the old demo words
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

        self.sequence_buffer = []

    def predict(self, keypoints):
        self.sequence_buffer.append(keypoints)
        if len(self.sequence_buffer) > self.sequence_length:
            self.sequence_buffer.pop(0)

        if len(self.sequence_buffer) == self.sequence_length:
            sequence = np.array(self.sequence_buffer)
            sequence_tensor = torch.tensor(sequence, dtype=torch.float32).unsqueeze(0)

            with torch.no_grad():
                outputs = self.model(sequence_tensor)
                probs = torch.softmax(outputs, dim=1)
                conf, predicted = torch.max(probs, 1)
                predicted_class = self.gesture_classes[predicted.item()]
                self.sequence_buffer = []
                return predicted_class, round(float(conf) * 100, 1)

        return "None", 0.0