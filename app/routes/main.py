# app/routes/main.py
from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from ..services.anthropic_chat import AnthropicChat
from ..services.data_service import DataService

bp = Blueprint('main', __name__)


@bp.route('/chats')
def chats():
    user_chats = DataService.get_all_chats()
    return render_template('main/chats.html', chats=user_chats)

@bp.route('/chat/new', methods=['POST'])
def new_chat():
    data = request.get_json()
    botnine_chatbot_id = data.get('botnine_chatbot_id')
    if not botnine_chatbot_id:
        return jsonify(error="BotNine Chatbot ID is required"), 400
    
    try:
        # Create a new chat
        chat_id = DataService.create_chat()
        return jsonify(redirect_url=url_for('main.chat', chat_id=chat_id))
    except Exception as e:
        return jsonify(error=str(e)), 500

@bp.route('/chat/<uuid:chat_id>')
def chat(chat_id):
    chat = DataService.get_chat_by_id(str(chat_id))
    conversation = DataService.load_conversation(str(chat_id))
    return render_template('main/chat.html', chat=chat, conversation=conversation)

@bp.route('/chat/<uuid:chat_id>/message', methods=['POST'])
def send_message(chat_id):
    user_message = request.json['user_message']
    chat_response = AnthropicChat.handle_chat(str(chat_id), user_message)
    return jsonify(chat_response=chat_response.dict())

@bp.route('/chat/<uuid:chat_id>/refresh', methods=['GET'])
def refresh_chat(chat_id):
    chat = DataService.get_chat_by_id(str(chat_id))
    conversation = DataService.load_conversation(str(chat_id))
    return jsonify(conversation=conversation)