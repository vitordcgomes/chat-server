# Chat Server com Flask

Este projeto é um servidor de chat desenvolvido em Python utilizando o framework Flask. Ele permite a criação de salas de bate-papo, envio e recebimento de mensagens em tempo real, além de uma interface web para interação.

## Tecnologias Utilizadas

- **Python 3**
- **Flask** - Framework para criar o servidor web
- **Flask-CORS** - Para permitir requisições cross-origin
- **JavaScript** (Frontend) - Para comunicação com o backend via API
- **HTML/CSS** - Interface web para o chat

## Estrutura do Projeto

```
/chat-server
│── server.py          # Servidor Flask
│── requirements.txt   # Lista de dependências
│── static/            # Arquivos estáticos (HTML, JS, CSS)
│   ├── index.html     # Interface do chat
│   ├── script.js      # Lógica frontend para comunicação com o servidor
```

## Como Rodar o Servidor

### 1. Instalar Dependências
Antes de rodar o servidor, instale as dependências necessárias executando:
```sh
pip install -r requirements.txt
```

### 2. Executar o Servidor
Para iniciar o servidor, utilize o comando no diretório /src:
```sh
cd src
python3 server.py
```
O servidor estará rodando em `http://localhost:5501`.

### 3. Acessar o Chat
Abra `http://localhost:5501` no navegador para acessar a interface do chat.

## Funcionamento do Código

### Servidor Flask
O `server.py` implementa um servidor Flask que gerencia as interações entre os usuários e o sistema de salas de chat. Ele mantém o estado das salas e mensagens em memória, permitindo que múltiplos usuários interajam sem necessidade de um banco de dados.

As principais rotas do servidor são:
- **`/join` (POST)**: Um usuário pode se juntar a uma sala especificada. Se a sala não existir, ela é criada. O usuário recebe uma confirmação de entrada na sala.
- **`/leave` (POST)**: Remove um usuário de uma sala. Se a sala ficar vazia, ela é automaticamente removida do sistema.
- **`/send` (POST)**: Envia uma mensagem para uma sala específica. A mensagem é armazenada no histórico e enviada para os demais usuários.
- **`/receive` (GET)**: Recupera todas as mensagens enviadas para uma sala desde o último timestamp armazenado pelo cliente.
- **`/user_rooms` (GET)**: Retorna a lista de salas das quais um usuário faz parte.
- **`/` (GET)**: Retorna a página HTML principal.
- **`/<path:filename>` (GET)**: Fornece arquivos estáticos como JavaScript e CSS.

O servidor mantém um histórico de até 50 mensagens por sala, evitando sobrecarga de memória.

### Conexão entre `script.js` e `server.py`
O frontend implementado em `script.js` interage com o servidor Flask através de requisições HTTP utilizando `fetch()`. Ele realiza as seguintes funções:
- **Atualização da lista de salas**: Periodicamente, o frontend consulta a API (`/user_rooms`) para listar as salas disponíveis.
- **Entrada e saída de salas**: Quando um usuário entra em uma sala, um pedido POST é enviado para `/join`. Ao sair, um pedido POST é enviado para `/leave`.
- **Envio de mensagens**: Quando uma mensagem é enviada, um pedido POST é feito para `/send`.
- **Recebimento de mensagens**: A cada segundo, uma requisição GET é feita para `/receive` para buscar novas mensagens, simulando comunicação em tempo real.

## Escolhas de Implementação

- **Uso de Flask:** Foi escolhido por sua simplicidade e facilidade de configuração para aplicações web.
- **Histórico limitado a 50 mensagens por sala:** Isso evita consumo excessivo de memória e garante melhor performance.
- **Uso de Flask-CORS:** Permite que a interface frontend, rodando em um host diferente, possa se comunicar com o servidor.
- **Mensagens armazenadas em memória:** Para manter a aplicação leve e de fácil manutenção, mas pode ser substituído por um banco de dados em produção.

## Possíveis Melhorias

- **Persistência de dados:** Implementação de um banco de dados para armazenar mensagens e usuários.
- **Autenticação de usuários:** Adicionar um sistema de login para garantir maior controle sobre os usuários.
- **WebSockets:** Substituir o polling por WebSockets para comunicação em tempo real mais eficiente.
- **Interface aprimorada:** Melhorar o design e usabilidade da interface do chat -> incluir lista de usuários no chat, por exemplo.
- **Desdobramento para produção:** Configurar o servidor para rodar em ambientes como AWS, Heroku ou DigitalOcean.

## Observações
- O servidor está configurado para rodar localmente, mas pode ser adaptado para produção.
- O histórico de mensagens de cada sala é armazenado temporariamente e limitado a 50 mensagens para evitar sobrecarga de memória.

