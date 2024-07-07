document.addEventListener('DOMContentLoaded', function() {
    function setupModal() {
        const userInputModal = document.getElementById('userInputModal');
        const closeModalButton = document.getElementById('closeUserInputModal');
        const submitButton = document.getElementById('submitUserInput');
        const userInputText = document.getElementById('userInputText');

        if (!userInputModal || !closeModalButton || !submitButton || !userInputText) {
            console.error("One or more modal elements not found. Retrying in 500ms...");
            setTimeout(setupModal, 500);
            return;
        }

        closeModalButton.addEventListener('click', closeUserInputModal);

        submitButton.addEventListener('click', function() {
            const chatbotId = userInputModal.getAttribute('data-chatbot-id');
            const userInput = userInputText.value.trim();

            if (!chatbotId) {
                alert('Please select a chatbot');
                return;
            }

            if (!userInput) {
                alert('Please enter some input');
                return;
            }

            startAnalysis(chatbotId, userInput);
        });

        console.log("Modal setup completed successfully");
    }

    setupModal();

    function setupAnalysisButtons() {
        const startAnalysisButtons = document.querySelectorAll('button[onclick^="openUserInputModal"]');
        if (startAnalysisButtons.length === 0) {
            console.error("No 'Start Analysis' buttons found. Retrying in 500ms...");
            setTimeout(setupAnalysisButtons, 500);
            return;
        }

        startAnalysisButtons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.preventDefault();
                const chatbotId = this.getAttribute('onclick').match(/'(.+)'/)[1];
                openUserInputModal(chatbotId);
            });
        });

        console.log("Analysis buttons setup completed successfully");
    }

    setupAnalysisButtons();
});

function openUserInputModal(chatbotId) {
    const userInputModal = document.getElementById('userInputModal');
    if (userInputModal) {
        userInputModal.classList.remove('hidden');
        userInputModal.setAttribute('data-chatbot-id', chatbotId);
    } else {
        console.error("Cannot open modal: userInputModal is null");
    }
}

function closeUserInputModal() {
    const userInputModal = document.getElementById('userInputModal');
    const userInputText = document.getElementById('userInputText');
    if (userInputModal) userInputModal.classList.add('hidden');
    if (userInputText) userInputText.value = '';
}

function startAnalysis(chatbotId, userInput) {
    const payload = {
        chatbot_id: chatbotId,
        user_input: userInput
    };

    fetch("/new_chat", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    })
    .then(response => response.json())
    .then(data => {
        closeUserInputModal();
        window.location.href = data.redirect_url;
    })
    .catch(error => {
        console.error('Error creating new chat:', error);
        alert('Error creating new chat: ' + error);
    });
}