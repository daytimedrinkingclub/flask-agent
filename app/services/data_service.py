# app/services/data_service.py
from ..extensions import db
import json
from sqlalchemy import desc
from ..models.models import Chat, Message

class DataService:
    @staticmethod
    # service to get chat by id
    def get_chat_by_id(chat_id):
        return Chat.query.get(chat_id)

    @staticmethod
    # service to get all chats from the database
    def get_all_chats():
        return Chat.query.all()

    @staticmethod
    # service to create a new chat
    def create_chat():
        new_chat = Chat()
        db.session.add(new_chat)
        db.session.commit()
        print(f"New Chat created with ID: {new_chat.id}")
        return str(new_chat.id)

    @staticmethod
    # service to save a message to the database
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
        return message
    
    @staticmethod
    # service to load the conversation from the database
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
    def get_chat_summary(chat_id):
        # service to get the chat summary only
        chat = Chat.query.get(chat_id)
        if not chat:
            return None
        last_message = Message.query.filter_by(chat_id=chat_id).order_by(desc(Message.created_at)).first()
        message_count = Message.query.filter_by(chat_id=chat_id).count()
        return {
            "id": chat.id,
            "last_message": last_message.content[:50] + "..." if last_message else None,
            "message_count": message_count,
            "created_at": chat.created_at
        }