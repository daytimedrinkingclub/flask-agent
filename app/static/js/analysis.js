function updateAnalysisStatus(chatbotId) {
    fetch(`/analysis/${chatbotId}/analysis_status`)
        .then(response => response.json())
        .then(data => {
            const button = document.querySelector(`#chatbot-container-${chatbotId} button`);
            if (data.status === 'in_progress') {
                button.innerHTML = '<span class="animate-spin inline-block mr-2">&#8987;</span> Analyzing...';
                button.disabled = true;
            } else if (data.status === 'completed') {
                button.textContent = 'Analysis Complete';
                button.disabled = false;
            } else if (data.status === 'error') {
                button.textContent = 'Error in Analysis';
                button.disabled = false;
            } else {
                button.textContent = 'Start Analysis';
                button.disabled = false;
            }
        })
        .catch(error => console.error('Error:', error));
}

document.addEventListener('DOMContentLoaded', () => {
    const chatbotContainers = document.querySelectorAll('[id^="chatbot-container-"]');
    chatbotContainers.forEach(container => {
        const chatbotId = container.id.split('-').pop();
        setInterval(() => updateAnalysisStatus(chatbotId), 10000); // Check every 10 seconds
    });
});