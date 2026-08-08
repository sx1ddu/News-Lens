"""
Central configuration for the backend.

Everything that can change between environments (dev / production) lives
here and is read from environment variables, never hardcoded.
"""

from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

# --- Model paths ------------------------------------------------------

MODELS_DIR = BASE_DIR / "models"

BIAS_MODEL_PATH = MODELS_DIR / "bias_model"
STANCE_MODEL_PATH = MODELS_DIR / "stance_model"

# --- News API -----------------------------------------------------------

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# --- Server ---------------------------------------------------------------

PORT = int(os.getenv("PORT", "8000"))

# Comma separated list, e.g. "http://localhost:5173,https://myapp.com"
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

# --- Search / article handling --------------------------------------------

# How many articles to request from the News API per search.
ARTICLE_LIMIT = int(os.getenv("ARTICLE_LIMIT", "10"))

# How long (seconds) we wait for a single article page to download.
ARTICLE_FETCH_TIMEOUT = int(os.getenv("ARTICLE_FETCH_TIMEOUT", "8"))

# Articles shorter than this (in words) are treated as extraction failures
# (paywalled stubs, "enable JavaScript" pages, etc.)
MIN_ARTICLE_WORDS = int(os.getenv("MIN_ARTICLE_WORDS", "50"))
