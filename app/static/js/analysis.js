let activeInputChatbotId = null;
let refreshIntervals = {};
let lastKnownStatus = {};
let isRefreshPaused = false;

function updateAnalysisStatus(chatbotId) {
    if (isRefreshPaused) return;

    console.log(`Fetching analysis status for chatbot ID: ${chatbotId}`);
    fetch(`/analysis/${chatbotId}/analysis_status`, {
        method: 'GET',
    })
    .then(response => response.json())
    .then(data => {
        console.log(`Received status for chatbot ID ${chatbotId}:`, data.status);
        if (lastKnownStatus[chatbotId] === 'need_input' && data.status === 'need_input') {
            console.log(`Skipping update for chatbot ID ${chatbotId} as it's still in need_input status`);
            return;
        }
        lastKnownStatus[chatbotId] = data.status;
        const button = document.querySelector(`button[data-bot9-chatbot-id="${chatbotId}"]`);
        const form = button.closest('form');
        switch (data.status) {
            case 'in_progress':
                updateButtonStatus(button, '<span class="animate-spin inline-block mr-2">&#8987;</span> Analyzing...', true, ['bg-gray-500', 'cursor-not-allowed'], ['hover:bg-dark-black', 'bg-red-500', 'animate-shake']);
                form.onsubmit = null;
                hideInputForm();
                break;
            case 'completed':
                updateButtonStatus(button, 'Analysis Complete', false, ['hover:bg-dark-black'], ['bg-gray-500', 'bg-red-500', 'animate-shake', 'cursor-not-allowed']);
                form.onsubmit = null;
                hideInputForm();
                break;
            case 'error':
                updateButtonStatus(button, 'Error in Analysis', false, ['hover:bg-dark-black', 'bg-rose-500'], ['bg-gray-500', 'animate-shake', 'cursor-not-allowed']);
                form.onsubmit = null;
                hideInputForm();
                break;
            case 'need_input':
                updateButtonStatus(button, 'Input Needed', false, ['hover:bg-dark-black', 'bg-red-500', 'animate-shake'], ['bg-gray-500', 'cursor-not-allowed']);
                form.onsubmit = (e) => {
                    e.preventDefault();
                    const sampleText = `
                        <p class="mb-4">We need more information to proceed with the analysis. Please answer the following question:</p>
                        
                        <p>Your detailed input will help us tailor the analysis to your needs.</p>
                    `;
                    showInputForm(chatbotId, sampleText);
                    pauseRefresh();
                };
                break;
            case 'browsing_web':
                updateButtonStatus(button, '<span class="inline-block mr-2">🌐</span> Browsing Web...', true, ['bg-slate-600', 'cursor-not-allowed', 'text-white'], ['hover:bg-dark-black', 'bg-red-500', 'animate-shake']);
                hideInputForm();
                break;
            case 'writing_code':
                updateButtonStatus(button, '<span class="inline-block mr-2">💻</span> Writing Code...', true, ['bg-teal-700', 'cursor-not-allowed', 'text-white'], ['hover:bg-dark-black', 'bg-red-500', 'animate-shake']);
                hideInputForm();
                break;
            case 'creating_actions':
                updateButtonStatus(button, '<span class="inline-block mr-2">⚡</span> Creating Actions...', true, ['bg-amber-700', 'cursor-not-allowed', 'text-white'], ['hover:bg-dark-black', 'bg-red-500', 'animate-shake']);
                hideInputForm();
                break;
            case 'creating_instructions':
                updateButtonStatus(button, '<span class="inline-block mr-2">📝</span> Creating Instructions...', true, ['bg-indigo-700', 'cursor-not-allowed', 'text-white'], ['hover:bg-dark-black', 'bg-red-500', 'animate-shake']);
                hideInputForm();
                break;
            case 'consulting_subhash':
                updateButtonStatus(button, '<span class="inline-block mr-2">🧠</span> Consulting Subhash...', true, ['bg-rose-800', 'cursor-not-allowed', 'text-white'], ['hover:bg-dark-black', 'bg-red-500', 'animate-shake']);
                hideInputForm();
                break;
            case 'not_found':
            default:
                updateButtonStatus(button, 'Start Analysis', false, ['hover:bg-dark-black'], ['bg-gray-500', 'bg-red-500', 'animate-shake', 'cursor-not-allowed']);
                form.onsubmit = null;
                hideInputForm();
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function updateButtonStatus(button, text, disabled, classesToAdd, classesToRemove) {
    button.innerHTML = text;
    button.disabled = disabled;
    button.classList.remove(...classesToRemove);
    button.classList.add(...classesToAdd);
}

function showInputForm(chatbotId, richText) {
    const inputContainer = document.getElementById('user-input-container');
    inputContainer.classList.remove('hidden');
    activeInputChatbotId = chatbotId;
    
    updateRichTextParagraph(richText);
    
    const form = inputContainer.querySelector('form');
    form.action = form.action.replace(/chat_id=\w+/, `chat_id=${chatbotId}`);
    
    inputContainer.scrollIntoView({ behavior: 'smooth' });
}

function updateRichTextParagraph(text) {
    const questionTextDiv = document.getElementById('question-text');
    questionTextDiv.innerHTML = text;
    
    // Apply additional styling
    questionTextDiv.querySelectorAll('p').forEach(p => p.classList.add('mb-2'));
    questionTextDiv.querySelectorAll('h3').forEach(h3 => h3.classList.add('text-lg', 'font-semibold', 'mb-2', 'text-white'));
    questionTextDiv.querySelectorAll('ul').forEach(ul => ul.classList.add('list-disc', 'list-inside', 'mb-4', 'pl-4'));
    questionTextDiv.querySelectorAll('li').forEach(li => li.classList.add('mb-1'));
}

function hideInputForm() {
    const inputContainer = document.getElementById('user-input-container');
    inputContainer.classList.add('hidden');
    activeInputChatbotId = null;
}

function handleInputSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Input submitted successfully:', data);
        hideInputForm();
        resumeRefresh();
        updateAnalysisStatus(activeInputChatbotId);
    })
    .catch(error => {
        console.error('Error submitting input:', error);
    });
}

function pauseRefresh() {
    isRefreshPaused = true;
    Object.values(refreshIntervals).forEach(clearInterval);
    refreshIntervals = {};
}

function resumeRefresh() {
    isRefreshPaused = false;
    startStatusUpdates();
}
function startStatusUpdates() {
    console.log('Starting status updates for chatbots');
    chatbotIds.forEach(chatbotId => {
        console.log(`Setting up interval for chatbot ID: ${chatbotId}`);
        updateAnalysisStatus(chatbotId);  // Initial update
        refreshIntervals[chatbotId] = setInterval(() => updateAnalysisStatus(chatbotId), 5000);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    startStatusUpdates();
    
    const inputForm = document.getElementById('user-input-form');
    if (inputForm) {
        const form = inputForm.querySelector('form');
        form.addEventListener('submit', handleInputSubmit);
    }

    hideInputForm();
});

window.startStatusUpdates = startStatusUpdates;