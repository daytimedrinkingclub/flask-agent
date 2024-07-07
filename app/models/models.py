from datetime import datetime
from ..extensions import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class User(UserMixin, BaseModel):
    __tablename__ = 'users'
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    tokens = relationship('Token', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    chats = relationship('Chat', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    chatbots = relationship('Chatbot', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

class Token(BaseModel):
    __tablename__ = 'tokens'
    bot9_token = db.Column(db.String(1000), unique=True, nullable=False, index=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False, index=True)
    user = relationship('User', back_populates='tokens')

class Chatbot(BaseModel):
    __tablename__ = 'chatbots'
    bot9_chatbot_id = db.Column(UUID(as_uuid=True), unique=True, nullable=True, index=True)
    bot9_chatbot_name = db.Column(db.String(256), nullable=True)
    bot9_chatbot_url = db.Column(db.String(256), nullable=True)
    bot9_state = db.Column(db.String(256), nullable=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='chatbots')
    instructions = relationship('ChatbotInstruction', back_populates='chatbot', lazy='dynamic', cascade='all, delete-orphan')
    actions = relationship('ChatbotAction', back_populates='chatbot', lazy='dynamic', cascade='all, delete-orphan')
    chats = relationship('Chat', back_populates='chatbot', lazy='dynamic', cascade='all, delete-orphan')

class ChatbotInstruction(BaseModel):
    __tablename__ = 'chatbot_instructions'
    bot9_chatbot_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chatbots.bot9_chatbot_id'), nullable=False, index=True)
    bot9_instruction_category_id = db.Column(UUID(as_uuid=True), nullable=True, index=True)
    bot9_instruction_category_name = db.Column(db.String(256), nullable=True)
    bot9_instruction_category_description = db.Column(db.Text, nullable=True)
    bot9_instruction_id = db.Column(UUID(as_uuid=True), nullable=True, index=True)
    bot9_instruction_name = db.Column(db.String(256), nullable=True)
    bot9_instruction_text = db.Column(db.Text, nullable=True)
    is_category = db.Column(db.Boolean, default=False)  # True for categories, False for instructions
    chatbot = relationship('Chatbot', back_populates='instructions')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_chatbot_instruction_category', 'bot9_chatbot_id', 'bot9_instruction_category_id'),
        db.Index('idx_chatbot_instruction', 'bot9_chatbot_id', 'bot9_instruction_id'),
    )

class ChatbotAction(BaseModel):
    __tablename__ = 'chatbot_actions'
    bot9_chatbot_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chatbots.bot9_chatbot_id'), nullable=False)
    bot9_action_id = db.Column(UUID(as_uuid=True), unique=True, nullable=True)
    bot9_action_name = db.Column(db.String(256), nullable=True)
    bot9_action_description = db.Column(db.Text, nullable=True)
    bot9_action_type = db.Column(db.String(64), nullable=True)
    bot9_action_meta = db.Column(db.Text, nullable=True)
    chatbot = relationship('Chatbot', back_populates='actions')
    is_active_on_bot9 = db.Column(db.Boolean, nullable=True)

class Chat(BaseModel):
    __tablename__ = 'chats'
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False, index=True)
    bot9_chatbot_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chatbots.bot9_chatbot_id'), nullable=False, index=True)
    user = relationship('User', back_populates='chats')
    chatbot = relationship('Chatbot', back_populates='chats')
    messages = relationship('Message', back_populates='chat', lazy='dynamic', cascade='all, delete-orphan')
    action_curls = relationship("ActionCurl", back_populates="chat", cascade='all, delete-orphan')

class Message(BaseModel):
    __tablename__ = 'messages'
    chat_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chats.id'), nullable=False)
    role = db.Column(db.Enum('user', 'assistant', name='role_enum'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tool_name = db.Column(db.String(256), nullable=True)
    tool_use_id = db.Column(db.String(256), nullable=True)
    tool_input = db.Column(db.JSON, nullable=True)
    tool_result = db.Column(db.Text, nullable=True)
    chat = relationship('Chat', back_populates='messages')

    __table_args__ = (
        db.CheckConstraint(role.in_(['user', 'assistant']), name='check_valid_role'),
    )

class ActionCurl(BaseModel):
    __tablename__ = 'action_curls'
    chat_id = db.Column(UUID(as_uuid=True), db.ForeignKey('chats.id'), nullable=False)
    action_name = db.Column(db.String(256), nullable=False)
    curl_as_json = db.Column(db.Text, nullable=False)
    chat = relationship('Chat', back_populates='action_curls')