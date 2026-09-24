import cv2
import asyncio
import websockets

async def test_webcam():
    # Connect to your running FastAPI backend
    uri = "ws://localhost:8000/ws"
    print("🔄 Connecting to backend...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to backend! Starting camera...\n")
            
            # Open your laptop webcam
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                print("❌ Error: Could not open webcam.")
                return

            print("🎥 Camera is ON. Wave your hands around!")
            print("⌨️  Press 'q' on your keyboard to quit.\n")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # 🔄 FLIP THE IMAGE HORIZONTALLY
                frame = cv2.flip(frame, 1)  # 1 means flip horizontally

                # Compress the image to JPEG bytes...

                # Compress the image to JPEG bytes to send over the internet
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    continue

                # 1. Send the video frame to the backend
                await websocket.send(buffer.tobytes())

                # 2. Wait for the backend to tell us what sign it recognized
                response = await websocket.recv()
                
                # Print what the AI sees
                print(f"🤖 AI Backend says: {response}")

                # Show the camera feed on your screen
                cv2.imshow('SignBridge AI - Camera Test', frame)

                # Press 'q' to stop the test
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
            
    except Exception as e:
        print(f"❌ Connection failed. Is the uvicorn server running? Error: {e}")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_webcam())