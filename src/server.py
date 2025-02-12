import time
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Estrutura para armazenar salas, mensagens e usuários ativos
rooms = {}
room_messages = {}

@app.route('/')
def serve_index():
    return send_from_directory(os.path.join(BASE_DIR, 'static'), 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'static'), filename)

@app.route('/join', methods=['POST'])
def join_room():
    data = request.json
    room = data['room']
    username = data['username']

    if room not in rooms:
        rooms[room] = set()
        room_messages[room] = []

    rooms[room].add(username)
    broadcast({'type': 'system', 'message': f"{username} entrou na sala"}, room)

    return jsonify({"status": "success", "message": f"Entrou na sala {room}"})

@app.route('/leave', methods=['POST'])
def leave_room():
    data = request.json
    room = data['room']
    username = data['username']

    if room in rooms and username in rooms[room]:
        rooms[room].remove(username)
        broadcast({'type': 'system', 'message': f"{username} saiu da sala"}, room)
        if not rooms[room]:  # Se não houver usuários, limpa a sala
            del rooms[room]
            del room_messages[room]

        return jsonify({"status": "success", "message": f"Saiu da sala {room}"})

    return jsonify({"status": "error", "message": "Usuário ou sala não encontrados"})

@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    username = data['username']
    message = data['message']
    room = data['room']

    if room in rooms:
        msg_data = {
            'type': 'message',
            'username': username,
            'message': message,
            'timestamp': time.time()
        }
        broadcast(msg_data, room)
        return jsonify({"status": "success"})
    
    return jsonify({"status": "error", "message": "Sala não encontrada"})

@app.route('/receive', methods=['GET'])
def receive_messages():
    room = request.args.get('room')
    last_timestamp = float(request.args.get('last_timestamp', 0))

    if room in room_messages:
        new_messages = [msg for msg in room_messages[room] if msg['timestamp'] > last_timestamp]
        return jsonify({"messages": new_messages})

    return jsonify({"messages": []})

@app.route('/user_rooms', methods=['GET'])
def get_user_rooms():
    username = request.args.get('username')
    user_rooms = [room for room, users in rooms.items() if username in users]
    return jsonify({"rooms": user_rooms})

def broadcast(data, room):
    """Adiciona mensagem ao histórico da sala e envia para os usuários."""
    if room in room_messages:
        data['timestamp'] = time.time()
        room_messages[room].append(data)
        room_messages[room] = room_messages[room][-50:]  # Mantém um histórico limitado para evitar sobrecarga

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5501, debug=True, use_reloader=False)
