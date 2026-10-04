import pyttsx3
import threading

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 1.0) # Volume (0.0 to 1.0)
        
        self.is_speaking = False
        self.lock = threading.Lock()

    def speak(self, text, lang="en"):
        if text and text != "None":
            thread = threading.Thread(target=self._speak_text, args=(text, lang))
            thread.start()

    def _speak_text(self, text, lang):
        with self.lock:
            if not self.is_speaking:
                self.is_speaking = True
                try:
                    # Try to pick a Hindi system voice if the user chose हिंदी
                    if lang == "hi":
                        for v in self.engine.getProperty('voices'):
                            if 'hindi' in v.name.lower() or 'hi-in' in v.id.lower():
                                self.engine.setProperty('voice', v.id)
                                break
                    self.engine.say(text)
                    self.engine.runAndWait()
                finally:
                    self.is_speaking = False