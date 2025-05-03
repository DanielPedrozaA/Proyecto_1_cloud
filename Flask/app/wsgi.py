from app import create_app
from flask_socketio import SocketIO
from google.cloud import pubsub_v1
import os

app = create_app()

# Configuración de Google Cloud Pub/Sub para WebSockets
project_id = os.getenv("GCP_PROJECT_ID")  # ID de tu proyecto en Google Cloud
subscription_id = os.getenv("GCP_SUBSCRIPTION_ID")  # ID de la suscripción a Pub/Sub

# Configuración de Pub/Sub
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

# Configuración de SocketIO para trabajar con Pub/Sub
socketio = SocketIO(app, async_mode="eventlet", message_queue=subscription_path, cors_allowed_origins="*")

# Eventos WebSocket
@socketio.on("connect")
def handle_connect():
    print("Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")

@socketio.on("custom_event")
def handle_custom_event(data):
    print("Received data:", data)

# Esta es la línea que Gunicorn necesita (¡debe ser un callable!)
app = app
