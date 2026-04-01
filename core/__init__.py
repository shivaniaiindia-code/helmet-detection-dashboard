from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure snapshots directory exists
    os.makedirs(os.path.join(app.root_path, 'static', 'snapshots'), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from core.models import User
        return User.query.get(int(user_id))

    # Register Blueprints
    from core.routes.auth import auth_bp
    from core.routes.dashboard import dashboard_bp
    from core.routes.logs import logs_bp
    from core.routes.stream import stream_bp
    from core.routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(stream_bp)
    app.register_blueprint(settings_bp)

    with app.app_context():
        db.create_all()
        
        # Create default user if none exists
        from core.models import User
        from werkzeug.security import generate_password_hash
        if not User.query.first():
            default_user = User(username='admin', password=generate_password_hash('admin'))
            db.session.add(default_user)
            db.session.commit()
            print("Default admin user created (admin/admin).")

    return app
