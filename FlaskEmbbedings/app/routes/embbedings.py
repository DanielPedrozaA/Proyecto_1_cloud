from flask import Blueprint, request
from app.views.embbedings import embbedings, question

auth_bp = Blueprint('auth', __name__)

# Endpoint para crear usuario
@auth_bp.route('/test', methods=['GET'])
def EmbbedingsWrapper():
    return embbedings()

@auth_bp.route('/question', methods=['POST'])
def QuestionWrapper():
    data = request.json
    return question(data)


