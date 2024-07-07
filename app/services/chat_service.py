from ..extensions import db
from ..models.models import Chat

# app/services/chat_service.py
class ChatService:
    @staticmethod
    def create_chat(user_id, bot9_chatbot_id):
        new_chat = Chat(user_id=user_id, bot9_chatbot_id=bot9_chatbot_id)
        db.session.add(new_chat)
        db.session.commit()
        return str(new_chat.id)

    @staticmethod
    def get_chat_by_id(chat_id):
        return Chat.query.get(chat_id)
    
    @staticmethod
    def get_chats_by_user_id(user_id):
        return Chat.query.filter_by(user_id=user_id).all()
