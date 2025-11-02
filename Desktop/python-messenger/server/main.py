from flask import Flask, request
from flask_socketio import SocketIO, send

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Словарь для хранения никнеймов
users = {}

@app.route("/")
def index():
    return "Messenger server is running!"

@socketio.on("set_nickname")
def handle_set_nickname(nickname):
    # request.sid — уникальный ID текущего подключения
    users[request.sid] = nickname
    print(f"User {nickname} connected with SID {request.sid}")

@socketio.on("message")
def handle_message(msg):
    sid = request.sid
    nick = users.get(sid, "Unknown")
    print(f"{nick}: {msg}")
    # Рассылаем всем клиентам
    send(f"{nick}: {msg}", broadcast=True)

@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    nick = users.pop(sid, "Unknown")
    print(f"{nick} disconnected")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 3000))  # Replit требует использовать PORT
    socketio.run(app, host="0.0.0.0", port=port)
