from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, jwt_required, get_jwt_identity, JWTManager
from app.models import User, db
from app import jwt


revoked_tokens = set()

# Crear nuevo usuario
def crear_usuario(data):
    if 'username' not in data or 'password' not in data:
        return {'mensaje': 'Faltan datos obligatorios'}, 400

    if User.query.filter_by(username=data['username']).first():
        return {'mensaje': 'El nombre de usuario ya está en uso'}, 409

    if User.query.filter_by(email=data['email']).first():
        return {'mensaje': 'El email ya está siendo utilizado'}, 409

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    nuevo_usuario = User(username=data['username'], email=data['email'], password=hashed_password)
    
    db.session.add(nuevo_usuario)
    db.session.commit()

    return {'mensaje': 'Usuario creado exitosamente'}, 201

# Login
def login(data):
    if 'username' not in data or 'password' not in data:
        return {'mensaje': 'Faltan datos obligatorios'}, 400

    usuario = User.query.filter_by(username=data['username']).first()
    if not usuario or not check_password_hash(usuario.password, data['password']):
        return {'mensaje': 'Credenciales inválidas'}, 401

    access_token = create_access_token(identity=str(usuario.id))
    refresh_token = create_refresh_token(identity=str(usuario.id))

    return {'access_token': access_token,'refresh_token': refresh_token, 'usuario': usuario.id, 'username': str(usuario.username)}, 200

# logout
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    revoked_tokens.add(jti)
    return {'mensaje': 'Logout exitoso, token revocado'}, 200

# Refresh Token
@jwt_required(refresh=True)
def refresh_token():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return {'access_token': new_access_token}, 200

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in revoked_tokens