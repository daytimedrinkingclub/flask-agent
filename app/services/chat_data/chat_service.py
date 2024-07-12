from ...extensions import db
from ...models.models import Chat
from ...services.user_data.status_service import StatusService
from ...services.chat_data.message_service import MessageService

class ChatService:
    @staticmethod
    def create_analysis_chat(user_id, bot9_chatbot_id):
        new_analysis_chat = Chat(user_id=user_id, bot9_chatbot_id=bot9_chatbot_id)
        status = "in_progress"
        db.session.add(new_analysis_chat)
        db.session.commit()
        StatusService.update_analysis_chat_status(new_analysis_chat.id, status, bot9_chatbot_id)
        MessageService.save_message(new_analysis_chat.id, "user", content="Start the analysis")
        return new_analysis_chat

    @staticmethod
    def get_chat_by_id(chat_id):
        return Chat.query.get(chat_id)

    @staticmethod
    def get_chats_by_user_id(user_id):
        return Chat.query.filter_by(user_id=user_id).all()