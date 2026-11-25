
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "change-this-development-secret"
    )

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{ROOT / 'database' / 'codemate.db'}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024

    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

    NVIDIA_MODEL = os.getenv(
        "NVIDIA_MODEL",
        "meta/llama-3.3-70b-instruct"
    )

    NVIDIA_BASE_URL = os.getenv(
        "NVIDIA_BASE_URL",
        "https://integrate.api.nvidia.com/v1"
    )

    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
