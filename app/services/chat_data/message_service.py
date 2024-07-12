from ...extensions import db
from ...models.models import Message
from rq import Queue
from ...redis_client import get_redis
from .chat_utils import update_chat_status
from ...services.user_data.status_service import StatusService
from ...services.anthropic_services.anthropic_chat import handle_chat




class MessageService:
    @staticmethod
    def save_message(chat_id, role, content, tool_use_id=None, tool_use_input=None, tool_name=None, tool_result=None):
        message = Message(
            chat_id=chat_id,
            role=role,
            content=content,
            tool_name=tool_name,
            tool_use_id=tool_use_id,
            tool_input=tool_use_input,
            tool_result=tool_result
        )
        db.session.add(message)
        db.session.commit()
        
        if role == 'assistant' and not tool_name and content:
            update_chat_status(chat_id, 'input_needed')
            return message
        else:
            status = f"{role}_{tool_name}" if tool_name else f"{role}_tool_result" if tool_result else role
            update_chat_status(chat_id, status)
        
        # q = Queue(connection=get_redis())

        # q.enqueue(handle_chat, chat_id)
        return message

    @staticmethod
    def load_conversation(chat_id):
        messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.created_at).all()
        conversation = []
        for message in messages:
            if message.role == "user":
                if message.tool_result:
                    conversation.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": message.tool_use_id,
                                "content": message.tool_result
                            }
                        ]
                    })
                else:
                    conversation.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": message.content
                            }
                        ]
                    })
            elif message.role == "assistant":
                if message.tool_name:
                    conversation.append({
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": message.content
                            },
                            {
                                "type": "tool_use",
                                "id": message.tool_use_id,
                                "name": message.tool_name,
                                "input": message.tool_input
                            }
                        ]
                    })
                else:
                    conversation.append({
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": message.content
                            }
                        ]
                    })
        return conversation
    
    @staticmethod
    def get_total_messages(chat_id):
        return Message.query.filter_by(chat_id=chat_id).count()