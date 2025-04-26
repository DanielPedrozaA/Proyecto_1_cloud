from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.views.auth import crear_usuario, login, logout, refresh_token, health

# Create Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

# Register User
@auth_bp.route('/register', methods=['POST'])
def register_route():
    data = request.json
    return crear_usuario(data)

# Login User
@auth_bp.route('/login', methods=['POST'])
def login_route():
    data = request.json
    return login(data)

# Logout User
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout_route():
    return logout()

# Refresh Token
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_route():
    return refresh_token()

# Health
@auth_bp.route('/health', methods=['GET'])
def getHealth():
    return health()
