from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)

    # Register blueprints
    from app.api.donations import bp as donations_bp
    from app.api.organizations import bp as organizations_bp
    from app.api.admin import bp as admin_bp
    from app.api.auth import bp as auth_bp
    
    app.register_blueprint(donations_bp, url_prefix='/api/donations')
    app.register_blueprint(organizations_bp, url_prefix='/api/organizations')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    return app