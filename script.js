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

    console.log("loadInitialMessage: Now targeting /test_chat with a simple POST.");
    try {
        const payload = { message: "Hello from client on initial load (test_chat)" }; // Changed to 'message' to match /test_chat expectation
        console.log("TEST_CHAT: About to fetch /test_chat. Payload:", payload);

        const response = await fetch('/test_chat', { // Target the new endpoint
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        console.log("TEST_CHAT: Fetch response status:", response.status, "Ok:", response.ok);

        if (!response.ok) {
            let errorContent = `Server error on /test_chat: ${response.status} ${response.statusText}`;
            try {
                const errorData = await response.json();
                console.log("TEST_CHAT: Server error response JSON:", errorData);
                if (errorData && errorData.content) { // Assuming error structure {content: ...}
                    errorContent = errorData.content;
                } else if (errorData && errorData.reply) { // Or if it's our test reply structure
                     errorContent = JSON.stringify(errorData);
                }
            } catch (e) {
                console.error("TEST_CHAT: Failed to parse server error JSON from /test_chat", e);
            }
            throw new Error(errorContent);
        }

        const data = await response.json();
        console.log("TEST_CHAT: Fetched data from /test_chat:", data);

        if (data && data.reply) {
            console.log("TEST_CHAT: Server reply:", data.reply);
            // For this test, display the reply on the UI to confirm visibility
            appendMessage('assistant', 'text', `Test Reply: ${data.reply} (Received: ${data.received_message})`);
        }

    } catch (error) {
        console.error("TEST_CHAT: VERY SPECIFIC Fetch error for /test_chat:", error);
        if (error) {
            console.error("TEST_CHAT: Error name:", error.name);
            console.error("TEST_CHAT: Error message:", error.message);
            console.error("TEST_CHAT: Error stack:", error.stack);
        } else {
            console.error("TEST_CHAT: Caught an undefined error during /test_chat fetch.");
        }
        // For this test, display the error on the UI
        appendMessage('assistant', 'error', `Test Error: ${error.message || 'Unknown fetch error'}`);
    }
  }

  console.log("Adding DOMContentLoaded listener for loadInitialMessage..."); // Added log
  // Temporarily comment out other event listeners for clean test
  // sendButton.addEventListener('click', function() {
  //   console.log("Send button clicked, about to call handleSendMessage."); // Added log
  //   handleSendMessage();
  // });
  // messageInput.addEventListener('keypress', (event) => {
  //   if (event.key === 'Enter') {
  //     event.preventDefault(); // Added this line
  //     console.log("Enter key pressed, about to call handleSendMessage."); // Existing log
  //     handleSendMessage();
  //   }
  // });

  loadInitialMessage(); // Load welcome message on page start
});
