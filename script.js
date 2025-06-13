let conversationHistory = []; // Global history variable

document.addEventListener('DOMContentLoaded', () => {
  const messageArea = document.getElementById('messageArea');
  const messageInput = document.getElementById('messageInput');
  const sendButton = document.getElementById('sendButton');

  // appendMessage function remains largely the same, responsible for rendering one message
  function appendMessage(sender, type, content) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender === 'user' ? 'user-message' : 'assistant-message');

    switch (type) {
      case 'text':
        messageDiv.textContent = content;
        break;
      case 'image':
        const img = document.createElement('img');
        img.src = content; // content is the URL
        img.alt = "Assistant Image";
        img.style.maxWidth = '100%';
        img.style.height = 'auto';
        img.style.borderRadius = '8px'; // Match chat bubble style
        img.onload = () => { messageArea.scrollTop = messageArea.scrollHeight; };
        img.onerror = () => {
            messageDiv.textContent = "Error loading image: " + content;
            messageArea.scrollTop = messageArea.scrollHeight;
        };
        messageDiv.appendChild(img);
        break;
      case 'list':
        const listElement = document.createElement('ul');
        listElement.style.listStylePosition = 'inside';
        listElement.style.paddingLeft = '20px';
        if (Array.isArray(content)) {
            content.forEach(itemText => {
                const listItem = document.createElement('li');
                listItem.textContent = itemText;
                listElement.appendChild(listItem);
            });
        } else if (typeof content === 'object' && content !== null) {
            for (const key in content) {
                if (Object.prototype.hasOwnProperty.call(content, key)) {
                    const mainListItem = document.createElement('li');
                    mainListItem.textContent = key + ':';
                    if (Array.isArray(content[key])) {
                        const subListElement = document.createElement('ul');
                        subListElement.style.paddingLeft = '20px';
                        content[key].forEach(program => {
                            const subListItem = document.createElement('li');
                            subListItem.textContent = program;
                            subListElement.appendChild(subListItem);
                        });
                        mainListItem.appendChild(subListElement);
                    } else {
                        const subText = document.createElement('span');
                        subText.textContent = ' ' + content[key];
                        mainListItem.appendChild(subText);
                    }
                    listElement.appendChild(mainListItem);
                }
            }
        } else {
            messageDiv.textContent = "Received a list with invalid format.";
        }
        messageDiv.appendChild(listElement);
        break;
      case 'error':
        messageDiv.textContent = `Error: ${content}`;
        messageDiv.classList.add('error-message');
        break;
      default:
        messageDiv.textContent = `Received an unknown response type: ${type || 'undefined'}`;
        break;
    }
    messageArea.appendChild(messageDiv);
    // Defer scroll until after current execution context, allowing DOM to update
    setTimeout(() => { messageArea.scrollTop = messageArea.scrollHeight; }, 0);
  }

  function renderChatHistory() {
    messageArea.innerHTML = ''; // Clear existing messages
    conversationHistory.forEach(msg => {
      appendMessage(msg.sender, msg.type || 'text', msg.content);
    });
  }

  async function callChatAPI(newMessageText) {
    // Show a temporary "Thinking..." message for immediate feedback
    // This will be cleared on the next full re-render
    if (newMessageText !== null) { // Don't show "Thinking..." for initial load
        appendMessage('assistant', 'text', 'Traitement en cours...');
    }

    const payload = {
      history: conversationHistory,
      newMessage: newMessageText // Can be null for initial load
    };

    try {
      const response = await fetch('http://127.0.0.1:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        let errorContent = `Request failed: ${response.status}`;
        try {
          const errorData = await response.json();
          errorContent = (errorData && errorData.content) ? errorData.content : errorContent;
        } catch (e) { /* Ignore if error response is not JSON */ }
        throw new Error(errorContent);
      }

      const data = await response.json();

      if (data.updated_history) {
        conversationHistory = data.updated_history;
      } else {
        // If backend doesn't send back full history, manually add AI response to current history
        // This is a fallback, ideally backend sends complete history
        if (data.ui_response) {
             conversationHistory.push({sender: 'assistant', type: data.ui_response.type, content: data.ui_response.content});
        } else {
            throw new Error("Received no valid response or history from server.");
        }
      }
      renderChatHistory();

    } catch (error) {
      // Remove the temporary "Thinking..." if it's the last message.
      // This is a bit simplistic; a better way would be to give status messages IDs.
      const lastMessageDiv = messageArea.lastElementChild;
      if (lastMessageDiv && lastMessageDiv.textContent === 'Traitement en cours...') {
          lastMessageDiv.remove();
      }
      appendMessage('assistant', 'error', error.message || 'A network error occurred, or the server is unreachable.');
      console.error('Fetch error details:', error);
    }
  }

  function handleSendMessage() {
    const messageText = messageInput.value.trim();
    if (messageText) {
      // Add user message to history immediately for responsiveness (optional, server is source of truth)
      // conversationHistory.push({ sender: 'user', type: 'text', content: messageText });
      // renderChatHistory(); // Optional: render user message immediately

      callChatAPI(messageText);
      messageInput.value = '';
    }
  }

  async function loadInitialMessage() {
    // Call API with null newMessage to signify initial load and get welcome message
    await callChatAPI(null);
  }

  sendButton.addEventListener('click', handleSendMessage);
  messageInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
      handleSendMessage();
    }
  });

  loadInitialMessage(); // Load welcome message on page start
});
