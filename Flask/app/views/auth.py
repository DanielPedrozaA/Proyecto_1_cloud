from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app.models import User, db


# Crear nuevo usuario
def crear_usuario(data):
    errors = {}

    if 'username' not in data or not data['username'].strip():
        errors['username'] = 'El nombre de usuario es obligatorio'
    elif len(data['username']) < 3:
        errors['username'] = 'El nombre de usuario debe tener al menos 3 caracteres'

    # Validate Email
    if 'email' not in data or not data['email'].strip():
        errors['email'] = 'El correo electrónico es obligatorio'
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
        errors['email'] = 'El correo electrónico no es válido'

    # Validate Password
    if 'password' not in data or not data['password'].strip():
        errors['password'] = 'La contraseña es obligatoria'
    elif len(data['password']) < 6:
        errors['password'] = 'La contraseña debe tener al menos 6 caracteres'

    if errors:
        return {'errores': errors}, 400

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

    access_token = create_access_token(identity={'id': usuario.id, 'username': usuario.username})

    return {'access_token': access_token, 'usuario': usuario.id}, 200
