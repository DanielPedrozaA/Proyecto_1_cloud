from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Initialize extensions globally, but bind later

def create_app():
    """Initialize Flask application with configurations."""
    load_dotenv()
    
    app = Flask(__name__)

    CORS(app, resources={r"/*": {"origins": os.getenv("CORS_ORIGINS", "*")}})

    with app.app_context():

        from app.routes.embbedings import auth_bp
        app.register_blueprint(auth_bp)

    return app
