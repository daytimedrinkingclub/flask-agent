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

# This table stores the tokens for bot9 accounts
class Token(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    botnine_token = db.Column(db.String(100000), unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    user = relationship('User', back_populates='tokens')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Chat(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    botnine_chatbot_id = db.Column(db.String(256), unique=False, nullable=True)
    user = relationship('User', back_populates='chats')
    messages = relationship('Message', back_populates='chat', lazy='dynamic', cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

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