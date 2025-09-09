import os
from dotenv import load_dotenv

load_dotenv()

ASSISTANT_NAME = "Aethera"
WAKE_WORDS = ["aethera", "hey aethera", "ok aethera"]
LISTENING_TIMEOUT = 5
PHRASE_TIMEOUT = 10

TTS_RATE = 200
TTS_VOLUME = 0.8
TTS_VOICE_INDEX = 1

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

SCREENSHOTS_DIR = "screenshots"
DOWNLOADS_DIR = "downloads"

CONFIRMATION_REQUIRED = [
    "delete", "remove", "shutdown", "restart", "format"
]

MAX_SEARCH_RESULTS = 3
SEARCH_SUMMARY_LENGTH = 200