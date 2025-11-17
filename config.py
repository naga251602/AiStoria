# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Read from env, fallback to random only for local dev
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(24))
    
    UPLOAD_FOLDER = 'uploads'
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///local.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False