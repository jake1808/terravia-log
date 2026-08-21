from flask import Flask
from app.config import Config
from app.models import db

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize database with the app
    db.init_app(app)
    
    # Import and register Blueprints (URLs)
    from app.auth import auth_bp
    from app.protected import protected_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(protected_bp)
    
    # Create tables automatically
    with app.app_context():
        db.create_all()

    return app

# from flask import Flask

# # from flask_migrate import Migrate
# from app.config import Config
# from app.models import db
# from app.auth import auth_bp
# from app.protected import protected_bp


# # Use Flask-Migrate for database migrations in production, but for development, 
# # you can use db.create_all() to create tables directly.

# # migrate = Migrate()

# def create_app():
#     app = Flask(__name__)
#     # Load configuration from Config class
#     app.config.from_object(Config)
    
#     # Initialize extensions
#     db.init_app(app)
#     # migrate.init_app(app, db)
    
#     # Register blueprints
#     app.register_blueprint(auth_bp)
#     app.register_blueprint(protected_bp)
    
#     # Create database tables if they don't exist
#     with app.app_context():
#         db.create_all()

#     return app