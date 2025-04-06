from app import create_app
import os
from flask_socketio import SocketIO

app = create_app()

# 🔹 Configuración de Redis
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = os.getenv("REDIS_PORT", "6379")

# 🔹 Configuración de WebSockets
socketio = SocketIO(app, async_mode="eventlet", message_queue=f"redis://{redis_host}:{redis_port}", cors_allowed_origins="*")

@socketio.on("connect")
def handle_connect():
    print("Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")

@socketio.on("custom_event")
def handle_custom_event(data):
    print("Received data:", data)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)