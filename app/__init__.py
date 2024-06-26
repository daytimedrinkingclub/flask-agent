# app/__init__.py
from flask import Flask
from .config import Config
from .extensions import login_manager, init_extensions


def create_app(config_class=Config):

    print(f"Creating Flask app...")
    app = Flask(__name__)

    print(f"Flask app created successfully")
    app.config.from_object(config_class)

    print(f"App config loaded initalising extensions")
    init_extensions(app)
    print(f"Extensions initialised")

    from .routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .routes.main import bp as main_bp  
    app.register_blueprint(main_bp)
    
    from .services.data_service import DataService
    
    @login_manager.user_loader
    def load_user(user_id):
        return DataService.get_user_by_id(user_id)

    return app