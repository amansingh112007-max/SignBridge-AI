<div align="center">

# 🤟 SignBridge AI

### Real-Time Sign Language to Speech Translator

**Empowering 466M+ deaf and hard-of-hearing individuals with instant, on-device gesture-to-speech translation — turning silence into conversation, anywhere.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
![Build](https://img.shields.io/badge/build-passing-brightgreen)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-orange.svg)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [How It Works](#-how-it-works-the-pipeline)
- [Tech Stack](#️-tech-stack)
- [Project Structure](#-project-structure)
- [Local Setup & Installation](#️-local-setup--installation)
- [Docker Deployment](#️-docker-deployment-recommended)
- [App & Web Interfaces](#-app--web-interfaces)
- [Privacy & Ethics](#-privacy--ethics)
- [Roadmap](#️-roadmap)
- [Contributing](#-contributing)
- [Acknowledgments](#-acknowledgments)
- [License](#-license)

---

## 🚀 Overview

SignBridge AI bridges the communication gap faced by the deaf and mute community. Traditional human interpreters are costly and rarely available on-demand. SignBridge AI turns any standard webcam or smartphone camera into an instant sign language interpreter using skeletal tracking and sequential deep learning — fully on-device, with zero raw video ever stored.

| | |
|---|---|
| 🤖 **Computer Vision** | MediaPipe Holistic + OpenCV |
| ⚡ **Low Latency** | Sub-100ms gesture recognition pipeline |
| 🔒 **Privacy-First** | Zero video frames stored or transmitted |
| 🌍 **Multilingual** | Hindi, English, and regional language voice output |

---

## 🧠 How It Works (The Pipeline)

```
📷 Camera Feed → 🦴 Keypoint Tracking → 🧠 LSTM Model → 🗣️ Text-to-Speech
```

1. **Keypoint Tracking** (`ai_core/services/tracker.py`)
   Uses OpenCV and MediaPipe Holistic to extract 3D skeletal joints (hands, face, pose) frame-by-frame — no raw pixels are retained.

2. **Sequential AI Model** (`ai_core/services/model.py`)
   A custom PyTorch LSTM ingests the sequence of keypoints over time, recognizing the fluid shape of a gesture rather than a single static pose.

3. **Multilingual Voice Output** (`ai_core/services/voice.py`)
   Translates the recognized gesture into text and synthesizes spoken audio in Hindi, English, or regional languages.

> **Note:** Latency and accuracy figures depend on hardware (CPU vs GPU inference) and camera FPS. See [`docs/benchmarks.md`](docs/benchmarks.md) for methodology *(add this doc to back your performance claims)*.

---

## ⚙️ Tech Stack

**AI & Backend**
- Language: Python 3.10+
- Computer Vision: OpenCV, MediaPipe Holistic
- Deep Learning: PyTorch (LSTM architecture)
- API Layer: FastAPI + WebSockets (real-time streaming)
- Voice: gTTS / pyttsx3

**Web App**
- Framework: React 18 + Vite
- Streaming: Native WebSocket API
- Styling: Tailwind CSS

**Mobile App**
- Framework: React Native + Expo
- Camera: `react-native-vision-camera` (high-FPS frame processing)
- Offline Inference: TensorFlow Lite

---

## 📂 Project Structure

```
SignBridge-AI/
├── ai_core/
│   ├── app/                # FastAPI entrypoint
│   └── services/
│       ├── tracker.py      # MediaPipe keypoint extraction
│       ├── model.py        # PyTorch LSTM inference
│       └── voice.py        # TTS synthesis
├── web_app/                # React + Vite frontend
├── mobile_app/              # React Native + Expo app
├── docker-compose.yml
└── README.md
```

---

## 🛠️ Local Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Webcam or smartphone camera

### 1. AI Core Backend

```bash
cd ai_core
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Web App

```bash
cd web_app
npm install
npm run dev
```

Visit **http://localhost:5173** to access the web interface.

### 3. Mobile App

```bash
cd mobile_app
npm install
npx expo start
```

Scan the QR code with the **Expo Go** app on your phone.

---

## ☁️ Docker Deployment (Recommended)

Spin up the entire stack (Backend API + Web Frontend) with a single command:

```bash
git clone https://github.com/amansingh112007-max/SignBridge-AI.git
cd SignBridge-AI

docker-compose up --build
```

| Service | URL |
|---|---|
| Web App | http://localhost:80 |
| API Docs (Swagger) | http://localhost:8000/docs |

---

## 📱 App & Web Interfaces

**Web Interface**
- ⚡ One-click webcam access
- 💬 Real-time translated text overlay on video feed
- ♿ Accessibility controls — high contrast mode, large text

**Mobile Interface**
- 📴 On-device processing via TensorFlow Lite for offline use
- 🔔 Background translation while app is minimized

---

## 🔒 Privacy & Ethics

1. **Zero Raw Storage** — Raw video frames are never stored or transmitted.
2. **Skeletal Abstraction** — The model only ever sees mathematical (x, y, z) joint coordinates; a face or identity cannot be reconstructed from this data.
3. **On-Device Fallback** — The LSTM model can run entirely on-device via TFLite for absolute offline privacy.

---

## 🗺️ Roadmap

- [ ] Expand gesture vocabulary beyond current dataset
- [ ] Add support for additional regional sign languages
- [ ] Benchmark suite with published latency/accuracy numbers
- [ ] Two-way translation (speech → sign avatar)

---

## 🤝 Contributing

We welcome contributions from developers, sign language experts, and accessibility advocates!

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/AudioImprovements`
3. Commit your changes: `git commit -m 'Added multilingual TTS caching'`
4. Push to the branch: `git push origin feature/AudioImprovements`
5. Open a Pull Request

---

## 🙏 Acknowledgments

- [MediaPipe](https://github.com/google/mediapipe) — Holistic pose/hand/face tracking
- [PyTorch](https://pytorch.org/) — LSTM model training and inference
- Sign language datasets and consultants who made this project possible *(credit specific sources here)*

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

<div align="center">

*"Bridging human connection — turning silent signs into spoken words, instantly."*

</div>