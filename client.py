import threading
import socket

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('localhost', 1234))
    except:
        return print('\nNão foi possível se conectar ao servidor!\n')
    
    room_name = input('Escolha uma sala para entrar (ou crie uma nova): ')
    client.send(room_name.encode())
    
    username = input('Usuário> ')
    print('\nConectado')
    
    thread1 = threading.Thread(target=receive_messages, args=[client])
    thread2 = threading.Thread(target=send_messages, args=[client, username])
    
    thread1.start()
    thread2.start()

def receive_messages(client):
    while True:
        try:
            msg = client.recv(2048).decode('utf-8')
            print(msg+'\n')
        except:
            print('\nNão foi possível permanecer conectado no servidor!\n')
            print('Pressione <Enter> para continuar...')
            client.close()
            break

def send_messages(client, username):
    while True:
        try:
            msg = input('\n')
            if msg.lower() == '/exit':
                client.send(msg.encode())
                break
            client.send(f'<{username}> {msg}'.encode('utf-8'))
        except:
            return

if __name__ == '__main__':
    main()
