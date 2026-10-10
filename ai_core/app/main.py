from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.tracker import KeypointTracker
from app.services.model import GestureModel
from app.services.voice import TextToSpeech

app = FastAPI(title="SignBridge AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MVP vocabulary in both launch languages (words; letters fall back to themselves)
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
CONFIDENCE_FLOOR = 40

current_lang = "en"   # simple global for the student MVP

tracker = KeypointTracker()
model = GestureModel()
tts = TextToSpeech()


@app.get("/")
def read_root():
    return {"message": "SignBridge AI Backend is running! 🚀"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global current_lang
    await websocket.accept()
    print("✅ Client connected via WebSocket")

    try:
        while True:
            message = await websocket.receive()

            # Text message = control command (e.g. language switch)
            if "text" in message:
                ctrl = json.loads(message["text"])
                current_lang = ctrl.get("lang", current_lang)
                print(f"🌐 Language set to: {current_lang}")
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
                gesture, confidence = model.predict(keypoints)
                if gesture != "None" and confidence >= CONFIDENCE_FLOOR:
                    entry = TRANSLATIONS.get(gesture, {"en": gesture, "hi": gesture})
                    spoken = entry.get(current_lang, gesture)
                    tts.speak(spoken, current_lang)
                    text_out = spoken
                else:
                    text_out = None   # graceful uncertainty: ask to repeat, don't guess

                await websocket.send_json({
                    "gesture": gesture,
                    "text": text_out,
                    "confidence": confidence,
                    "tracking": True,
                    "landmarks": display,
                })
            else:
                await websocket.send_json({
                    "gesture": "None", "text": None,
                    "confidence": 0, "tracking": False, "landmarks": None,
                })

    except WebSocketDisconnect:
        print("❌ Client disconnected")