document.addEventListener('DOMContentLoaded', () => {
  const messageArea = document.getElementById('messageArea');
  const messageInput = document.getElementById('messageInput');
  const sendButton = document.getElementById('sendButton');

  function appendMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender === 'user' ? 'user-message' : 'assistant-message');
    messageDiv.textContent = text;
    messageArea.appendChild(messageDiv);
    messageArea.scrollTop = messageArea.scrollHeight; // Scroll to the latest message
  }

  function handleSendMessage() {
    const messageText = messageInput.value.trim();
    if (messageText) {
      appendMessage(messageText, 'user');
      messageInput.value = '';

      // Simulate assistant response
      setTimeout(() => {
        appendMessage('Thinking...', 'assistant');
      }, 500);

      // Simulate a more detailed assistant response after a further delay
      setTimeout(() => {
        // Remove "Thinking..." message
        const thinkingMessage = messageArea.querySelector('.assistant-message:last-child');
        if (thinkingMessage && thinkingMessage.textContent === 'Thinking...') {
            thinkingMessage.remove();
        }
        appendMessage(`I received your message: "${messageText}". How can I assist you further?`, 'assistant');
      }, 1500);
    }
  }

  sendButton.addEventListener('click', handleSendMessage);

  messageInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
      handleSendMessage();
    }
  });
});
