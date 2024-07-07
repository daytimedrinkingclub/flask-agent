# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')
    GOOGLE_SEARCH_API_KEY = os.environ.get('GOOGLE_SEARCH_API_KEY')
    SEARCH_ENGINE_ID = os.environ.get('SEARCH_ENGINE_ID')
    # Database configuration
    DATABASE_URL = os.environ.get('HEROKU_POSTGRESQL_PURPLE_URL') or os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', '1') == '1'
    # Redis configuration
    REDIS_URL = os.environ.get('REDIS_URL')
    if REDIS_URL and REDIS_URL.startswith("redis://"):
        REDIS_URL = REDIS_URL.replace("redis://", "redis://:", 1)
    
    # Use REDIS_TLS_URL if available (for Heroku Redis)
    REDIS_TLS_URL = os.environ.get('REDIS_TLS_URL')
    if REDIS_TLS_URL:
        REDIS_URL = REDIS_TLS_URL
    # # Email configuration
    # SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    # SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    # IMAP_SERVER = os.environ.get('IMAP_SERVER', 'imap.gmail.com')
    # IMAP_PORT = int(os.environ.get('IMAP_PORT', 993))
    # EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
    # EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')