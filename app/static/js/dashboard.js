function openUserInputModal(chatbotId = null) {
    document.getElementById('userInputModal').classList.remove('hidden');
    if (chatbotId) {
        document.getElementById('userInputModal').setAttribute('data-chatbot-id', chatbotId);
    }
}

function closeUserInputModal() {
    document.getElementById('userInputModal').classList.add('hidden');
    document.getElementById('userInputText').value = '';
}

document.addEventListener('DOMContentLoaded', function() {
    const closeModalButton = document.getElementById('closeUserInputModal');
    if (closeModalButton) {
        closeModalButton.addEventListener('click', closeUserInputModal);
    }

    const submitButton = document.getElementById('submitUserInput');
    if (submitButton) {
        submitButton.addEventListener('click', function() {
            const chatbotId = document.getElementById('userInputModal').getAttribute('data-chatbot-id');
            const userInput = document.getElementById('userInputText').value;

            if (!chatbotId) {
                alert('Please select a chatbot');
                return;
            }

            if (!userInput.trim()) {
                alert('Please enter some input');
                return;
            }

            fetch("/new_chat", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    chatbot_id: chatbotId,
                    user_input: userInput
                }),
            })
            .then(response => response.json())
            .then(data => {
                closeUserInputModal();
                window.location.href = data.redirect_url;
            })
            .catch(error => {
                alert('Error creating new chat: ' + error);
            });
        });
    }
});

// Function to open the modal when the "Add Input" or "Start Analysis" button is clicked
function openNewChatModal(chatbotId) {
    const button = document.querySelector(`button[onclick="openNewChatModal('${chatbotId}')"]`);
    const state = button.getAttribute('data-state');

    if (state === 'need_input') {
        openUserInputModal(chatbotId);
    } else {
        // If the state is not 'need_input', proceed with starting the analysis directly
        fetch("/new_chat", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({chatbot_id: chatbotId}),
        })
        .then(response => response.json())
        .then(data => {
            window.location.href = data.redirect_url;
        })
        .catch(error => {
            alert('Error creating new chat: ' + error);
        });
    }
}