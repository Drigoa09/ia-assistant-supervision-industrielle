document.addEventListener('DOMContentLoaded', () => {
  const messageArea = document.getElementById('messageArea');
  const messageInput = document.getElementById('messageInput');
  const sendButton = document.getElementById('sendButton');

  // Refactored appendMessage function
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
        img.onload = () => { // Scroll after image loads to get correct height
            messageArea.scrollTop = messageArea.scrollHeight;
        };
        img.onerror = () => { // Handle broken image links
            messageDiv.textContent = "Error loading image: " + content;
            messageArea.scrollTop = messageArea.scrollHeight;
        };
        messageDiv.appendChild(img);
        break;
      case 'list':
        const listElement = document.createElement('ul');
        listElement.style.listStylePosition = 'inside'; // Ensure bullets/numbers are inside the bubble
        listElement.style.paddingLeft = '20px'; // Add some padding for the list items

        if (Array.isArray(content)) {
            // Handle simple array of strings
            content.forEach(itemText => {
                const listItem = document.createElement('li');
                listItem.textContent = itemText;
                listElement.appendChild(listItem);
            });
        } else if (typeof content === 'object' && content !== null) {
            // Handle object like {"Cycle A": ["Prog1", "Prog2"]}
            for (const key in content) {
                if (Object.prototype.hasOwnProperty.call(content, key)) {
                    const mainListItem = document.createElement('li');
                    mainListItem.textContent = key + ':';

                    if (Array.isArray(content[key])) {
                        const subListElement = document.createElement('ul');
                        subListElement.style.paddingLeft = '20px'; // Indent sub-list
                        content[key].forEach(program => {
                            const subListItem = document.createElement('li');
                            subListItem.textContent = program;
                            subListElement.appendChild(subListItem);
                        });
                        mainListItem.appendChild(subListElement);
                    } else {
                        // If the value is not an array, display it directly (though not per example)
                        const subText = document.createElement('span');
                        subText.textContent = ' ' + content[key]; // Add space after key
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
        messageDiv.classList.add('error-message'); // Optional: for specific error styling
        break;
      default:
        messageDiv.textContent = `Received an unknown response type: ${type}`;
        break;
    }

    messageArea.appendChild(messageDiv);
    messageArea.scrollTop = messageArea.scrollHeight; // Scroll to the latest message
  }

  function handleSendMessage() {
    const messageText = messageInput.value.trim();
    if (messageText) {
      appendMessage('user', 'text', messageText);
      messageInput.value = '';

      // Display "Traitement en cours..." message (temporary, not using appendMessage for this status)
      const tempStatusDiv = document.createElement('div');
      tempStatusDiv.classList.add('message', 'assistant-message', 'status-message'); // 'status-message' for potential specific styling
      tempStatusDiv.textContent = 'Traitement en cours...';
      messageArea.appendChild(tempStatusDiv);
      messageArea.scrollTop = messageArea.scrollHeight;

      fetch('http://127.0.0.1:5000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: messageText }),
      })
      .then(async response => { // Make this async to use await for response.json()
        if (!response.ok) {
          let errorContent = `Request failed with status: ${response.status}`;
          try {
            // Try to parse the error response body as JSON
            const errorData = await response.json();
            if (errorData && errorData.content) {
              errorContent = errorData.content;
            } else if (response.statusText) {
              errorContent = response.statusText;
            }
          } catch (e) {
            // JSON parsing failed, or it wasn't a JSON response
            if (response.statusText) {
                errorContent = response.statusText;
            }
            console.warn('Could not parse error response as JSON.', e);
          }
          throw new Error(errorContent); // Throw an error to be caught by the .catch() block
        }
        return response.json(); // If response is OK, parse it as JSON
      })
      .then(data => {
        // Remove "Traitement en cours..." message
        if (tempStatusDiv) {
            tempStatusDiv.remove();
        }

        // Use the new appendMessage with type from backend
        // Ensure data and data.type exist before trying to access them
        const messageType = data && data.type ? data.type : 'error';
        const messageContent = data && data.content ? data.content : 'Received an invalid response structure from server.';
        appendMessage('assistant', messageType, messageContent);
      })
      .catch(error => {
        // Remove "Traitement en cours..." message
        if (tempStatusDiv) {
            tempStatusDiv.remove();
        }
        // Display error message using the new appendMessage
        // error.message here will be from the Error thrown above or from network failure
        appendMessage('assistant', 'error', error.message || 'A network error occurred, or the server is unreachable.');
        console.error('Fetch error details:', error);
      });
    }
  }

  sendButton.addEventListener('click', handleSendMessage);

  messageInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
      handleSendMessage();
    }
  });
});
