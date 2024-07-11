from ..bot9_data.bot9_data_service import Bot9DataService
from ..bot9_data.token_service import TokenService

class DataRefreshService:
    @staticmethod
    def refresh_user_data(user_id):
        print(f"Starting data refresh for user_id: {user_id}")
        token = TokenService.get_bot9_token(user_id)
        if not token:
            print("No token found")
            return "No token found"
        
        # Fetch chatbots
        print("Fetching chatbots")
        chatbots = Bot9DataService.fetch_bot9_chatbots(token)
        if not chatbots:
            print("No chatbots found")
            return "No chatbots found"
        
        # Save chatbots
        print(f"Saving {len(chatbots)} chatbots")
        success, message = Bot9DataService.save_bot9_chatbots(user_id, chatbots)
        if not success:
            print(f"Error saving chatbots: {message}")
            return message

        # Fetch and save instructions for all unique chatbots
        unique_chatbot_ids = set(chatbot['id'] for chatbot in chatbots)
        print(f"Fetching and saving instructions for {len(unique_chatbot_ids)} unique chatbots")
        for chatbot_id in unique_chatbot_ids:
            print(f"Processing chatbot_id: {chatbot_id}")
            instructions = Bot9DataService.fetch_bot9_chatbot_instructions(chatbot_id, token)
            if instructions:
                print(f"Saving {len(instructions)} instructions for chatbot_id: {chatbot_id}")
                success, message = Bot9DataService.save_bot9_instructions(chatbot_id, instructions)
                if not success:
                    print(f"Error saving instructions for chatbot {chatbot_id}: {message}")
                    return f"Error saving instructions for chatbot {chatbot_id}: {message}"

        # Ensure chatbots have the correct structure
        formatted_chatbots = []
        for chatbot in chatbots:
            formatted_chatbot = {
                'bot9_chatbot_id': chatbot.get('id'),
                'bot9_chatbot_name': chatbot.get('name'),
                'bot9_chatbot_url': chatbot.get('url', ''),
                'instructions': [],  # Will be populated later
                'actions': []  # Will be populated later
            }
            formatted_chatbots.append(formatted_chatbot)

        print("Data refresh completed successfully")
        return formatted_chatbots