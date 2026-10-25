from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.tracker import KeypointTracker
from app.services.model import GestureModel
from app.services.voice import TextToSpeech

app = FastAPI(title="SignBridge AI Backend")

# Locked down: only our own frontend may talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Server-side speech is OFF by default (the browser speaks on-device).
# Enable only for same-machine kiosk demos:  set SIGNBRIDGE_SERVER_TTS=1
SERVER_TTS = os.environ.get("SIGNBRIDGE_SERVER_TTS", "0") == "1"

# Vocabulary hook for future word-level models; letters fall back to themselves
TRANSLATIONS = {
    "Hello":     {"en": "Hello",     "hi": "नमस्ते"},
    "Thank You": {"en": "Thank you", "hi": "धन्यवाद"},
    "Yes":       {"en": "Yes",       "hi": "हाँ"},
    "No":        {"en": "No",        "hi": "नहीं"},
    "Please":    {"en": "Please",    "hi": "कृपया"},
    "Help":      {"en": "Help",      "hi": "मदद"},
    "Water":     {"en": "Water",     "hi": "पानी"},
    "Food":      {"en": "Food",      "hi": "खाना"},
    "Bathroom":  {"en": "Bathroom",  "hi": "शौचालय"},
}

# FR-7: low-confidence recognition never guesses silently
CONFIDENCE_FLOOR = 60

tracker = KeypointTracker()
model = GestureModel()                      # shared weights, stateless per connection
tts = TextToSpeech() if SERVER_TTS else None


@app.get("/")
def read_root():
    return {"message": "SignBridge AI Backend is running! 🚀"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ Client connected via WebSocket")

    # Per-connection state: two users can never corrupt each other's predictions
    session = {"buffer": [], "lang": "en", "last": None}

    try:
        while True:
            message = await websocket.receive()

            # Text message = control command (e.g. language switch)
            if "text" in message:
                ctrl = json.loads(message["text"])
                session["lang"] = ctrl.get("lang", session["lang"])
                print(f"🌐 Session language: {session['lang']}")
                continue

            # Bytes message = a JPEG video frame
            data = message.get("bytes")
            if not data:
                continue

            nparr = np.frombuffer(data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                continue

            keypoints, display = tracker.process_frame(img)

            if keypoints is not None:
                gesture, confidence, session["buffer"] = model.step(session["buffer"], keypoints)

                # FR-7 + temporal smoothing: caption/speak only on repeated, confident signs
                if (gesture != "None" and confidence >= CONFIDENCE_FLOOR
                        and gesture == session["last"]):
                    entry = TRANSLATIONS.get(gesture, {"en": gesture, "hi": gesture})
                    spoken = entry.get(session["lang"], gesture)
                    if tts:
                        tts.speak(spoken, session["lang"])
                    text_out = spoken
                else:
                    text_out = None
                session["last"] = gesture

                await websocket.send_json({
                    "gesture": gesture, "text": text_out,
                    "confidence": confidence, "tracking": True,
                    "landmarks": display,
                })
            else:
                # Tracking lost -> reset the temporal window (no stale-frame mixing)
                session["buffer"] = []
                session["last"] = None
                await websocket.send_json({
                    "gesture": "None", "text": None,
                    "confidence": 0, "tracking": False, "landmarks": None,
                })

    except WebSocketDisconnect:
        print("❌ Client disconnected")