document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const userMessageInput = document.getElementById('user-message');
    const sendButton = document.getElementById('send-button');
    const conversationDiv = document.getElementById('conversation');
    let isInputBlocked = false;

    function disableUserInput() {
        userMessageInput.disabled = true;
        sendButton.disabled = true;
        userMessageInput.placeholder = "Please wait for the assistant's response...";
        isInputBlocked = true;
    }

    function enableUserInput() {
        userMessageInput.disabled = false;
        sendButton.disabled = false;
        userMessageInput.placeholder = "Type your message...";
        isInputBlocked = false;
    }

    function shouldEnableInput(lastMessage) {
        return lastMessage && 
               lastMessage.role === 'assistant' && 
               !lastMessage.content.some(c => c.type === 'tool_use');
    }

    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (isInputBlocked) return;

        var userMessage = userMessageInput.value;
        userMessageInput.value = ''; // Clear input immediately
        disableUserInput(); // Disable input immediately

        fetch(window.chatData.sendMessageUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_message: userMessage })
        })
        .then(response => response.json())
        .then(data => {
            refreshChat();
        })
        .catch(error => {
            console.error('Error:', error);
            enableUserInput(); // Re-enable input if there's an error
        });
    });

    function refreshChat() {
        fetch(window.chatData.refreshChatUrl)
            .then(response => response.json())
            .then(data => {
                let newContent = '';
                data.conversation.forEach(message => {
                    newContent += `
                    <div class="mb-4 p-3 rounded-lg ${message.role === 'user' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}">
                    `;
                    message.content.forEach(content => {
                        if (content.type === 'text') {
                            newContent += `<p class="mb-1"><strong>${message.role.charAt(0).toUpperCase() + message.role.slice(1)}:</strong> ${content.text}</p>`;
                        } else if (content.type === 'tool_result') {
                            newContent += `<p class="mb-1"><strong>Tool Result:</strong> ${content.content}</p>`;
                        } else if (content.type === 'tool_use') {
                            newContent += `<p class="mb-1"><strong>Tool Used:</strong> ${content.name}</p>`;
                            newContent += `<p class="mb-1"><strong>Tool Input:</strong> ${JSON.stringify(content.input)}</p>`;
                        }
                    });
                    newContent += `</div>`;
                });
                
                // Update the conversation div without scrolling
                conversationDiv.innerHTML = newContent;

                // Check if we should enable or disable user input
                const lastMessage = data.conversation[data.conversation.length - 1];
                
                if (data.conversation.length > 0) {
                    if (shouldEnableInput(lastMessage)) {
                        enableUserInput();
                    } else if (lastMessage.role === 'user') {
                        disableUserInput();
                    }
                    // If it's not a user message and not an assistant message without tool use, keep the current input state
                } else {
                    // If there are no messages, enable input for the first message
                    enableUserInput();
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

    // Refresh chat every 1 second
    setInterval(refreshChat, 1000);

    // Initial refresh
    refreshChat();
});