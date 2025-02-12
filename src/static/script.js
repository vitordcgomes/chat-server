const SERVER_URL = "http://localhost:5501";

const username = prompt("Digite seu nome de usuário:");
let currentRoom = null;
let rooms = [];
const lastMessageTimestamps = {};
const clientId = Date.now().toString();

function updateRoomList() {
  fetch(`${SERVER_URL}/user_rooms?username=${username}`)
    .then((response) => response.json())
    .then((data) => {
      rooms = data.rooms;
      const roomList = document.getElementById("room-list");
      roomList.innerHTML = "";
      rooms.forEach((room) => {
        const li = document.createElement("li");
        li.textContent = room;
        li.onclick = () => switchRoom(room);
        if (room === currentRoom) {
          li.classList.add("active");
        }
        roomList.appendChild(li);
      });
    });
}

function switchRoom(room) {
  if (currentRoom !== room) {
    currentRoom = room;
    document.getElementById("chat-header").textContent = `Sala: ${room}`;
    document.getElementById("chat-messages").innerHTML = ""; // Limpa mensagens apenas ao trocar de sala
    lastMessageTimestamps[currentRoom] = 0; // Reseta o timestamp para buscar todas as mensagens
    updateRoomList();
    receiveMessages(); // Chama a função para carregar mensagens antigas
  }
}

function addMessageToChat(sender, message, isSent, timestamp) {
  const chatMessages = document.getElementById("chat-messages");
  const messageElement = document.createElement("div");

  if (sender === "system" || sender === null || sender === undefined) {
    messageElement.classList.add("system-message");
    messageElement.textContent = message; // Exibe a mensagem centralizada sem prefixo
  } else {
    messageElement.classList.add("message");
    messageElement.classList.add(isSent ? "message-sent" : "message-received");
    messageElement.textContent = isSent ? message : `${sender}: ${message}`;
  }

  chatMessages.appendChild(messageElement);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  if (timestamp > (lastMessageTimestamps[currentRoom] || 0)) {
    lastMessageTimestamps[currentRoom] = timestamp;
  }
}

function receiveMessages() {
  if (!currentRoom) return;

  fetch(`${SERVER_URL}/receive?room=${currentRoom}&last_timestamp=${lastMessageTimestamps[currentRoom] || 0}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.messages && data.messages.length > 0) {
        data.messages.forEach((messageData) => {
          if (messageData.timestamp > (lastMessageTimestamps[currentRoom] || 0)) {
            const isSent = messageData.username === username;
            addMessageToChat(messageData.username, messageData.message, isSent);
            lastMessageTimestamps[currentRoom] = messageData.timestamp; // Atualiza timestamp
          }
        });
      }
    })
    .catch((error) => console.error("Erro ao receber mensagens:", error))
    .finally(() => {
      setTimeout(receiveMessages, 1000);
    });
}

function sendMessage() {
  const messageInput = document.getElementById("message-input");
  const message = messageInput.value.trim();

  if (message && currentRoom) {
    fetch(`${SERVER_URL}/send`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, message, room: currentRoom }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          messageInput.value = "";
        }
      })
      .catch((error) => console.error("Erro ao enviar mensagem:", error));
  }
}

document.getElementById("message-input").addEventListener("keypress", (event) => {
  if (event.key === "Enter") {
    sendMessage();
  }
});

document.getElementById("join-room").addEventListener("click", () => {
  const room = prompt("Digite o nome da sala:");
  if (room) {
    fetch(`${SERVER_URL}/join`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ room, username }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          updateRoomList();
          switchRoom(room);
        }
      })
      .catch((error) => console.error("Erro ao entrar na sala:", error));
  }
});

document.getElementById("leave-room").addEventListener("click", () => {
  if (currentRoom) {
    fetch(`${SERVER_URL}/leave`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ room: currentRoom, username }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          updateRoomList();
          currentRoom = null;
          document.getElementById("chat-header").textContent = "Nenhuma sala selecionada";
          document.getElementById("chat-messages").innerHTML = "";
        }
      })
      .catch((error) => console.error("Erro ao sair da sala:", error));
  } else {
    alert("Você não está em nenhuma sala.");
  }
});

updateRoomList();
setInterval(updateRoomList, 5000);
