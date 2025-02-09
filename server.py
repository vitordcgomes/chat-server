import threading
import socket

# Dicionário para armazenar salas e seus respectivos clientes
chat_rooms = {}
lock = threading.Lock()

def handle_client(client, addr):
    try:
        client.send(b'Escolha uma sala para entrar (ou crie uma nova): ')
        room_name = client.recv(1024).decode().strip()
        
        with lock:
            if room_name not in chat_rooms:
                chat_rooms[room_name] = []
            chat_rooms[room_name].append(client)
        
        client.send(f'Entrou na sala: {room_name}\n'.encode())
        broadcast(room_name, f'Usuário {addr} entrou na sala.\n', client)
        
        while True:
            msg = client.recv(2048)
            if not msg or msg.decode().strip().lower() == '/exit':
                break
            broadcast(room_name, msg.decode(), client)
    except:
        pass
    finally:
        remove_client(room_name, client, addr)
        client.close()

def broadcast(room_name, msg, sender):
    with lock:
        if room_name in chat_rooms:
            for client in chat_rooms[room_name]:
                if client != sender:
                    try:
                        client.send(msg.encode())
                    except:
                        remove_client(room_name, client, None)

def remove_client(room_name, client, addr):
    with lock:
        if room_name in chat_rooms and client in chat_rooms[room_name]:
            chat_rooms[room_name].remove(client)
            if not chat_rooms[room_name]:
                del chat_rooms[room_name]
        if addr:
            broadcast(room_name, f'Usuário {addr} saiu da sala.\n', client)

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 1234))
    server.listen()
    print("Servidor iniciado na porta 1234")
    
    while True:
        client, addr = server.accept()
        print(f'Novo cliente conectado: {addr}')
        threading.Thread(target=handle_client, args=(client, addr)).start()

if __name__ == '__main__':
    main()
