import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # secret key is needed for sessions and tokens
    SECRET_KEY = os.environ["AKPIK_SECRET_KEY"]
    SESSION_COOKIE_SECURE = True
    USE_HTTPS = os.getenv("AKPIK_USE_HTTPS", "").lower() == "true"
