function refreshChatStatus(chatId) {
    fetch(`/chat/${chatId}/status_update`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('chat-status').textContent = data.status;
            
            const chatMessages = document.getElementById('chat-messages');
            chatMessages.innerHTML = '';
            data.messages.forEach(message => {
                const messageDiv = document.createElement('div');
                messageDiv.className = `mb-4 ${message.role === 'user' ? 'text-right' : ''}`;
                messageDiv.innerHTML = `
                    <span class="font-bold">${message.role.charAt(0).toUpperCase() + message.role.slice(1)}:</span>
                    <p>${message.content}</p>
                `;
                chatMessages.appendChild(messageDiv);
            });
            chatMessages.scrollTop = chatMessages.scrollHeight;

            const userInputForm = document.getElementById('user-input-form');
            if (data.status === 'need_input') {
                userInputForm.classList.remove('hidden');
            } else {
                userInputForm.classList.add('hidden');
            }
        })
        .catch(error => console.error('Error:', error));
}

// Refresh status every 5 seconds if a chat is in progress
if (typeof chatId !== 'undefined') {
    setInterval(() => refreshChatStatus(chatId), 5000);
}