document.addEventListener('DOMContentLoaded', function() {
    function setupAnalysisButtons() {
        const startAnalysisButtons = document.querySelectorAll('button[onclick^="startAnalysis"]');
        if (startAnalysisButtons.length === 0) {
            console.error("No 'Start Analysis' buttons found. Retrying in 500ms...");
            setTimeout(setupAnalysisButtons, 500);
            return;
        }

        startAnalysisButtons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.preventDefault();
                const chatbotId = this.getAttribute('data-chatbot-id');
                const userInput = this.getAttribute('data-user-input');
                startAnalysis(chatbotId, userInput);
            });
        });

        console.log("Analysis buttons setup completed successfully");
    }

    setupAnalysisButtons();
});

function startAnalysis(chatbotId, userInput) {
    const payload = {
        chatbot_id: chatbotId,
        user_input: userInput
    };

    fetch("/chat/new", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    })
    .then(response => response.json())
    .then(data => {
        if (data.redirect_url) {
            window.location.href = data.redirect_url;
        } else {
            console.error('No redirect URL provided in the response');
        }
    })
    .catch(error => {
        console.error('Error starting analysis:', error);
        alert('Error starting analysis: ' + error);
    });
}