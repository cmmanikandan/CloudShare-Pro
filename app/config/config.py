import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    CLOUDINARY_UPLOAD_PRESET = os.environ.get('CLOUDINARY_UPLOAD_PRESET')
    
    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # Telegram
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

    # Firebase (for frontend)
    VITE_FIREBASE_API_KEY = os.environ.get('VITE_FIREBASE_API_KEY')
    VITE_FIREBASE_AUTH_DOMAIN = os.environ.get('VITE_FIREBASE_AUTH_DOMAIN')
    VITE_FIREBASE_PROJECT_ID = os.environ.get('VITE_FIREBASE_PROJECT_ID')
    VITE_FIREBASE_STORAGE_BUCKET = os.environ.get('VITE_FIREBASE_STORAGE_BUCKET')
    VITE_FIREBASE_MESSAGING_SENDER_ID = os.environ.get('VITE_FIREBASE_MESSAGING_SENDER_ID')
    VITE_FIREBASE_APP_ID = os.environ.get('VITE_FIREBASE_APP_ID')
    VITE_FIREBASE_MEASUREMENT_ID = os.environ.get('VITE_FIREBASE_MEASUREMENT_ID')
