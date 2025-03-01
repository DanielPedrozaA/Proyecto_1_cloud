from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from celery import Celery
import time
import os
import re
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langgraph.graph import  START, StateGraph
from typing_extensions import List,  TypedDict
from langchain.chat_models import init_chat_model
from langchain import hub
import os
from langchain_core.documents import Document

# 🔹 Initialize Flask App
app = Flask(__name__)

# 🔹 Add WebSockets (Does NOT break existing routes)
socketio = SocketIO(app, cors_allowed_origins="*")

# 🔹 Configure Celery
app.config["CELERY_BROKER_URL"] = "redis://localhost:6379/0"
app.config["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/0"

# Configuración de Celery
redis_host = os.environ.get("REDISHOST", "redis")
celery_app = Celery('tasks', broker=f"redis://{redis_host}:6379/0")

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str
    collection: str

def retrieve(state: State):

    chroma_path = "/chroma_db"  # Directorio donde se guardaron los embeddings
    collection_name = state["collection"]  # Asegúrate de usar el mismo nombre de colección

    embeddings = OllamaEmbeddings(
        model="llama3:8b",
        base_url="http://ollama:11434"
    )

    vector_store = Chroma(
        persist_directory=chroma_path,
        embedding_function=embeddings,
        collection_name=collection_name
    )

    retrieved_docs = vector_store.similarity_search(state["question"])

    return {"context": retrieved_docs}


def generate(state: State):
    llm = init_chat_model("llama3:8b", model_provider="ollama", base_url="http://ollama:11434")
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


# 🔹 New Route to Start Background Task
@app.route("/start_task", methods=["POST"])
def start_task():
    data = request.json
    duration = data.get("duration", 5)

    task = long_running_task.apply_async(args=[duration])
    return jsonify({"task_id": task.id}), 202

# 🔹 Check Task Status (Optional)
@app.route("/task_status/<task_id>")
def task_status(task_id):
    result = celery.AsyncResult(task_id)
    return jsonify({"task_id": task_id, "status": result.status, "result": result.result})

# 🔹 Celery Background Task
@celery_app.task(name='process.embeddings')
def long_running_task(self, duration):

        

    
    
    socketio.emit("task_update", {"task_id": self.request.id, "state": "FINISHED"})

    return f"Task completed "

# 🔹 WebSocket Connection Events
@socketio.on("connect")
def handle_connect():
    print("Client Connected")

@socketio.on("disconnect")
def handle_disconnect():
    print("Client Disconnected")

# 🔹 Start Flask with WebSockets
if __name__ == "__main__":
    socketio.run(app, debug=True)