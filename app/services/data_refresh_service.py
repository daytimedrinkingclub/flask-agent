# app/services/data_service.py
from ..extensions import db
from ..models.models import Chatbot
from .token_service import TokenService
from .bot9_data_service import Bot9DataService

class DataRefreshService:
    @staticmethod
    def refresh_user_data(user_id):
        print(f"Starting data refresh for user {user_id}")
        bot9_token = TokenService.get_bot9_token(user_id)
        # Update chatbots
        chatbots_updated = Bot9DataService.fetch_and_store_bot9_chatbots(user_id, bot9_token=bot9_token)
        print(f"Chatbots updated for user {user_id}: {chatbots_updated}")
        
        # Get and store instructions for all chatbots in a single call
        instructions_updated = Bot9DataService.get_and_store_bot9_instructions(user_id)
        print(f"Instructions updated for user {user_id}: {instructions_updated}")
        
        # Get updated chatbots
        user_chatbots = Bot9DataService.get_user_chatbots(user_id)
        print(f"Found {len(user_chatbots)} chatbots for user {user_id}")
        
        return user_chatbots