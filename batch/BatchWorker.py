# Standard library
import os
import re
import shutil

# Third-party libraries
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from celery import Celery, current_task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing_extensions import List, TypedDict

# Langchain and related libraries
from langchain import hub
from langchain.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    Docx2txtLoader,
)
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
import chromadb

# Local application
from models import Documentt, Status_Embeddings, Base, Status

load_dotenv()

# 🔹 Configuración de Redis
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = os.getenv("REDIS_PORT", "6379")

# 🔹 Configuración de WebSockets
socketio = SocketIO(message_queue=f"redis://{redis_host}:{redis_port}", cors_allowed_origins="*")

# 🔹 Configuración de Celery
celery_app = Celery('tasks', broker="redis://{redis_host}:{redis_port}/0")

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
    else:
        raise ValueError(f"Unsupported file format: {extension}")


# Crear nuevo usuario
def embbedings(document_id,extension,collection_name):

    file_path = f"/flask_app/uploadedDocuments/processedDocuments/document_{document_id}.{extension}"


    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found!")
    
    loader = get_loader(file_path, extension)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(
        model=os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001"),
        google_api_key=os.getenv("GOOGLE_API_KEY")
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


@celery_app.task(name='process.document', queue = "allqueue")
def process_document(file_path, document_id):
    """
    Tarea que simula el procesamiento del documento:
    - Actualiza la base de datos, marcando el documento como COMPLETED.
    """
    print("EJECUTAR COPIAR")

    processed_dir = os.path.join(os.path.dirname(file_path), "processedDocuments")
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
    filename = os.path.basename(file_path)
    destination_path = os.path.join(processed_dir, filename)
    
    shutil.move(file_path, destination_path)

    session = Session()
    try:
        doc = session.query(Documentt).get(document_id)
        if doc:
            doc.status = Status.COMPLETED
            doc.file_path = destination_path
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


class State(TypedDict):
    question: str
    context: List[Document]
    answer: str
    collection: str

def retrieve(state: State):
    chroma_path = os.getenv("CHROMA_DB_PATH", "/chroma_db")  # Cargar ruta desde el .env
    collection_name = state["collection"]

    embeddings = GoogleGenerativeAIEmbeddings(
    model=os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001"),
    google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    vector_store = Chroma(
        persist_directory=chroma_path,
        embedding_function=embeddings,
        collection_name=collection_name
    )

    retrieved_docs = vector_store.similarity_search(state["question"])

    return {"context": retrieved_docs}

def generate(state: State):

    llm = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-pro"),
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    prompt = hub.pull("rlm/rag-prompt")

    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}

def question(data):
    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()

    response = graph.invoke({"question": data["question"], "collection": data["collection"]})

    return {"respuesta": response["answer"]}

# 🔹 Tarea en Segundo Plano con Celery
@celery_app.task(name='process.sms', queue="allqueue", bin=True)
def long_running_task(data):
    chroma_path = "/chroma_db"  # or os.getenv("CHROMA_DB_PATH")
    client = chromadb.PersistentClient(path=chroma_path)


    collections = client.list_collections()
    exists = data["collection"] in collections

    if not exists:
        embbedings(data["id"],data["extension"],data["collection"])

    respuesta = question(data)

    print(respuesta["respuesta"])
    socketio.emit("task_update", {"task_id": current_task.request.id, "message": respuesta["respuesta"]})
    return f"Task completed"
