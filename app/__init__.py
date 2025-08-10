from flask import Flask
from app.config import config_dict
from app.extensions import db, migrate, login_manager, csrf


def create_app(config_name='development'):
    """
    Application factory function to create and configure the Flask app
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_dict[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.groups.routes import groups_bp
    from app.main import main_bp
    from app.payments.routes import payments_bp
    from app.history.routes import history_bp
    from app.profile.routes import profile_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(profile_bp)
    
    # Context processor for templates
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.utcnow()}
    
    return app