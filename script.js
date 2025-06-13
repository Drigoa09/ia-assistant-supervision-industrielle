console.log("--- script.js started ---");
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
    console.log("Rendering history:", conversationHistory); // Added log
    messageArea.innerHTML = ''; // Clear existing messages
    conversationHistory.forEach(msg => {
      console.log("Appending message to UI from history:", msg); // Added log
      // Add a basic check for message integrity
      if (msg && typeof msg.sender !== 'undefined' && typeof msg.content !== 'undefined') {
          appendMessage(msg.sender, msg.type || 'text', msg.content);
      } else {
          console.error("Malformed message in history:", msg);
          // Optionally, append an error message to the UI for this malformed message
          // appendMessage('system', 'error', 'Malformed message detected in history.');
      }
    });
  }

  async function callChatAPI(newMessageText) {
    console.log("callChatAPI() function called with newMessageText:", newMessageText); // Added log
    // Show a temporary "Thinking..." message for immediate feedback
    // This will be cleared on the next full re-render
    if (newMessageText !== null) { // Don't show "Thinking..." for initial load
        appendMessage('assistant', 'text', 'Traitement en cours...');
    }

    const payload = {
      history: conversationHistory,
      newMessage: newMessageText // Can be null for initial load
    };
    console.log("callChatAPI: Preparing to fetch. Payload:", payload); // Added log

    try {
      const response = await fetch('http://127.0.0.1:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      console.log("callChatAPI: Fetch response received. Status:", response.status, "Ok:", response.ok); // Added log

      if (!response.ok) {
        let errorContent = `Request failed: ${response.status}`;
        try {
          const errorData = await response.json();
          console.log("callChatAPI: Server error response JSON:", errorData); // Added log
          errorContent = (errorData && errorData.content) ? errorData.content : errorContent;
        } catch (e) {
            console.error("callChatAPI: Failed to parse error JSON from server", e); // Added log
            // errorContent remains as defined above or use response.statusText if available
            if(response.statusText) errorContent = response.statusText;
        }
        throw new Error(errorContent);
      }

      const data = await response.json();
      console.log("Received from server:", data); // Existing log

      if (data.updated_history) {
        conversationHistory = data.updated_history;
        console.log("Updated conversationHistory (from updated_history):", conversationHistory); // Existing log
      } else if (data.ui_response) {
        console.warn("callChatAPI: updated_history not received from server. Manually adding ui_response to history."); // Added log
        conversationHistory.push({sender: 'assistant', type: data.ui_response.type, content: data.ui_response.content});
        console.log("Updated conversationHistory (manually added ui_response):", conversationHistory); // Existing log
      } else {
        console.error("callChatAPI: Response from server is missing both updated_history and ui_response.", data); // Added log
        // If we don't have updated_history or a ui_response, it's an issue.
        // But we should still render whatever history we had before, plus an error.
        renderChatHistory(); // Render previous history first
        throw new Error("Received no valid response or history update from server.");
      }
      renderChatHistory();

    } catch (error) {
        console.error("VERY SPECIFIC ERROR IN callChatAPI:", error);
        if (error) { // Check if error object exists
            console.error("Error name:", error.name);
            console.error("Error message:", error.message);
            console.error("Error stack:", error.stack);
        } else {
            console.error("callChatAPI: Caught an undefined error.");
        }

        // Temporarily comment out UI updates from catch block to ensure logs are primary focus
        // const lastMessageDiv = messageArea.lastElementChild;
        // if (lastMessageDiv && lastMessageDiv.textContent === 'Traitement en cours...') {
        //     lastMessageDiv.remove();
        // }
        // appendMessage('assistant', 'error', error && error.message ? error.message : "Error in callChatAPI.");
    }
  }

  function handleSendMessage() {
    console.log("handleSendMessage() called. Current messageInput.value:", messageInput.value); // Added log
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
    // console.log("loadInitialMessage() function called"); // Original log - commented
    // await callChatAPI(null); // Original call - commented

    console.log("loadInitialMessage() function called - SIMPLIFIED TEST");
    try {
        console.log("SIMPLIFIED: About to fetch /chat (POST with empty body)");
        const response = await fetch('/chat', { // Assuming /chat is the correct endpoint
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ history: [], newMessage: null })
        });
        console.log("SIMPLIFIED: Fetch response status:", response.status, "Ok:", response.ok);

        if (!response.ok) {
            let errorContent = `Server error: ${response.status} ${response.statusText}`;
            try {
                const errorData = await response.json();
                console.log("SIMPLIFIED: Server error response JSON:", errorData);
                if (errorData && errorData.content) {
                    errorContent = errorData.content;
                }
            } catch (e) {
                console.error("SIMPLIFIED: Failed to parse server error JSON", e);
            }
            throw new Error(errorContent);
        }

        const data = await response.json();
        console.log("SIMPLIFIED: Fetched data:", data);

        // NOTE: This simplified version does NOT update conversationHistory or render the chat.
        // It's purely for testing the initial fetch and logging the direct response.

    } catch (error) {
        console.error("SIMPLIFIED: VERY SPECIFIC Fetch error:", error);
        if (error) {
            console.error("SIMPLIFIED: Error name:", error.name);
            console.error("SIMPLIFIED: Error message:", error.message);
            console.error("SIMPLIFIED: Error stack:", error.stack);
        } else {
            console.error("SIMPLIFIED: Caught an undefined error during fetch.");
        }
    }
  }

  console.log("Adding DOMContentLoaded listener for loadInitialMessage..."); // Added log
  sendButton.addEventListener('click', function() {
    console.log("Send button clicked, about to call handleSendMessage."); // Added log
    handleSendMessage();
  });
  messageInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault(); // Added this line
      console.log("Enter key pressed, about to call handleSendMessage."); // Existing log
      handleSendMessage();
    }
  });

  loadInitialMessage(); // Load welcome message on page start
});
