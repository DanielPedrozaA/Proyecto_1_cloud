from app import create_app
from flask_socketio import SocketIO
import os

app = create_app()

# Configuración de Redis para WebSockets
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = os.getenv("REDIS_PORT", "6379")

socketio = SocketIO(app, async_mode="eventlet", message_queue=f"redis://{redis_host}:{redis_port}", cors_allowed_origins="*")

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

# 🔹 Esta es la línea que Gunicorn necesita (¡debe ser un callable!)
app = app

