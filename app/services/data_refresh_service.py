# app/services/data_service.py
from ..extensions import db
from ..models.models import Chatbot
from .token_service import TokenService
from .bot9_data_service import Bot9DataService

class DataRefreshService:
    @staticmethod
    def refresh_user_data(user_id):
        print(f"Starting data refresh for user {user_id}")
        # Get the user's Bot9 token
        bot9_token = TokenService.get_bot9_token(user_id)
        if not bot9_token:
            return False, "Bot9 token not found for user"

        # Fetch and store chatbots
        chatbots_updated = Bot9DataService.fetch_and_store_bot9_chatbots(user_id, bot9_token)
        print(f"Chatbots updated for user {user_id}: {chatbots_updated}")
        if not chatbots_updated:
            return False, "Failed to update chatbots"

        # Get and store instructions for each chatbot
        chatbots = Chatbot.query.filter_by(user_id=user_id).all()
        print(f"Found {len(chatbots)} chatbots for user {user_id}")  # Added print statement
        for chatbot in chatbots:
            instructions_result = Bot9DataService.get_and_store_bot9_instructions(user_id)
            print(f"Instructions updated for chatbot {chatbot.chatbot_name}: {instructions_result}")  # Added print statement
            if "Error" in instructions_result:
                return False, f"Failed to update instructions for chatbot {chatbot.chatbot_name}: {instructions_result}"

        print(f"Data refresh for user {user_id} completed successfully")  # Added print statement
        return True, "User data refreshed successfully"