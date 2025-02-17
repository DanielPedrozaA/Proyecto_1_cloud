from flask import Blueprint, request
from app.views.auth import crear_usuario, login

auth_bp = Blueprint('auth', __name__)

# Endpoint para crear usuario
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    return crear_usuario(data)

# Endpoint para login
@auth_bp.route('/login', methods=['POST'])
def login_route():
    data = request.json
    return login(data)