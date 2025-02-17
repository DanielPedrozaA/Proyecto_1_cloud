from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Initialize extensions globally, but bind later
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    """Initialize Flask application with configurations."""
    load_dotenv()

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret')
    app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/*": {"origins": os.getenv("CORS_ORIGINS", "*")}})

    with app.app_context():

        from app.routes.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')

        db.create_all()

    return app
