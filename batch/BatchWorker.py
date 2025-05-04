# Standard library
import os
import re
import shutil
import json
import base64
import tempfile
import io
from typing import Optional

# Third-party libraries
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from google.cloud import pubsub_v1
from google.cloud import storage
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing_extensions import List, TypedDict
import threading

# Langchain and related libraries (con importaciones actualizadas)
from langchain import hub
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    Docx2txtLoader,
)
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
import pickle

# Local application
from models import Documentt, Status_Embeddings, Base, Status
from smb.SMBConnection import SMBConnection
import tempfile

load_dotenv()

# 🔹 Configuración de WebSockets
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 🔹 Configuración de Google Cloud
project_id = os.getenv("GCP_PROJECT_ID", "desarollo-de-soluciones-cloud")
gcs_bucket_name = os.getenv("GCS_BUCKET_NAME", "ultra-pro-bucket")
gcs_embeddings_bucket_name = os.getenv("GCS_BUCKET_EMBEDDINGS_NAME", "chimba-embeddings")
pubsub_topic = os.getenv("PUBSUB_TOPIC", "rag-tasks")
pubsub_subscription = os.getenv("PUBSUB_SUBSCRIPTION", "rag-worker-subscription")
pubsub_results_topic = os.getenv("PUBSUB_RESULTS_TOPIC", "rag-results")

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
SMB_SERVER = os.environ.get("SMB_SERVER")  # IP o hostname de la VM que tiene el sistema de archivos
SMB_PORT = int(os.environ.get("SMB_PORT", "445"))
SMB_USERNAME = os.environ.get("SMB_USERNAME")
SMB_PASSWORD = os.environ.get("SMB_PASSWORD")
SMB_SHARE = os.environ.get("SMB_SHARE")  # Nombre del recurso compartido en la VM remota
SMB_DIRECTORY = os.environ.get("SMB_DIRECTORY", "uploadedDocuments")  # Directorio dentro del recurso compartido
MY_NAME = os.environ.get("MY_NAME", "backend")  # Nombre del cliente para la conexión SMB
REMOTE_NAME = os.environ.get("REMOTE_NAME", "fileserver")  # Nombre de la VM remota en la red

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_loader(file_input, extension):
    """
    Si file_input es una ruta (str), se utiliza directamente.
    Si es un objeto file-like (por ejemplo, io.BytesIO), se escribe su contenido en un archivo temporal.
    """
    # Si ya es una ruta, úsala tal cual.
    if isinstance(file_input, str):
        file_path = file_input
    else:
        # Se asume que es un objeto file-like
        suffix = f".{extension}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_input.read())
            file_path = tmp.name
        # Reinicia el puntero del objeto, por si se necesita más adelante.
        file_input.seek(0)

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

def download_from_gcs(document_id, extension):
    """Descarga un archivo desde Google Cloud Storage"""
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(gcs_bucket_name)
    blob = bucket.blob(f"document_{document_id}.{extension}")
    
    file_obj = io.BytesIO()
    blob.download_to_file(file_obj)
    file_obj.seek(0)
    
    return file_obj

def upload_embeddings_to_gcs(collection_name, embeddings_data):
    """Sube los embeddings a Google Cloud Storage"""
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(gcs_embeddings_bucket_name)
    blob = bucket.blob(f"{collection_name}_embeddings.pkl")
    
    # Serializamos los embeddings
    pickled_data = pickle.dumps(embeddings_data)
    blob.upload_from_string(pickled_data)
    
    print(f"📂 Embeddings para {collection_name} guardados en GCS bucket: {gcs_embeddings_bucket_name}")

def download_embeddings_from_gcs(collection_name):
    """Descarga los embeddings desde Google Cloud Storage"""
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(gcs_embeddings_bucket_name)
    blob = bucket.blob(f"{collection_name}_embeddings.pkl")
    
    if not blob.exists():
        return None
    
    # Deserializamos los embeddings
    pickled_data = blob.download_as_bytes()
    embeddings_data = pickle.loads(pickled_data)
    
    return embeddings_data

