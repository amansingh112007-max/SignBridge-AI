print(" Testing all imports...")

try:
    print("1. Testing tracker.py...")
    from app.services.tracker import KeypointTracker
    tracker = KeypointTracker()
    print("   ✅ Tracker loaded successfully!")
except Exception as e:
    print(f"   ❌ Tracker error: {e}")

try:
    print("2. Testing model.py...")
    from app.services.model import GestureModel
    model = GestureModel()
    print("   ✅ Model loaded successfully!")
except Exception as e:
    print(f"   ❌ Model error: {e}")

try:
    print("3. Testing voice.py...")
    from app.services.voice import TextToSpeech
    tts = TextToSpeech()
    print("   ✅ Voice service loaded successfully!")
except Exception as e:
    print(f"   ❌ Voice error: {e}")

try:
    print("4. Testing main.py (FastAPI app)...")
    from app.main import app
    print("   ✅ FastAPI app loaded successfully!")
except Exception as e:
    print(f"   ❌ FastAPI error: {e}")

print("\n All imports completed!")