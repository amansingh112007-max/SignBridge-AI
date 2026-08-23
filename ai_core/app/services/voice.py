import pyttsx3
import threading

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 1.0) # Volume (0.0 to 1.0)
        
        self.is_speaking = False
        self.lock = threading.Lock()

    def speak(self, text):
        if text and text != "None":
            # Run in a separate thread to avoid blocking the main app
            thread = threading.Thread(target=self._speak_text, args=(text,))
            thread.start()

    def _speak_text(self, text):
        with self.lock:
            if not self.is_speaking:
                self.is_speaking = True
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                finally:
                    self.is_speaking = False