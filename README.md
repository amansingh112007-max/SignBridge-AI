                                  SignBridge AI
                       Real-Time Sign Language to Speech Translator
   🤖 Computer Vision    ⚡ <100ms Latency    🔒 Zero Video Stored    🌍Hindi & English


Empowering 466M+ deaf and mute individuals with instant, on-device gesture-to-speech translation — turning silence into conversation, anywhere, in real time.

📖 Table of Contents
🚀 Overview
🧠 How It Works (The Pipeline)
⚙️ Tech Stack
🛠️ Local Setup & Installation
☁️ Docker Deployment (Recommended)
📱 App & Web Interfaces
🔒 Privacy & Ethics
🤝 Contributing
📜 License

🚀 Overview
SignBridge AI bridges the massive communication gap faced by the deaf and mute community. Traditional human interpreters are costly and rarely available on-demand. SignBridge AI turns any standard webcam or smartphone camera into an instant, highly accurate sign language interpreter using advanced skeletal tracking and sequential deep learning.

🧠 How It Works (The Pipeline)
Our end-to-end pipeline processes gestures in under 100 milliseconds, fully on-device. We never store raw video feeds, ensuring absolute user privacy.

1. Keypoint Tracking (ai_core/services/tracker.py): Uses OpenCV and MediaPipe to extract 500+ 3D skeletal joints (hands, face, pose) frame-by-frame.

2. Sequential AI Model (ai_core/services/model.py): A custom PyTorch LSTM (Long Short-Term Memory) neural network ingests the sequence of keypoints over time, recognizing the fluid shape of the gesture rather than static poses.
3. Multilingual Voice Output (ai_core/services/voice.py): Translates the recognized gesture into text and instantly synthesizes spoken audio in Hindi, English, or regional languages.

⚙️ Tech Stack
AI & Backend
-> Language: Python 3.10+
-> Computer Vision: OpenCV, MediaPipe Holistic
-> Deep Learning: PyTorch (LSTM Architecture)
-> API Layer: FastAPI + WebSockets (Crucial for real-time video streaming)
-> Voice: gTTS / pyttsx3

Web App
-> Framework: React 18 + Vite
-> Streaming: Native WebSocket API
-> Styling: Tailwind CSS

Mobile App
-> Framework: React Native + Expo
-> Camera: react-native-vision-camera (for high FPS frame processing)

  🛠️ Local Setup & Installation
Prerequisites
  ->Python 3.10+
  ->Node.js 18+
  ->Webcam or smartphone camera
1. Setup AI Core Backend
cd ai_corepython -m venv venvsource venv/bin/activate  # On Windows: venv\Scripts\activate# Install dependenciespip install -r requirements.txt# Run the FastAPI serveruvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
2. Setup Web App
bash

cd web_app
npm install
npm run dev
Visit http://localhost:5173 to access the web interface.

3. Setup Mobile App
bash

cd mobile_app
npm install
npx expo start
Download the Expo Go app on your phone and scan the QR code.

☁️ Docker Deployment (Recommended)
To spin up the entire stack (Backend API + Web Frontend) with a single command:

bash

# Clone the repo
git clone https://github.com/amansingh112007-max/SignBridge-AI.git
cd SignBridge-AI

# Build and run
docker-compose up --build
Access the web app at http://localhost:80 and the API docs at http://localhost:8000/docs.

📱 App & Web Interfaces
Web Interface
1. One-Click Start: Grants browser webcam access instantly.
2. Real-Time Overlay: Translated text floats over the video feed.
3. Accessibility Controls: High contrast mode, large text options.

Mobile Interface
1. On-Device Processing Option: Can be configured to run the LSTM model locally via TensorFlow Lite for offline use.
2. Background Translation: Minimizes the app while continuing to translate signs via voice.

🔒 Privacy & Ethics
1. Zero Raw Storage: We do NOT store or transmit raw video frames.
2. Skeletal Abstraction: The AI only sees mathematical coordinates (x, y, z) of body joints. It is impossible to reconstruct a person's face or identity from this data.
3. On-Device Fallback: The architecture supports moving the LSTM model directly to the smartphone via TFLite for absolute offline privacy.

🤝 Contributing
We welcome contributions from developers, sign language experts, and accessibility advocates!

1. Fork the repository.
2. Create your feature branch (git checkout -b feature/AudioImprovements).
3. Commit your changes (git commit -m 'Added multilingual TTS caching').
4. Push to the branch (git push origin feature/AudioImprovements).
5. Open a Pull Request.

📜 License
Distributed under the MIT License. See LICENSE for more information.

"Bridging human connection — turning silent signs into spoken words, instantly."

