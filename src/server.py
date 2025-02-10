import threading
import socket
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import send_from_directory
import json
import time
import os 


app = Flask(__name__)
CORS(app)

# Obtém o diretório atual do script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Servindo a página principal
@app.route('/')
def serve_index():
    return send_from_directory(os.path.join(BASE_DIR, 'static'), 'index.html')

# Servindo arquivos estáticos corretamente
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'static'), filename)


# Dicionário de salas, onde cada sala é uma lista de clientes
rooms = {}

# Dicionário de mensagens para cada sala
room_messages = {}

# Dicionário de timestamps da última mensagem para cada cliente
last_message_timestamps = {}

# Função para lidar com as mensagens de um cliente
def handle_client(client, room):
    while True:
        try:
            msg = client.recv(2048).decode('utf-8')
            data = json.loads(msg)
            if data['type'] == 'message':
                broadcast(data, client, room)
            elif data['type'] == 'join':
                broadcast({'type': 'system', 'message': f"{data['username']} entrou na sala"}, client, room)
            elif data['type'] == 'leave':
                broadcast({'type': 'system', 'message': f"{data['username']} saiu da sala"}, client, room)
                remove_client(client, room)
                break
        except:
            remove_client(client, room)
            break

# Função para transmitir mensagens para todos os clientes em uma sala
def broadcast(data, sender, room):
    if room in rooms:
        timestamp = time.time()
        data['timestamp'] = timestamp
        room_messages[room].append(data)
        for client in rooms[room]:
            try:
                client.send(json.dumps(data).encode('utf-8'))
            except:
                remove_client(client, room)

# Função para remover um cliente de uma sala
def remove_client(client, room):
    if room in rooms and client in rooms[room]:
        rooms[room].remove(client)
        client.close()

# Rota para entrar em uma sala
@app.route('/join', methods=['POST'])
def join_room():
    data = request.json
    room = data['room']
    username = data['username']
    if room not in rooms:
        rooms[room] = []
        room_messages[room] = []
    broadcast({'type': 'system', 'message': f"{username} entrou na sala"}, None, room)
    return jsonify({"status": "success", "message": f"Joined room {room}"})

# Rota para sair de uma sala
@app.route('/leave', methods=['POST'])
def leave_room():
    data = request.json
    room = data['room']
    username = data['username']
    if room in rooms:
        broadcast({'type': 'system', 'message': f"{username} saiu da sala"}, None, room)
        return jsonify({"status": "success", "message": f"Left room {room}"})
    return jsonify({"status": "error", "message": "Room not found"})

# Rota para enviar mensagens
@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    username = data['username']
    message = data['message']
    room = data['room']
    if room in rooms:
        broadcast({'type': 'message', 'username': username, 'message': message}, None, room)
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Room not found"})

# Rota para receber mensagens (long-polling)
@app.route('/receive', methods=['GET'])
def receive_messages():
    room = request.args.get('room')
    client_id = request.args.get('client_id')
    last_timestamp = float(request.args.get('last_timestamp', 0))
    
    if room in room_messages:
        new_messages = [msg for msg in room_messages[room] if msg['timestamp'] > last_timestamp]
        if new_messages:
            return jsonify({"messages": new_messages})
        else:
            # Espera por novas mensagens por até 20 segundos
            start_time = time.time()
            while time.time() - start_time < 20:
                new_messages = [msg for msg in room_messages[room] if msg['timestamp'] > last_timestamp]
                if new_messages:
                    return jsonify({"messages": new_messages})
                time.sleep(0.5)
    
    return jsonify({"messages": []})

# Função principal
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("Iniciou o servidor de bate-papo")

    try:
        server.bind(("192.168.15.13", 5500))
        server.listen()
    except:
        return print('\nNão foi possível iniciar o servidor!\n')

    def accept_clients():
        while True:
            client, addr = server.accept()
            print(f'Cliente conectado com sucesso. IP: {addr}')

            # Aguarda o cliente enviar o nome da sala
            data = json.loads(client.recv(1024).decode('utf-8'))
            room = data['room']
            username = data['username']
            if room not in rooms:
                rooms[room] = []
                room_messages[room] = []
            rooms[room].append(client)

            # Inicia uma nova thread para lidar com as mensagens do cliente
            thread = threading.Thread(target=handle_client, args=(client, room))
            thread.start()

    # Inicia uma thread para aceitar clientes
    threading.Thread(target=accept_clients).start()

    # Inicia o servidor Flask
    app.run(host="0.0.0.0", port=5501, debug=True, use_reloader=False)

# Executa o programa
if __name__ == '__main__':
    main()

