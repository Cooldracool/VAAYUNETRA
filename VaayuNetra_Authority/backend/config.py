import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Default geographical coordinates (Center: Delhi NCR)
DEFAULT_LATITUDE = 28.6139
DEFAULT_LONGITUDE = 77.2090

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
APP_VERSION = "1.0.0"
APP_NAME = "VaayuNetra Environmental Intelligence BFF"

# CORS origins
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://10.0.2.2:8000",  # Android emulator localhost alias
    "*",
]

# Google AI / Gemini Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
