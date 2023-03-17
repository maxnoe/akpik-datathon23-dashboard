import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


class Config:
    # secret key is needed for sessions and tokens
    SECRET_KEY = os.environ["AKPIK_SECRET_KEY"]
    SESSION_COOKIE_SECURE = True
    USE_HTTPS = os.getenv("AKPIK_USE_HTTPS", "").lower() == "true"

    # submissions are stored here
    UPLOAD_PATH = Path(os.getenv("AKPIK_UPLOAD_PATH", "submissions")).absolute()

    SQLALCHEMY_DATABASE_URI = os.environ["AKPIK_DATABASE_URI"]

    REDIS_URL = os.getenv("AKPIK_REDIS_URL", "redis://localhost")
