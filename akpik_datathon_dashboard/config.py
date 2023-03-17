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
    DATA_PATH = Path(os.getenv("AKPIK_DATA_PATH", "submissions")).absolute()

    SQLALCHEMY_DATABASE_URI = os.getenv("AKPIK_DATABASE_URI", "sqlite:///akpik23.sqlite")
    REDIS_URL = os.getenv("AKPIK_REDIS_URL", "redis://localhost")
    RANDOM_SEED = int(os.getenv("AKPIK_RANDOM_SEED", 0))

    # limit upload size to 100 kb
    MAX_CONTENT_LENGTH = 100 * 1024
