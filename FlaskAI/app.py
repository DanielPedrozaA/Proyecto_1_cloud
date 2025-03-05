from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from celery import Celery, current_task
import os
from dotenv import load_dotenv  # Cargar variables del .env
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain.chat_models import init_chat_model
from langchain import hub
from langchain_core.documents import Document
from flask_cors import CORS

load_dotenv()

# 🔹 Inicializar Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv("CORS_ORIGINS", "*")}}, supports_credentials=True)

# 🔹 Configuración de Redis
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = os.getenv("REDIS_PORT", "6379")

# 🔹 Configuración de WebSockets
socketio = SocketIO(app, message_queue=f"redis://{redis_host}:{redis_port}", cors_allowed_origins="*")
socketIO = SocketIO(message_queue=f"redis://{redis_host}:{redis_port}", cors_allowed_origins="*")

# 🔹 Configuración de Celery
app.config["CELERY_BROKER_URL"] = os.getenv("CELERY_BROKER_URL", f"redis://{redis_host}:{redis_port}/0")
app.config["CELERY_RESULT_BACKEND"] = os.getenv("CELERY_RESULT_BACKEND", f"redis://{redis_host}:{redis_port}/0")

celery_app = Celery('tasks', broker=app.config["CELERY_BROKER_URL"])

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str
    collection: str

def retrieve(state: State):
    chroma_path = os.getenv("CHROMA_DB_PATH", "/chroma_db")  # Cargar ruta desde el .env
    collection_name = state["collection"]

    embeddings = OllamaEmbeddings(
        model=os.getenv("OLLAMA_MODEL", "llama:8b"),
        base_url=os.getenv("OLLAMA_URL", "http://ollama:11434")
    )

    vector_store = Chroma(
        persist_directory=chroma_path,
        embedding_function=embeddings,
        collection_name=collection_name
    )

    retrieved_docs = vector_store.similarity_search(state["question"])

    return {"context": retrieved_docs}

def generate(state: State):
    llm = init_chat_model(
        os.getenv("OLLAMA_MODEL", "llama3:8b"),
        model_provider="ollama",
        base_url=os.getenv("OLLAMA_URL", "http://ollama:11434")
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

# 🔹 Nueva Ruta para Iniciar una Tarea en Segundo Plano
@app.route("/start_task", methods=["POST"])
def start_task():
    data = request.json
    socketio.emit("task_update", {"state": "READY"})
    task = celery_app.send_task('process.sms', queue="sms_queue", args=[data])
    return jsonify({"task_id": task.id}), 202

# 🔹 Comprobar el Estado de una Tarea
@app.route("/task_status/<task_id>")
def task_status(task_id):
    result = celery_app.AsyncResult(task_id)
    return jsonify({"task_id": task_id, "status": result.status, "result": result.result})

# 🔹 Tarea en Segundo Plano con Celery
@celery_app.task(name='process.sms', queue="sms_queue", bin=True)
def long_running_task(data):
    respuesta = question(data)
    socketIO.emit("task_update", {"task_id": current_task.request.id, "message": respuesta["respuesta"]})
    return f"Task completed"

# 🔹 Eventos de Conexión WebSocket
@socketio.on("connect")
def handle_connect():
    print("Client Connected")

@socketio.on("disconnect")
def handle_disconnect():
    print("Client Disconnected")

# 🔹 Iniciar Flask con WebSockets
if __name__ == "__main__":
    socketio.run(app, debug=True)