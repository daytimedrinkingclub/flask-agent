document.addEventListener('DOMContentLoaded', function() {
    const refreshButton = document.getElementById('refresh-data-btn');
    const refreshIcon = document.getElementById('refresh-icon');
    const refreshText = document.getElementById('refresh-text');

    if (refreshButton) {
        refreshButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Disable the button and start animation
            refreshButton.disabled = true;
            refreshButton.classList.add('opacity-75');
            refreshIcon.classList.add('animate-spin');
            refreshText.textContent = 'Syncing...';

            let dots = '';
            const dotAnimation = setInterval(() => {
                dots = dots.length < 3 ? dots + '.' : '';
                refreshText.textContent = 'Syncing' + dots;
            }, 500);

            // Make API call to refresh data
            fetch('/refresh_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the dashboard with new data
                    updateDashboard(data.chatbots);
                    // Restart status updates for new chatbot list
                    if (window.startStatusUpdates) {
                        window.startStatusUpdates();
                    }
                } else {
                    console.error('Error refreshing data:', data.message);
                    alert('Failed to refresh data. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            })
            .finally(() => {
                // Stop dot animation
                clearInterval(dotAnimation);

                // Re-enable the button and stop animation
                refreshButton.disabled = false;
                refreshButton.classList.remove('opacity-75');
                refreshIcon.classList.remove('animate-spin');
                refreshText.textContent = 'Sync with Bot9';

                // Add a quick "completed" animation
                refreshIcon.classList.add('text-green-500', 'scale-110');
                refreshText.textContent = 'Sync Complete!';
                setTimeout(() => {
                    refreshIcon.classList.remove('text-green-500', 'scale-110');
                    refreshText.textContent = 'Sync with Bot9';
                }, 1500);
            });
        });
    }
});

function updateDashboard(chatbots) {
    const chatbotList = document.querySelector('.grid');
    if (chatbotList) {
        chatbotList.innerHTML = ''; // Clear existing list
        if (chatbots.length > 0) {
            chatbots.forEach(chatbot => {
                const chatbotElement = createChatbotElement(chatbot);
                chatbotList.appendChild(chatbotElement);
            });
        } else {
            chatbotList.innerHTML = '<p class="text-center text-gray-400">You don\'t have any chatbots yet. Please refresh your data to start analyzing.</p>';
        }
    }
    // Update chatbotIds for analysis.js
    window.chatbotIds = chatbots.map(chatbot => chatbot.bot9_chatbot_id);
}

function createChatbotElement(chatbot) {
    const div = document.createElement('div');
    div.className = 'bg-medium-black shadow-lg rounded-lg overflow-hidden flex flex-col h-full border border-light-black';
    div.innerHTML = `
        <div class="p-4 border-b border-light-black">
            <h2 class="text-lg font-bold text-white">${chatbot.bot9_chatbot_name}</h2>
            <p class="text-sm text-gray-400">ID: ${chatbot.bot9_chatbot_id}</p>
        </div>
        <div class="p-4 flex-grow">
            <div class="mb-4">
                <h3 class="text-md font-medium text-gray-300 mb-2">Active Instructions</h3>
                <div class="flex flex-wrap gap-2">
                    ${chatbot.instructions.map(instruction => `
                        <span class="px-3 py-1 bg-light-black text-gray-300 text-xs font-medium rounded-full">
                            ${instruction.bot9_instruction_name}
                        </span>
                    `).join('')}
                </div>
            </div>
            <div>
                <h3 class="text-md font-medium text-gray-300 mb-2">Available Actions</h3>
                <div class="flex flex-wrap gap-2">
                    ${chatbot.actions.map(action => `
                        <span class="px-3 py-1 bg-light-black text-gray-300 text-xs font-medium rounded-full">
                            ${action.bot9_action_name}
                        </span>
                    `).join('')}
                </div>
            </div>
        </div>
        <div class="p-4 bg-light-black mt-auto">
            <form action="/start_analysis" method="POST">
                <input type="hidden" name="chatbot_id" value="${chatbot.bot9_chatbot_id}">
                <button type="submit" class="w-full bg-medium-black hover:bg-dark-black text-gray-300 font-medium py-2 px-4 rounded text-sm transition duration-300" data-bot9-chatbot-id="${chatbot.bot9_chatbot_id}">
                    Start Analysis
                </button>
            </form>
        </div>
    `;
    return div;
}