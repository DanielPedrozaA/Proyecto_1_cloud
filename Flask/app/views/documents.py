import os
import io
from datetime import datetime
from flask import request, send_file
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User, Document, Status, Status_Embeddings
from celery import Celery
from google.cloud import storage
from google.oauth2 import service_account

# Ruta local al archivo JSON
#key_path = "/flask_app/keyfile.json"

# Cargar credenciales manualmente
#credentials = service_account.Credentials.from_service_account_file(key_path)

# Crear cliente de GCS con esas credenciales
#client = storage.Client(credentials=credentials, project="desarollo-de-soluciones-cloud")

GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "ultra-pro-bucket")

# No cargamos credenciales manualmente, GCP las inyecta por IAM
client = storage.Client()

bucket = client.bucket(GCS_BUCKET_NAME)

# Configuración de Celery
redis_host = os.environ.get("REDISHOST", "redis")
celery_app = Celery('tasks', broker=f"redis://{redis_host}:6379/0")

ALLOWED_DOC_EXTENSIONS = {'pdf', 'txt', 'md'}

def allowed_doc_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_DOC_EXTENSIONS

class DocumentUploadResource(Resource):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        user = User.query.filter_by(id=current_user).first()
        if not user:
            return {'message': 'Usuario no encontrado'}, 404

        if 'file' not in request.files:
            return {'message': 'No se ha seleccionado ningún archivo'}, 412

        file = request.files['file']
        if file.filename == '' or not allowed_doc_file(file.filename):
            return {'message': 'Archivo inválido'}, 412

        extension = file.filename.rsplit('.', 1)[1].lower()
        document = Document(
            user_id=user.id,
            timestamp=datetime.utcnow(),
            status=Status.UPLOADED,
            embbedings_status=Status_Embeddings.PENDING,
            extension=extension,
            original_filename=file.filename,
            file_path=""
        )
        db.session.add(document)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error en la base de datos: {str(e)}'}, 500

        filename = f"document_{document.id}.{extension}"
        blob = bucket.blob(filename)
        blob.upload_from_file(file, content_type=file.content_type)

        document.file_path = filename
        db.session.commit()

        return {'message': 'Documento subido exitosamente'}, 201

class DocumentListResource(Resource):
    """
    GET /documents
    Lista todos los documentos del usuario autenticado.
    """
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        if not current_user:
            return {'message': 'Acceso no autorizado'}, 403

        user = User.query.filter_by(id=current_user).first()
        if not user:
            return {'message': 'Usuario no encontrado'}, 404

        documents = Document.query.filter_by(user_id=user.id).all()
        results = []
        for doc in documents:
            results.append({
                'id': doc.id,
                'original_filename': doc.original_filename,
                'status': doc.status.value,
                'timestamp': doc.timestamp.isoformat(),
                'file_path': doc.file_path,
                'summary': doc.summary
            })
        return results, 200

class DocumentDetailResource(Resource):
    """
    GET /documents/<doc_id>
    Retorna información de un documento específico.

    DELETE /documents/<doc_id>
    Elimina un documento específico.
    """
    @jwt_required()
    def get(self, doc_id):
        current_user = get_jwt_identity()
        if not current_user:
            return {'message': 'Acceso no autorizado'}, 403

        user = User.query.filter_by(id=current_user).first()
        if not user:
            return {'message': 'Usuario no encontrado'}, 404

        doc = Document.query.filter_by(id=doc_id, user_id=user.id).first()
        if not doc:
            return {'message': 'Documento no encontrado'}, 404

        return {
            'id': doc.id,
            'original_filename': doc.original_filename,
            'status': doc.status.value,
            'timestamp': doc.timestamp.isoformat(),
            'file_path': doc.file_path,
            'summary': doc.summary
        }, 200

    @jwt_required()
    def delete(self, doc_id):
        current_user = get_jwt_identity()
        if not current_user:
            return {'message': 'Acceso no autorizado'}, 403

        user = User.query.filter_by(id=current_user).first()
        if not user:
            return {'message': 'Usuario no encontrado'}, 404

        doc = Document.query.filter_by(id=doc_id, user_id=user.id).first()
        if not doc:
            return {'message': 'Documento no encontrado'}, 404

        db.session.delete(doc)
        db.session.commit()
        return {'message': 'Documento eliminado exitosamente'}, 200

class DocumentDownloadResource(Resource):
    @jwt_required()
    def get(self, doc_id):
        current_user = get_jwt_identity()
        user = User.query.filter_by(id=current_user).first()
        if not user:
            return {'message': 'Usuario no encontrado'}, 404

        doc = Document.query.filter_by(id=doc_id, user_id=user.id).first()
        if not doc:
            return {'message': 'Documento no encontrado'}, 404

        try:
            blob = bucket.blob(doc.file_path)
            file_obj = io.BytesIO()
            blob.download_to_file(file_obj)
            file_obj.seek(0)
        except Exception as e:
            return {'message': f'Error al descargar el archivo: {str(e)}'}, 500

        return send_file(file_obj, download_name=doc.original_filename, as_attachment=True)
