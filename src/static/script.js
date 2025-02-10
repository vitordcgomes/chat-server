const SERVER_URL = "http://192.168.15.13:5501"

const username = prompt("Digite seu nome de usuário:")
const room = prompt("Digite o nome da sala:")
let lastMessageTimestamp = 0
const clientId = Date.now().toString()

// Função para entrar na sala
function joinRoom() {
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
        // Atualiza o cabeçalho com o nome da sala
        document.getElementById("chat-header").textContent = `Sala: ${room}`
        // Inicia a verificação de novas mensagens após entrar na sala
        receiveMessages()
      }
    })
    .catch((error) => console.error("Erro:", error))
}

function sendMessage() {
  const messageInput = document.getElementById("message-input")
  const message = messageInput.value.trim()

  if (message) {
    fetch(`${SERVER_URL}/send`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, message, room }),
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
  fetch(`${SERVER_URL}/receive?room=${room}&client_id=${clientId}&last_timestamp=${lastMessageTimestamp}`)
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
      receiveMessages()
    })
}

function leaveRoom() {
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
        console.log(data.message)
        alert("Você saiu da sala.")
        window.location.reload() // Recarrega a página para reiniciar o chat
      }
    })
    .catch((error) => console.error("Erro:", error))
}

// Entra na sala ao carregar a página
joinRoom()

// Adiciona um event listener para enviar mensagens ao pressionar Enter
document.getElementById("message-input").addEventListener("keypress", (event) => {
  if (event.key === "Enter") {
    sendMessage()
  }
})

// Adiciona um event listener para lidar com o fechamento da janela
window.addEventListener("beforeunload", (e) => {
  leaveRoom()
})

