import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"

TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# Voice Settings
DEFAULT_VOICE = os.getenv("VOICE_NAME", "ar-SA-HamedNeural")
VOICE_RATE = os.getenv("VOICE_RATE", "+10%")

# Video Output Specs
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
TARGET_FPS = 30
