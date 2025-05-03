from google.cloud import pubsub_v1
import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin
from app.models import Document, User
import re
from celery import Celery

# Set up Google Cloud Pub/Sub publisher
project_id = os.getenv("GCP_PROJECT_ID")
topic_id = os.getenv("PUBSUB_TOPIC_ID")
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

# Redis configuration
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
        # Convert payload to a JSON string and then to bytes
        message_data = str(payload).encode("utf-8")
        
        # Publish the message to Pub/Sub
        publisher.publish(topic_path, message_data)

    except Exception as e:
        return jsonify({'message': 'Error sending message to Pub/Sub', 'error': str(e)}), 500

    return jsonify({"message": "Message sent to worker", "status": "waiting for response"}), 202
