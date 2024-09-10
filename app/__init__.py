# app/__init__.py
from flask import Flask
from .config import Config
from .extensions import init_extensions


def create_app(config_class=Config):

    print(f"Creating Flask app...")
    app = Flask(__name__)

    print(f"Flask app created successfully")
    app.config.from_object(config_class)

    print(f"App config loaded initalising extensions")
    init_extensions(app)
    print(f"Extensions initialised")

    from .routes.main import bp as main_bp  
    app.register_blueprint(main_bp)
    
    from .services.data_service import DataService
    

    return app