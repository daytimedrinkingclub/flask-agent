# app/services/data_service.py
from ..extensions import db
import json
from sqlalchemy import desc
from ..models.models import User, Token, Chat, Message

class DataService:
    @staticmethod
    def create_user(username, password_hash, botnine_token):
        user = User(username=username, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        DataService.save_botnine_token(user.id, botnine_token)
        return user
    
    @staticmethod
    def save_botnine_token(user_id, botnine_token):
        token = Token(user_id=user_id, botnine_token=botnine_token)
        db.session.add(token)
        db.session.commit()
        return token
    
    @staticmethod
    def get_botnine_token(user_id):
        token = Token.query.filter_by(user_id=user_id).first()
        if token:
            return token.botnine_token
        return None # or handle this case as appropriate for your application
    
    @staticmethod
    def get_user_by_id(user_id):
        return User.query.filter_by(id=user_id).first()

    @staticmethod
    def get_chat_by_id(chat_id):
        return Chat.query.get(chat_id)
    
    @staticmethod
    def get_chats_by_user_id(user_id):
        return Chat.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def update_botnine_token(user_id, new_token):
        token = Token.query.filter_by(user_id=user_id).first()
        if token:
            token.botnine_token = new_token
            db.session.commit()
        return token

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def create_chat(user_id, botnine_chatbot_id):
        new_chat = Chat(user_id=user_id, botnine_chatbot_id=botnine_chatbot_id)
        db.session.add(new_chat)
        db.session.commit()
        print(f"New Chat created with ID: {new_chat.id}")
        return str(new_chat.id)

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
    def get_chat_summary(chat_id):
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

    @staticmethod
    def get_chats_with_summary(user_id):
        chats = Chat.query.filter_by(user_id=user_id).all()
        return [DataService.get_chat_summary(chat.id) for chat in chats] if chats else []
    
    @staticmethod
    def get_bot9_token(chat_id):
        chat = Chat.query.filter(Chat.id == chat_id).first()
        if chat:
            return Token.query.filter(Token.user_id == chat.user_id).first().botnine_token
        return None
    
    @staticmethod
    def get_chatbot_id(chat_id):
        chat = Chat.query.filter(Chat.id == chat_id).first()
        if chat:
            return chat.botnine_chatbot_id
        return None

