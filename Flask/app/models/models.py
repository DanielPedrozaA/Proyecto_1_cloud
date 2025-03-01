from flask_sqlalchemy import SQLAlchemy
import enum
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from datetime import datetime
from app import db 

class Status(enum.Enum):
    """Enum for document processing status."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Status_Embeddings(enum.Enum):
    """Enum for document processing status."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class User(db.Model):
    """User model for authentication and document tracking."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    documents = db.relationship('Document', cascade='all, delete, delete-orphan', backref='user')

class Document(db.Model):
    """Document model for storing uploaded files and their processing status."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum(Status), default=Status.UPLOADED)
    embbedings_status = db.Column(db.Enum(Status_Embeddings), default=Status_Embeddings.PENDING)
    original_filename = db.Column(db.String(256), nullable=False)
    extension = db.Column(db.String(256), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    summary = db.Column(db.Text, nullable=True)

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True

class DocumentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Document
        include_fk = True
        load_instance = True
