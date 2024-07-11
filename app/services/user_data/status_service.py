from ...extensions import db
from ...models.models import Chat

class StatusService:
    @staticmethod
    def get_chat_status(chatbot_id):
        chat = Chat.query.get(chatbot_id)
        return chat.status if chat else None

    @staticmethod
    def update_chat_status(chatbot_id, new_status):
        chat = Chat.query.get(chatbot_id)
        if chat:
            chat.status = new_status
            db.session.commit()
            return True
        return False