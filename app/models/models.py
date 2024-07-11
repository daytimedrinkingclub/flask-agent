from datetime import datetime
from ..extensions import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

def generate_uuid():
    return uuid.uuid4()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    
    tokens = relationship('Token', back_populates='user', cascade='all, delete-orphan')
    chats = relationship('Chat', back_populates='user', cascade='all, delete-orphan')
    
    def get_id(self):
        return str(self.id)

class Token(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    bot9_token = db.Column(db.String(1000), unique=True, nullable=False, index=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='tokens')

class Chatbot(db.Model):
    __tablename__ = 'chatbots'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot9_chatbot_id = db.Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    bot9_chatbot_name = db.Column(db.String(256), nullable=False)
    bot9_chatbot_url = db.Column(db.String(256))
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    instructions = relationship('ChatbotInstruction', back_populates='chatbot', cascade='all, delete-orphan')
    instruction_categories = relationship('ChatbotInstructionCategory', back_populates='chatbot', cascade='all, delete-orphan')
    actions = relationship('ChatbotAction', back_populates='chatbot', cascade='all, delete-orphan')
    chats = relationship('Chat', back_populates='chatbot', cascade='all, delete-orphan')

class ChatbotInstructionCategory(db.Model):
    __tablename__ = 'chatbot_instruction_categories'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot9_chatbot_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chatbots.bot9_chatbot_id'), nullable=False)
    bot9_instruction_category_id = db.Column(UUID(as_uuid=True), nullable=False)
    bot9_instruction_category_name = db.Column(db.String(256), nullable=False)
    bot9_instruction_category_description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chatbot = relationship('Chatbot', back_populates='instruction_categories')
    instructions = relationship('ChatbotInstruction', back_populates='category', cascade='all, delete-orphan')

class ChatbotInstruction(db.Model):
    __tablename__ = 'chatbot_instructions'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot9_chatbot_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chatbots.bot9_chatbot_id'), nullable=False)
    bot9_instruction_id = db.Column(UUID(as_uuid=True), nullable=False)
    bot9_instruction_name = db.Column(db.String(256), nullable=False)
    bot9_instruction_text = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chatbot_instruction_categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chatbot = relationship('Chatbot', back_populates='instructions')
    category = relationship('ChatbotInstructionCategory', back_populates='instructions')

class ChatbotAction(db.Model):
    __tablename__ = 'chatbot_actions'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot9_chatbot_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chatbots.bot9_chatbot_id'), nullable=False)
    bot9_action_id = db.Column(UUID(as_uuid=True), unique=True)
    bot9_action_name = db.Column(db.String(256))
    bot9_action_description = db.Column(db.Text)
    bot9_action_type = db.Column(db.String(64))
    bot9_action_meta = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chatbot = relationship('Chatbot', back_populates='actions')

class Chat(db.Model):
    __tablename__ = 'chats'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False, index=True)
    bot9_chatbot_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chatbots.bot9_chatbot_id'), nullable=False, index=True)
    status = db.Column(db.String(64), default='to_be_started')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship('User', back_populates='chats')
    chatbot = relationship('Chatbot', back_populates='chats')
    messages = relationship('Message', back_populates='chat', cascade='all, delete-orphan')
    action_curls = relationship("ActionCurl", back_populates="chat", cascade='all, delete-orphan')

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    chat_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chats.id'), nullable=False)
    role = db.Column(db.Enum('user', 'assistant', name='role_enum'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tool_name = db.Column(db.String(256))
    tool_use_id = db.Column(db.String(256))
    tool_input = db.Column(db.JSON)
    tool_result = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    chat = relationship('Chat', back_populates='messages')

class ActionCurl(db.Model):
    __tablename__ = 'action_curls'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    chat_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chats.id'), nullable=False)
    action_name = db.Column(db.String(256), nullable=False)
    curl_as_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    chat = relationship('Chat', back_populates='action_curls')