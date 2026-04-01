import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-fallback')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///dashboard.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CAMERA_SOURCE = os.environ.get('CAMERA_SOURCE', '0')
    # Use 0 for webcam, or RTSP/HTTP stream URL, or a local video path
