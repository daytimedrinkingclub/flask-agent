# app/extensions.py
# this file contains the extensions for the app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

print("Initializing extensions...")

db = SQLAlchemy()
migrate = Migrate()

def init_extensions(app):
    print("Running init_extensions...")
    print(f"SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    print("Extensions initialized successfully")