# app/extensions.py
# this file contains the extensions for the app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .redis_client import get_redis

print("Initializing extensions...")

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
redis_client = get_redis()

def init_extensions(app):
    print("Running init_extensions...")
    print(f"SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    print("Extensions initialized successfully")