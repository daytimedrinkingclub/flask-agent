from flask import Flask, render_template
from .config import Config
from .extensions import init_extensions
from .models import models  # Import at the top level
import logging

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
        # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    init_extensions(app)
    
    from .routes import auth, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    
    from .services.user_data.user_service import UserDataService
    
    @app.login_manager.user_loader
    def load_user(user_id):
        return UserDataService.get_user_by_id(user_id)
    
    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error('Server Error: %s', (error))
        return render_template('errors/500.html'), 500

    return app