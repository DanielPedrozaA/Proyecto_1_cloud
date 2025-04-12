import os
import io
from datetime import datetime
from flask import request, send_file
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User, Document, Status, Status_Embeddings
from celery import Celery
from smb.SMBConnection import SMBConnection

# Configuración de Celery
redis_host = os.environ.get("REDISHOST", "redis")
celery_app = Celery('tasks', broker=f"redis://{redis_host}:6379/0")

ALLOWED_DOC_EXTENSIONS = {'pdf', 'txt', 'md'}

def allowed_doc_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_DOC_EXTENSIONS

# Configuración de la conexión SMB (parámetros obtenidos desde variables de entorno)
SMB_SERVER = os.environ.get("SMB_SERVER")  # IP o hostname de la VM que tiene el sistema de archivos
SMB_PORT = int(os.environ.get("SMB_PORT", "445"))
SMB_USERNAME = os.environ.get("SMB_USERNAME")
SMB_PASSWORD = os.environ.get("SMB_PASSWORD")
SMB_SHARE = os.environ.get("SMB_SHARE")  # Nombre del recurso compartido en la VM remota
SMB_DIRECTORY = os.environ.get("SMB_DIRECTORY", "uploadedDocuments")  # Directorio dentro del recurso compartido
MY_NAME = os.environ.get("MY_NAME", "backend")  # Nombre del cliente para la conexión SMB
REMOTE_NAME = os.environ.get("REMOTE_NAME", "fileserver")  # Nombre de la VM remota en la red

class DocumentUploadResource(Resource):
    """
    POST /documents/upload
    Sube un documento (PDF, TXT, Markdown) a la VM remota que tiene el sistema de archivos vía SMB.
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

        extension = file.filename.rsplit('.', 1)[1].lower()

        document = Document(
            user_id=user.id,
            timestamp=datetime.utcnow(),
            status=Status.UPLOADED,
            embbedings_status=Status_Embeddings.PENDING,
            extension=extension,
            original_filename=file.filename,
            file_path=''
        )

        db.session.add(document)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error en la base de datos: {str(e)}'}, 500

        # Se define el nombre remoto para el archivo
        filename = f"document_{document.id}.{extension}"
        remote_path = filename

        # Se lee el contenido del archivo en memoria
        file_data = file.read()
        bio = io.BytesIO(file_data)

        # Se establece la conexión SMB y se almacena el archivo en la VM remota
        try:
            conn = SMBConnection(SMB_USERNAME, SMB_PASSWORD, MY_NAME, REMOTE_NAME, use_ntlm_v2=True)
            if not conn.connect(SMB_SERVER, SMB_PORT):
                return {'message': 'Error al conectar con el servidor de archivos'}, 500

            conn.storeFile(SMB_SHARE, remote_path, bio)
        except Exception as e:
            return {'message': f'Error al subir el archivo: {str(e)}'}, 500

        document.file_path = remote_path
        db.session.commit()

        # Se envía la tarea a Celery con la ruta remota
        #celery_app.send_task('process.document', queue='allqueue', args=[remote_path, document.id])
        # celery_app.send_task('process.embeddings', queue='allqueue', args=[document.id, extension, file.filename.rsplit('.', 1)[0].lower()], countdown=2)

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
    """
    GET /documents/<doc_id>/download
    Descarga el archivo almacenado en la VM remota a través de SMB.
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

        try:
            conn = SMBConnection(SMB_USERNAME, SMB_PASSWORD, MY_NAME, REMOTE_NAME, use_ntlm_v2=True)
            if not conn.connect(SMB_SERVER, SMB_PORT):
                return {'message': 'Error al conectar con el servidor de archivos'}, 500

            file_obj = io.BytesIO()
            conn.retrieveFile(SMB_SHARE, doc.file_path, file_obj)
            file_obj.seek(0)
        except Exception as e:
            return {'message': f'Error al descargar el archivo: {str(e)}'}, 500

        return send_file(file_obj, attachment_filename=doc.original_filename, as_attachment=True)
