const SERVER_URL = "http://192.168.15.13:5501"

const username = prompt("Digite seu nome de usuário:")
let activeRoom = null
let userRooms = new Set()
let lastMessageTimestamp = 0
const clientId = Date.now().toString()

// Gerenciamento de salas
function updateRoomsList() {
    const roomsList = document.getElementById('rooms-list')
    roomsList.innerHTML = ''
    
    userRooms.forEach(room => {
        const roomElement = document.createElement('div')
        roomElement.className = `room-item ${room === activeRoom ? 'active' : ''}`
        roomElement.textContent = room
        roomElement.onclick = () => switchRoom(room)
        roomsList.appendChild(roomElement)
    })
}

function switchRoom(room) {
    if (activeRoom === room) return
    
    // Limpa as mensagens da sala anterior
    document.getElementById('chat-messages').innerHTML = ''
    activeRoom = room
    document.getElementById('chat-header').textContent = `Sala: ${room}`
    lastMessageTimestamp = 0
    updateRoomsList()
    
    // Reinicia o polling de mensagens para a nova sala
    receiveMessages()
}

function joinNewRoom() {
    const newRoomInput = document.getElementById('new-room-input')
    const room = newRoomInput.value.trim()
    
    if (room) {
        joinRoom(room)
        newRoomInput.value = ''
    }
}

// Função para entrar na sala
function joinRoom(room) {
    fetch(`${SERVER_URL}/join`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ room, username }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.status === "success") {
                console.log(data.message)
                userRooms.add(room)
                if (!activeRoom) {
                    activeRoom = room
                    receiveMessages()
                }
                updateRoomsList()
                document.getElementById("chat-header").textContent = `Sala: ${activeRoom}`
            }
        })
        .catch((error) => console.error("Erro:", error))
}

function sendMessage() {
    if (!activeRoom) return
    
    const messageInput = document.getElementById("message-input")
    const message = messageInput.value.trim()

    if (message) {
        fetch(`${SERVER_URL}/send`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username, message, room: activeRoom }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.status === "success") {
                    messageInput.value = ""
                }
            })
            .catch((error) => console.error("Erro:", error))
    }
}

function addMessageToChat(sender, message, isSent, timestamp) {
    const chatMessages = document.getElementById("chat-messages")
    const messageElement = document.createElement("div")
    messageElement.classList.add("message")

    if (sender === "system") {
        messageElement.classList.add("system-message")
        messageElement.textContent = message
    } else {
        messageElement.classList.add(isSent ? "message-sent" : "message-received")
        messageElement.textContent = isSent ? message : `${sender}: ${message}`
    }

    chatMessages.appendChild(messageElement)
    chatMessages.scrollTop = chatMessages.scrollHeight

    if (timestamp > lastMessageTimestamp) {
        lastMessageTimestamp = timestamp
    }
}

function receiveMessages() {
    if (!activeRoom) return

    fetch(`${SERVER_URL}/receive?room=${activeRoom}&client_id=${clientId}&last_timestamp=${lastMessageTimestamp}`)
        .then((response) => response.json())
        .then((data) => {
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach((messageData) => {
                    if (messageData.type === "system") {
                        addMessageToChat("system", messageData.message, false, messageData.timestamp)
                    } else {
                        const isSent = messageData.username === username
                        addMessageToChat(messageData.username, messageData.message, isSent, messageData.timestamp)
                    }
                })
            }
        })
        .catch((error) => console.error("Erro:", error))
        .finally(() => {
            // Continua a verificar por novas mensagens imediatamente
            setTimeout(() => receiveMessages(), 1000)
        })
}

function leaveRoom(room) {
    room = room || activeRoom
    if (!room) return

    fetch(`${SERVER_URL}/leave`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ room, username }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.status === "success") {
                userRooms.delete(room)
                if (room === activeRoom) {
                    activeRoom = userRooms.size > 0 ? Array.from(userRooms)[0] : null
                    document.getElementById('chat-messages').innerHTML = ''
                    if (activeRoom) {
                        document.getElementById('chat-header').textContent = `Sala: ${activeRoom}`
                    }
                }
                updateRoomsList()
            }
        })
        .catch((error) => console.error("Erro:", error))
}

function listUsers() {
  if (!activeRoom) {
      alert('Selecione uma sala primeiro');
      return;
  }

  fetch(`${SERVER_URL}/list_users?room=${activeRoom}`)
      .then(response => response.json())
      .then(data => {
          if (data.status === 'success') {
              const usersList = document.getElementById('users-list');
              usersList.innerHTML = '';
              
              data.users.forEach(user => {
                  const li = document.createElement('li');
                  li.textContent = user;
                  if (user === username) {
                      li.textContent += ' (você)';
                      li.style.fontWeight = 'bold';
                  }
                  usersList.appendChild(li);
              });
              
              showUsersModal();
          } else {
              alert('Erro ao listar usuários');
          }
      })
      .catch(error => {
          console.error('Erro:', error);
          alert('Erro ao listar usuários');
      });
}

function showUsersModal() {
  const modal = document.getElementById('users-modal');
  modal.style.display = 'block';
}

function closeUsersModal() {
  const modal = document.getElementById('users-modal');
  modal.style.display = 'none';
}

// Fechar o modal quando clicar fora dele
window.onclick = function(event) {
  const modal = document.getElementById('users-modal');
  if (event.target === modal) {
      modal.style.display = 'none';
  }
}

// Atualizar a lista de usuários periodicamente quando o modal estiver aberto
setInterval(() => {
  const modal = document.getElementById('users-modal');
  if (modal.style.display === 'block') {
      listUsers();
  }
}, 5000);

// Adiciona um event listener para enviar mensagens ao pressionar Enter
document.getElementById("message-input").addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
        sendMessage()
    }
})

// Adiciona um event listener para lidar com o fechamento da janela
window.addEventListener("beforeunload", (e) => {
    userRooms.forEach(room => leaveRoom(room))
})

// Solicita a primeira sala ao iniciar
const initialRoom = prompt("Digite o nome da sala:")
if (initialRoom) {
    joinRoom(initialRoom)
}