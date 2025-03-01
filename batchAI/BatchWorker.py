import re
from langchain.document_loaders import TextLoader, PyPDFLoader, UnstructuredMarkdownLoader, Docx2txtLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from typing_extensions import List,  TypedDict
from langchain_core.documents import Document
import os
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Documentt, Status_Embeddings, Base

# Configuración de Celery
redis_host = os.environ.get("REDISHOST", "redis")
celery_app = Celery('tasks', broker=f"redis://{redis_host}:6379/0")


# Configuración de la base de datos

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str
    collection: str

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

def get_loader(file_path, extension):
    if extension == "txt":
        return TextLoader(file_path, encoding="utf-8")
    elif extension == "pdf":
        return PyPDFLoader(file_path)
    elif extension == "md":
        return UnstructuredMarkdownLoader(file_path)
    elif extension == "docx":
        return Docx2txtLoader(file_path)
    else:
        raise ValueError(f"Unsupported file format: {extension}")


# Crear nuevo usuario
@celery_app.task(name='process.embeddings', queue = "embeddings_queue")
def embbedings(document_id,extension,collection_name):

    file_path = f"/flask_app/uploadedDocuments/processedDocuments/document_{document_id}.{extension}"


    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found!")
    
    loader = get_loader(file_path, extension)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    embeddings = OllamaEmbeddings(
        model="llama3:8b",
        base_url="http://ollama:11434"
    )

    chroma_path = "/chroma_db" 

    Chroma.from_documents(docs, embeddings, persist_directory=chroma_path, collection_name=collection_name)

    print(f"📂 Se han guardado {len(docs)} fragmentos en ChromaDB.")

    session = Session()
    try:
        doc = session.query(Documentt).get(document_id)
        if doc:
            doc.embbedings_status = Status_Embeddings.COMPLETED
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


