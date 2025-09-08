try:
    import aifc
except ModuleNotFoundError:
    import aifc_fix

import speech_recognition as sr
import pyttsx3
import threading
import time
from config import TTS_RATE, TTS_VOLUME, TTS_VOICE_INDEX, LISTENING_TIMEOUT, PHRASE_TIMEOUT

class SpeechHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 3.0
        
        self.microphone = sr.Microphone()
        
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        
        print("Adjusting for ambient noise... Please wait.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Ready for voice commands!")
    
    def setup_tts(self):
        voices = self.tts_engine.getProperty('voices')
        
        if voices and len(voices) > TTS_VOICE_INDEX:
            self.tts_engine.setProperty('voice', voices[TTS_VOICE_INDEX].id)
        
        self.tts_engine.setProperty('rate', TTS_RATE)
        self.tts_engine.setProperty('volume', TTS_VOLUME)
    
    def listen(self):
        try:
            with self.microphone as source:
                print("Listening...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=LISTENING_TIMEOUT, 
                    phrase_time_limit=PHRASE_TIMEOUT
                )
            
            print("Processing...")
            text = self.recognizer.recognize_google(audio).lower()
            print(f"You said: {text}")
            return True, text
            
        except sr.WaitTimeoutError:
            return False, "Listening timeout"
        except sr.UnknownValueError:
            return False, "Could not understand audio"
        except sr.RequestError as e:
            return False, f"Could not request results; {e}"
        except Exception as e:
            return False, f"Error: {e}"
    
    def speak(self, text):
        print(f"Aethera: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def speak_async(self, text):
        def speak_thread():
            self.speak(text)
        
        thread = threading.Thread(target=speak_thread)
        thread.daemon = True
        thread.start()
    
    def is_wake_word_detected(self, text, wake_words):
        return any(wake_word in text.lower() for wake_word in wake_words)
    
    def remove_wake_word(self, text, wake_words):
        text_lower = text.lower()
        for wake_word in wake_words:
            if text_lower.startswith(wake_word):
                return text[len(wake_word):].strip()
        return text.strip()