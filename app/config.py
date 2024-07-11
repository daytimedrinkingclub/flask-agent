import os
from dotenv import load_dotenv

load_dotenv()

class Config:
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
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_DEBUG = False
    
    # Redis configuration
    REDIS_URL = os.environ.get('REDIS_TLS_URL') or os.environ.get('REDIS_URL')

    @classmethod
    def init_app(cls, app):
        # You can add application-wide configurations here
        pass