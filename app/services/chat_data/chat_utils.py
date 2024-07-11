from ...extensions import db
from ...models.models import Chat, Message

def get_total_messages(chat_id):
    return Message.query.filter_by(chat_id=chat_id).count()

def update_chat_status(chat_id, new_status):
    chat = Chat.query.get(chat_id)
    if chat:
        chat.status = new_status
        db.session.commit()
        return True
    return False