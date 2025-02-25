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

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret')
    app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'

    print("DATABASE_URL (Flask):", app.config.get('SQLALCHEMY_DATABASE_URI'))
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/*": {"origins": os.getenv("CORS_ORIGINS", "*")}})

    from app.routes.documents import document_bp
    from app.routes.auth import auth_bp
    with app.app_context():

        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(document_bp, url_prefix='/documents')

        db.create_all()

    return app
