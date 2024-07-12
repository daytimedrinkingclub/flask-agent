from ...extensions import db
from ...models.models import Chat

class StatusService:
    @staticmethod
    def get_analysis_status(chatbot_id):
        analysis_chat = Chat.query.filter_by(bot9_chatbot_id=chatbot_id).first()
        if analysis_chat:
            return analysis_chat.status
        return 'not_found'

    @staticmethod
    def update_analysis_chat_status(analysis_chat_id, new_status, bot9_chatbot_id):
        analysis_chat = Chat.query.filter_by(id=analysis_chat_id, bot9_chatbot_id=bot9_chatbot_id).first()
        if analysis_chat:
            analysis_chat.status = new_status
            db.session.commit()
            return True
        return False