def embbedings(document_id, extension, collection_name):
    try:
        # Descargamos el documento de GCS en lugar de SMB
        file_obj = download_from_gcs(document_id, extension)

        loader = get_loader(file_obj, extension)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs = text_splitter.split_documents(documents)

        embeddings = GoogleGenerativeAIEmbeddings(
            model=os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001"),
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

        # Crear los embeddings
        embeddings_data = {}
        for i, doc in enumerate(docs):
            vector = embeddings.embed_query(doc.page_content)
            embeddings_data[i] = {
                "text": doc.page_content,
                "metadata": doc.metadata,
                "embedding": vector
            }

        # Guardar los embeddings en GCS
        upload_embeddings_to_gcs(collection_name, embeddings_data)

        print(f"📂 Se han generado y guardado {len(docs)} fragmentos de embeddings.")

        # Actualizar estado en la base de datos
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

        return True
    except Exception as e:
        print(f"Error al generar embeddings: {str(e)}")
        return False

def retrieve(state: State):
    collection_name = state["collection"]
    
    # Obtener embeddings desde GCS
    embeddings_data = download_embeddings_from_gcs(collection_name)
    
    if not embeddings_data:
        return {"context": []}
    
    # Crear embedding para la pregunta
    embeddings_model = GoogleGenerativeAIEmbeddings(
        model=os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001"),
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    query_embedding = embeddings_model.embed_query(state["question"])
    
    # Búsqueda de similitud simple
    similarities = []
    for idx, item in embeddings_data.items():
        doc_embedding = item["embedding"]

        # Cálculo de similitud de coseno
        dot_product = sum(a * b for a, b in zip(query_embedding, doc_embedding))
        magnitude_a = sum(a * a for a in query_embedding) ** 0.5
        magnitude_b = sum(b * b for b in doc_embedding) ** 0.5
        similarity = dot_product / (magnitude_a * magnitude_b) if magnitude_a * magnitude_b > 0 else 0

        similarities.append((idx, similarity))
    
    # Ordenar por similitud y tomar los 4 mejores resultados
    top_results = sorted(similarities, key=lambda x: x[1], reverse=True)[:4]
    
    # Convertir a documentos de LangChain
    retrieved_docs = []
    for idx, score in top_results:
        item = embeddings_data[idx]
        doc = Document(page_content=item["text"], metadata=item["metadata"])
        retrieved_docs.append(doc)
    
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

# 🔹 Procesamiento de mensajes de Pub/Sub
def process_task(data):
    try:
        collection_exists = check_if_collection_exists(data["collection"])
        
        if not collection_exists:
            try:
                if not embbedings(data["id"], data["extension"], data["collection"]):
                    raise ValueError("Fallo al generar embeddings")
            except Exception as e:
                print(f"Error generando embeddings: {str(e)}")
                raise

        try:
            respuesta = question(data)
        except Exception as e:
            print(f"Error generando respuesta: {str(e)}")
            raise

        try:
            publish_result(data["task_id"], respuesta["respuesta"])
        except Exception as e:
            print(f"Error publicando resultado: {str(e)}")
            raise

        return respuesta["respuesta"]

    except Exception as e:
        print(f"Error en process_task: {str(e)}")
        raise

def check_if_collection_exists(collection_name):
    """Verifica si existe una colección de embeddings en GCS"""
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(gcs_embeddings_bucket_name)
    blob = bucket.blob(f"{collection_name}_embeddings.pkl")
    
    return blob.exists()

def publish_result(task_id, result):
    """Publica el resultado en el tema de resultados de Pub/Sub"""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, pubsub_results_topic)
    
    message_data = {
        "task_id": task_id,
        "result": result
    }
    
    message_bytes = json.dumps(message_data).encode("utf-8")
    publisher.publish(topic_path, data=message_bytes)
    print(f"Resultado publicado para la tarea {task_id}")

def start_pubsub_subscriber():
    """Inicia un suscriptor para escuchar mensajes de Pub/Sub"""
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, pubsub_subscription)
    
    def callback(message):
        try:
            message_data = json.loads(message.data.decode("utf-8"))
            print(f"Mensaje recibido: {message_data}")
            process_task(message_data)
            message.ack()
        except Exception as e:
            print(f"Error al procesar el mensaje: {str(e)}")
            message.nack()
    
    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=callback
    )
    print(f"Escuchando mensajes en {subscription_path}...")
    
    try:
        streaming_pull_future.result()
    except Exception as e:
        streaming_pull_future.cancel()
        print(f"Error en el suscriptor: {str(e)}")

if __name__ == "__main__":
    subscriber_thread = threading.Thread(target=start_pubsub_subscriber)
    subscriber_thread.daemon = True
    subscriber_thread.start()

    print("Iniciando worker de Pub/Sub...")

