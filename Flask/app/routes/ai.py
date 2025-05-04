<<<<<<< Updated upstream
import re
from flask import Blueprint, request, jsonify
import requests
=======
>>>>>>> Stashed changes
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin
from google.cloud import pubsub_v1
from app.models import Document, User
<<<<<<< Updated upstream
import os
from celery import Celery

redis_host = os.environ.get("REDIS_HOST", "redis")
celery_app = Celery('tasks', broker=f"redis://{redis_host}:6379/0")
=======

project_id = os.getenv("GCP_PROJECT_ID")
topic_id   = os.getenv("PUBSUB_TOPIC_ID")

>>>>>>> Stashed changes

ai_bp = Blueprint('ai', __name__)

def get_publisher():            # ← se crea DESPUÉS del fork
    return pubsub_v1.PublisherClient()

def sanitize_collection_name(name):
    base = name.rsplit('.', 1)[0].lower()
    base = re.sub(r'[^a-z0-9_-]', '_', base)
    base = re.sub(r'_+', '_', base).strip('_')
    return (base + 'doc')[:63] if len(base) < 3 else base[:63]

@ai_bp.route("/documents/<int:doc_id>/ask", methods=["POST", "OPTIONS"])
@cross_origin()
@jwt_required()
def ask_question(doc_id):
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify(msg="User not found"), 404

    doc = Document.query.filter_by(id=doc_id, user_id=user.id).first()
    if not doc:
        return jsonify(msg="Document not found"), 404

    payload = {
        "question": request.json.get("question"),
        "collection": sanitize_collection_name(doc.original_filename),
        "id": doc.id,
        "extension": doc.extension,
    }

    publisher  = get_publisher()
    topic_path = publisher.topic_path(project_id, topic_id)
    data       = json.dumps(payload).encode()

    try:
<<<<<<< Updated upstream
        task = celery_app.send_task('process.sms', queue="allqueue", args=[payload])
    except Exception as e:
        return jsonify({'message': 'Error connecting to AI service', 'error': str(e)}), 500

    return jsonify({"task_id": task.id}), 202
=======
        print(f"Project ID: {project_id}, Topic ID: {topic_id}")
        print(f"Topic Path: {topic_path}")
        print("inicio")
        future = publisher.publish(topic_path, data=data)
        print("medio")
        future.add_done_callback(lambda f: print("PubSub msg id:", f.result()))
        print("fin")
    except Exception as err:
        return jsonify(msg="Error publishing to Pub/Sub", error=str(err)), 500

    return jsonify(msg="Task queued"), 202
>>>>>>> Stashed changes
