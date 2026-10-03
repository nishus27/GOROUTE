"""Application configuration loaded from environment variables.

SQLite is the only supported database. The database file lives at
``backend/instance/goroute.db`` and is created automatically on startup.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# backend/  (this file is backend/app/config.py)
BACKEND_DIR = Path(__file__).resolve().parent.parent

# Load backend/.env if present. Real environment variables always win.
load_dotenv(BACKEND_DIR / ".env")

# backend/instance/  ->  backend/instance/goroute.db
INSTANCE_DIR = BACKEND_DIR / "instance"
DEFAULT_DB_PATH = INSTANCE_DIR / "goroute.db"


def _default_sqlite_uri() -> str:
    # as_posix() keeps forward slashes, which SQLAlchemy expects on Windows.
    return f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"


def _split_env_list(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


class Config:
    """Base configuration for the GoRoute backend."""

    # --- Core ---
    # Dev fallback only. Set SECRET_KEY in backend/.env for anything real.
    SECRET_KEY = os.getenv("SECRET_KEY", "goroute-dev-secret-key")
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
    JSON_SORT_KEYS = False

    # --- Database (SQLite only) ---
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or _default_sqlite_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # --- CORS (React + Vite dev server) ---
    CORS_ORIGINS = _split_env_list(
        os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
    )

    # --- Session-based auth ---
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False  # set True when served over HTTPS
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 7  # 7 days
