import re
from flask import Blueprint, request, jsonify
import requests
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin
from app.models import Document, User
import os
from celery import Celery

redis_host = os.environ.get("REDIS_HOST", "redis")
celery_app = Celery('tasks', broker=f"redis://{redis_host}:6379/0")

ai_bp = Blueprint('ai', __name__)

def sanitize_collection_name(filename):
    """
    Sanitize the original filename to create a valid collection name.
    - Remove the extension (if present).
    - Convert to lowercase.
    - Replace characters that are not alphanumeric, underscore or hyphen with an underscore.
    - Replace multiple underscores with a single underscore.
    - Trim underscores from start and end.
    - Ensure the final name length is between 3 and 63 characters.
    """
    # Remove extension
    if '.' in filename:
        name = filename.rsplit('.', 1)[0]
    else:
        name = filename
    name = name.lower()
    name = re.sub(r'[^a-z0-9_-]', '_', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip('_')
    if len(name) < 3:
        name = (name + "doc")[:3]
    if len(name) > 63:
        name = name[:63]
    return name

@ai_bp.route('/documents/<int:doc_id>/ask', methods=['POST','OPTIONS'])
@cross_origin()
@jwt_required()
def ask_question(doc_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    doc = Document.query.filter_by(id=doc_id, user_id=user.id).first()
    if not doc:
        return jsonify({'message': 'Document not found'}), 404

    # Generate a valid collection name from the document's original filename
    collection_name = sanitize_collection_name(doc.original_filename)

    payload = {
        "question": request.json.get("question"),
        "collection": collection_name,
        "id": doc.id,
        "extension": doc.extension
    }

    try:
        task = celery_app.send_task('process.sms', queue="allqueue", args=[payload])
    except Exception as e:
        return jsonify({'message': 'Error connecting to AI service', 'error': str(e)}), 500

    return jsonify({"task_id": task.id}), 202
