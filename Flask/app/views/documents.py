import os
from datetime import datetime
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User, Document, Status, Status_Embeddings
from celery import Celery

redis_host = os.environ.get("REDISHOST", "redis")
celery_app = Celery('tasks', broker=f"redis://{redis_host}:6379/0")

ALLOWED_DOC_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx', 'md'}

def allowed_doc_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_DOC_EXTENSIONS

class DocumentUploadResource(Resource):
    """
    POST /documents/upload
    Sube un documento (PDF, TXT, Word, Markdown).
    """
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if not current_user:
            return {'message': 'Acceso no autorizado'}, 403

        user = User.query.filter_by(id=current_user).first()
        if not user:
            return {'message': 'Usuario no encontrado'}, 404

        if 'file' not in request.files:
            return {'message': 'No se ha seleccionado ningún archivo'}, 412

        file = request.files['file']
        if file.filename == '':
            return {'message': 'No se ha seleccionado ningún archivo'}, 412

        if not allowed_doc_file(file.filename):
            return {'message': 'Extensión de archivo no permitida'}, 412

        REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        DOCUMENT_DIRECTORY = os.path.join(REPO_ROOT, "uploadedDocuments")
        if not os.path.exists(DOCUMENT_DIRECTORY):
            os.makedirs(DOCUMENT_DIRECTORY)

        extension = file.filename.rsplit('.', 1)[1].lower()

        document = Document(
            user_id=user.id,
            timestamp=datetime.utcnow(),
            status=Status.UPLOADED,
            embbedings_status=Status_Embeddings.PENDING,
            extension= extension,
            original_filename=file.filename,
            file_path=''
        )

        db.session.add(document)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error en la base de datos: {str(e)}'}, 500

        
        name = file.filename.rsplit('.', 1)[0].lower()
        filename = f"document_{document.id}.{extension}"
        file_path = os.path.join(DOCUMENT_DIRECTORY, filename)
        file.save(file_path)

        document.file_path = file_path
        db.session.commit()

        celery_app.send_task('process.document', queue='document_queue', args=[file_path, document.id])
        celery_app.send_task('process.embeddings',queue='embeddings_queue', args=[document.id,extension,name],countdown=2)

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