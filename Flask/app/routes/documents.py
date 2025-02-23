from flask import Blueprint
from flask_restful import Api
from app.views.documents import (
    DocumentUploadResource,
    DocumentListResource,
    DocumentDetailResource
)

document_bp = Blueprint('document', __name__)
document_api = Api(document_bp)

# POST /documents/upload
document_api.add_resource(DocumentUploadResource, '/upload')

# GET /documents
document_api.add_resource(DocumentListResource, '/')

# GET /documents/<doc_id> y DELETE /documents/<doc_id>
document_api.add_resource(DocumentDetailResource, '/<int:doc_id>')