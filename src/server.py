import time
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Estrutura para armazenar salas, mensagens e usuários ativos
rooms = {} # Um dicionário onde as chaves são os nomes das salas e os valores são conjuntos de usuários ativos naquela sala.
room_messages = {} # Um dicionário que armazena as mensagens trocadas em cada sala, associando-as por nome.

# Sempre que um usuário acessar a raiz do servidor (http://localhost:5501/), o arquivo index.html será enviado ao navegador.
@app.route('/')
def serve_index():
    """Servir a página inicial (index.html)."""
    return send_from_directory(os.path.join(BASE_DIR, 'static'), 'index.html')

# Isso permite carregar arquivos como CSS, imagens e scripts JavaScript necessários para o funcionamento da interface.
@app.route('/<path:filename>')
def serve_static(filename):
    """Servir arquivos estáticos da pasta 'static'."""
    return send_from_directory(os.path.join(BASE_DIR, 'static'), filename)

@app.route('/join', methods=['POST'])
def join_room():
    """Adicionar um usuário a uma sala de chat.
    
    Requisição:
        - JSON: {"room": "nome_da_sala", "username": "nome_do_usuario"}

    Retorno:
        - JSON com status de sucesso ou erro.
    """
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
    """Remover um usuário de uma sala de chat.
    
    Requisição:
        - JSON: {"room": "nome_da_sala", "username": "nome_do_usuario"}

    Retorno:
        - JSON com status de sucesso ou erro.
    """
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
    """Enviar uma mensagem para uma sala específica.
    
    Requisição:
        - JSON: {"username": "nome_do_usuario", "message": "texto_da_mensagem", "room": "nome_da_sala"}

    Retorno:
        - JSON com status de sucesso ou erro.
    """
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
    """Obter mensagens recentes de uma sala.
    
    Parâmetros:
        - room: Nome da sala (string)
        - last_timestamp: Último timestamp recebido (float, opcional)

    Retorno:
        - JSON: {"messages": [{"type": "message", "username": "user", "message": "texto", "timestamp": float}, ...]}
    """
    room = request.args.get('room')
    last_timestamp = float(request.args.get('last_timestamp', 0))

    if room in room_messages:
        new_messages = [msg for msg in room_messages[room] if msg['timestamp'] > last_timestamp]
        return jsonify({"messages": new_messages})

    return jsonify({"messages": []})

@app.route('/user_rooms', methods=['GET'])
def get_user_rooms():
    """Retorna uma lista de salas em que um usuário está presente.
    
    Parâmetros:
        - username: Nome do usuário (string)

    Retorno:
        - JSON: {"rooms": ["sala1", "sala2", ...]}
    """
    username = request.args.get('username')
    user_rooms = [room for room, users in rooms.items() if username in users]
    return jsonify({"rooms": user_rooms})

def broadcast(data, room):
    """Adiciona uma mensagem ao histórico da sala e limita a 50 mensagens.
    
    Parâmetros:
        - data: Dicionário contendo a mensagem.
        - room: Nome da sala.
    """
    if room in room_messages:
        data['timestamp'] = time.time()
        room_messages[room].append(data)
        room_messages[room] = room_messages[room][-50:]  # Mantém um histórico limitado para evitar sobrecarga

if __name__ == '__main__':
    app.run(host="localhost", port=5501, debug=True, use_reloader=False)
