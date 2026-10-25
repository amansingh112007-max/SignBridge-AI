# 🤟 SignBridge AI

**Real-time sign-language → speech web prototype (ASL alphabet).**

![CI](https://github.com/amansingh112007-max/SignBridge-AI/actions/workflows/ci.yml/badge.svg)

> **Honest status (Oct 2026):** working full-stack web prototype that recognizes
> **ASL alphabet letters** from a live webcam. Latest held-out validation accuracy:
> **__%** (fill in from your last training run).
> Mobile app, Docker-Compose stack, and ISL word vocabulary are **planned — see Roadmap**.
> This README describes only what exists today.

## What it does (today)
- Live webcam → MediaPipe Holistic keypoints (543 landmarks/frame) → 2-layer LSTM → letter prediction
- Real-time captions with **confidence %** and temporal smoothing (no flicker-words)
- Glowing **skeleton overlay** (pose + both hands) in the browser
- Session transcript, English/हिंदी caption modes, browser on-device speech (Web Speech API)
- Accessibility: large-text and high-contrast modes
- Privacy: frames are processed in RAM and **never stored**; no uploads, no accounts

## What it is not (yet)
- Not a word/phrase translator — letters only (ASL alphabet, 26 classes + symbols)
- Not multi-signer validated — trained on a single-signer Kaggle dataset
- Not on-device inference — frames stream over WebSocket to a **local** backend
- Not mobile, not a distributed multi-user service (per-session state exists, but no scaling work)

## Architecture
browser (React + Vite + Tailwind)
   │  JPEG frames @10 FPS over WebSocket
   ▼
FastAPI backend ── MediaPipe Holistic ── PyTorch LSTM (258-dim windows of 30 frames)
   │  JSON {gesture, text, confidence, landmarks}
   ▼
browser captions + Web Speech API voice

## Performance (measured, honest)
- Recognition window: **~3 s** (30 frames @ 10 FPS) per prediction — by design, not a bug
- Validation accuracy: **__%** on a held-out 20% split (see Training)
- CPU-only inference; no GPU required

## Quickstart
Prereqs: Python **3.10–3.12**, Node 18+.

Backend:
cd ai_core
python -m venv venv && .\venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

Frontend:
cd web_app
npm install
npm run dev
Open http://localhost:5173 → Start a session → hold ASL letters steady (both hands in frame).

## Training
Dataset: [Kaggle ASL Alphabet](https://www.kaggle.com/datasets/grassknoted/asl-alphabet).
kaggle datasets download -d grassknoted/asl-alphabet -p ai_core/dataset --unzip
cd ai_core
python -m training.extract_dataset --data dataset/asl_alphabet_train/asl_alphabet_train --out dataset/processed --per-class 200
python -m training.train --data dataset/processed --epochs 40
Weights save to ai_core/models/ (gitignored by design — retrain or request weights).

## Tests & CI
pip install pytest
cd ai_core && python -m pytest tests -q
GitHub Actions runs the same suite on every push (.github/workflows/ci.yml).

## Docker (backend only)
cd ai_core && docker build -t signbridge-backend . && docker run -p 8000:8000 signbridge-backend

## Known limitations (being fixed next)
- Tracker currently requires **both hands + pose** → one-handed signs/letters often drop
- Static-image training sequences (jitter-augmented); dynamic gesture windows are roadmap
- Single-signer data; no held-out multi-signer test set yet

## Roadmap
1. One-hand-tolerant tracker + wrist/shoulder-relative normalization
2. Held-out test-set evaluation (Kaggle asl_alphabet_test) + confusion matrix
3. Own-signer word vocabulary ("Hello", "Thank You"…) via webcam recording
4. React Native mobile client; Docker-Compose full stack; in-browser (WASM) on-device inference

## License
MIT