# app/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file in the root of the project
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
print(os.getenv('SECRET_KEY'))

class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False