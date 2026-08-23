from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2

# Import our custom services
from services.tracker import KeypointTracker
from services.model import GestureModel
from services.voice import TextToSpeech

app = FastAPI(title="SignBridge AI Backend")

# Allow the web app to talk to this backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, change this to your specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize our services globally so we don't reload them every request
tracker = KeypointTracker()
model = GestureModel()
tts = TextToSpeech()

@app.get("/")
def read_root():
    return {"message": "SignBridge AI Backend is running! 🚀"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ Client connected via WebSocket")
    
    try:
        while True:
            # 1. Receive raw image bytes from the frontend
            data = await websocket.receive_bytes()
            
            # 2. Convert bytes back to an OpenCV image
            nparr = np.frombuffer(data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is not None:
                # 3. Extract skeletal keypoints
                keypoints = tracker.get_keypoints(img)
                
                if keypoints is not None:
                    # 4. Predict the gesture
                    gesture = model.predict(keypoints)
                    
                    if gesture and gesture != "None":
                        # 5. Speak the word out loud
                        tts.speak(gesture)
                        # Send the recognized word back to the frontend
                        await websocket.send_json({"gesture": gesture})
                    else:
                        await websocket.send_json({"gesture": "None"})
                else:
                    await websocket.send_json({"gesture": "None"})
                    
    except WebSocketDisconnect:
        print("❌ Client disconnected")