# app/models/models.py
from datetime import datetime
from ..extensions import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

# The user table
class User(UserMixin, db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(10000))
    tokens = relationship('Token', back_populates='user', lazy='dynamic')
    chats = relationship('Chat', back_populates='user', lazy='dynamic')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    chatbots = relationship('Chatbots', back_populates='user', lazy='dynamic')

# This table stores the tokens for bot9 accounts
class Token(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot9_token = db.Column(db.String(100000), unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    user = relationship('User', back_populates='tokens')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Chatbots(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot9_chatbot_id = db.Column(UUID(as_uuid=True), unique=False, nullable=True)
    bot9_chatbot_name = db.Column(db.String(256), unique=False, nullable=True)
    bot9_chatbot_url = db.Column(db.String(256), unique=False, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    user = relationship('User', back_populates='chatbots')
    instructions = relationship('ChatbotInstructions', back_populates='chatbot', lazy='dynamic')
    actions = relationship('ChatbotActions', back_populates='chatbot', lazy='dynamic')

class ChatbotInstructions(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot9_chatbot_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chatbots.id'), nullable=False)
    bot9_instruction_category_id = db.Column(UUID(as_uuid=True), unique=True, nullable=True)
    bot9_instruction_category_name = db.Column(db.Text, nullable=True)
    bot9_instruction_category_description = db.Column(db.Text, nullable=True)
    bot9_instruction_id = db.Column(UUID(as_uuid=True), unique=True, nullable=True)
    bot9_instruction_name = db.Column(db.Text, nullable=True)
    bot9_instruction_text = db.Column(db.Text, nullable=True)
    chatbot = relationship('Chatbots', back_populates='instructions')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class ChatbotActions(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chatbot_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chatbots.id'), nullable=False)
    bot9_chatbot_id = db.Column(UUID(as_uuid=True), unique=False, nullable=True)
    bot9_action_id = db.Column(UUID(as_uuid=True), unique=True, nullable=True)
    bot9_action_name = db.Column(db.Text, nullable=True)
    bot9_action_description = db.Column(db.Text, nullable=True)
    bot9_action_type = db.Column(db.Text, nullable=True)
    bot9_action_meta = db.Column(db.Text, nullable=True)
    chatbot = relationship('Chatbots', back_populates='actions')
    is_active_on_bot = db.Column(db.Boolean, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Chat(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    bot9_chatbot_id = db.Column(UUID(as_uuid=True), unique=False, nullable=True)
    user = relationship('User', back_populates='chats')
    messages = relationship('Message', back_populates='chat', lazy='dynamic', cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    action_curls = relationship("ActionCurls", back_populates="chat")

# This table stores all types of messages (user, assistant, tool use, tool result)
class Message(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chat.id'), nullable=False)
    role = db.Column(db.Enum('user', 'assistant', name='role_enum'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tool_name = db.Column(db.Text, nullable=True)
    tool_use_id = db.Column(db.Text, nullable=True)
    tool_input = db.Column(db.JSON, nullable=True)
    tool_result = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    chat = relationship('Chat', back_populates='messages')

class ActionCurls(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chat.id'), nullable=False)
    action_name = db.Column(db.Text, nullable=False)
    curl_as_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    chat = relationship('Chat', back_populates='action_curls')