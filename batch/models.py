from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
import enum
from datetime import datetime

Base = declarative_base()

class Status(enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Status_Embeddings(enum.Enum):
    """Enum for document processing status."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(128), unique=True, nullable=False)
    email = Column(String(128), unique=True, nullable=False)
    password = Column(String(128), nullable=False)

class Documentt(Base):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(Status), default=Status.UPLOADED)
    embbedings_status = Column(Enum(Status_Embeddings), default=Status_Embeddings.PENDING)
    original_filename = Column(String(256), nullable=False)
    extension = Column(String(256), nullable=False)
    file_path = Column(String(512), nullable=False)
    summary = Column(String)