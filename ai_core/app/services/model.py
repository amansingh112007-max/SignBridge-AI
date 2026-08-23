import torch
import torch.nn as nn
import numpy as np

# Define the LSTM Neural Network Architecture
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
        out = self.fc(out[:, -1, :]) # Take the output of the last time step
        return out

class GestureModel:
    def __init__(self):
        self.input_size = 1662 # Matches our tracker output
        self.hidden_size = 64
        self.num_layers = 2
        self.num_classes = 10 # Example: 10 different gestures
        self.sequence_length = 30 # Look at the last 30 frames to make a decision
        
        # Initialize the model
        self.model = LSTMModel(self.input_size, self.hidden_size, self.num_layers, self.num_classes)
        self.model.eval() # Set to evaluation mode
        
        # Buffer to hold the sequence of frames
        self.sequence_buffer = []
        
        # Mapping of model output to actual words
        self.gesture_classes = ["Hello", "Thank You", "Yes", "No", "Please", 
                                "Help", "Water", "Food", "Bathroom", "None"]

    def predict(self, keypoints):
        # Add current frame to our buffer
        self.sequence_buffer.append(keypoints)
        
        # Keep the buffer size limited to our sequence length
        if len(self.sequence_buffer) > self.sequence_length:
            self.sequence_buffer.pop(0)
            
        # Only predict when we have a full sequence
        if len(self.sequence_buffer) == self.sequence_length:
            sequence = np.array(self.sequence_buffer)
            sequence_tensor = torch.tensor(sequence, dtype=torch.float32).unsqueeze(0)
            
            with torch.no_grad():
                outputs = self.model(sequence_tensor)
                _, predicted = torch.max(outputs, 1)
                predicted_class = self.gesture_classes[predicted.item()]
                
                # Clear buffer so we don't repeat the same word instantly
                self.sequence_buffer = []
                return predicted_class
                
        return "None"