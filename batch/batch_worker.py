# batch/batch_worker.py

import os
import shutil
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document, User,Status, Base

# Configuración de Celery
redis_host = os.environ.get("REDISHOST", "redis")
celery_app = Celery('tasks', broker=f"redis://{redis_host}:6379/0")

# Configuración de la base de datos
db_user = os.environ.get("POSTGRES_USER", "admin")
db_password = os.environ.get("POSTGRES_PASSWORD", "password")
db_host = os.environ.get("POSTGRES_HOST", "db")
db_name = os.environ.get("POSTGRES_DB", "rag_saas")
db_port = os.environ.get("POSTGRES_PORT", "5432")
DATABASE_URL = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@celery_app.task(name='process.document', queue = "document_queue")
def process_document(file_path, document_id):
    """
    Tarea que simula el procesamiento del documento:
    - Actualiza la base de datos, marcando el documento como COMPLETED.
    """

    processed_dir = os.path.join(os.path.dirname(file_path), "processedDocuments")
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
    filename = os.path.basename(file_path)
    destination_path = os.path.join(processed_dir, filename)
    
    shutil.move(file_path, destination_path)

    session = Session()
    try:
        doc = session.query(Document).get(document_id)
        if doc:
            doc.status = Status.COMPLETED
            doc.file_path = destination_path
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
