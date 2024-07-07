# app/routes/main.py
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
import logging
from flask_login import login_required, current_user
from ..services.anthropic_chat import AnthropicChat
from ..services.bot9_data_service import Bot9DataService
from ..services.chat_service import ChatService
from ..services.message_service import MessageService
from ..services.token_service import TokenService
from ..services.data_refresh_service import DataRefreshService

bp = Blueprint('main', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    user_chatbots = Bot9DataService.get_user_chatbots(current_user.id)
    if not user_chatbots:
        flash('You have no chatbots yet. Please create one to start chatting.')
    
    return render_template('main/dashboard-layout.html', chatbots=user_chatbots)

@bp.route('/chat/new', methods=['POST'])
@login_required
def new_chat():
    data = request.get_json()
    chatbot_id = data.get('chatbot_id')
    if not chatbot_id:
        return jsonify(error="Chatbot ID is required"), 400
    
    try:
        # Create a new chat
        chat_id = ChatService.create_chat(current_user.id, chatbot_id)
        return jsonify(redirect_url=url_for('main.chat', chat_id=chat_id))
    except Exception as e:
        return jsonify(error=str(e)), 500

@bp.route('/chat/<uuid:chat_id>')
@login_required
def chat(chat_id):
    chat = ChatService.get_chat_by_id(str(chat_id))
    if not chat or chat.user_id != current_user.id:
        return redirect(url_for('main.dashboard'))
    conversation = MessageService.load_conversation(str(chat_id))
    bot9_token = "Token Added" if TokenService.get_bot9_token(current_user.id) else None
    return render_template('main/chat.html', chat=chat, conversation=conversation, bot9_token=bot9_token)

@bp.route('/chat/<uuid:chat_id>/message', methods=['POST'])
@login_required
def send_message(chat_id):
    user_message = request.json['user_message']
    chat_response = AnthropicChat.handle_chat(str(chat_id), user_message)
    return jsonify(chat_response=chat_response.dict())

@bp.route('/chat/<uuid:chat_id>/refresh', methods=['GET'])
@login_required
def refresh_chat(chat_id):
    chat = ChatService.get_chat_by_id(str(chat_id))
    if not chat or chat.user_id != current_user.id:
        return jsonify(error="Unauthorized"), 403
    conversation = MessageService.load_conversation(str(chat_id))
    return jsonify(conversation=conversation)

@bp.route('/refresh_data')
@login_required
def refresh_data():
    print(f"Refreshing data for user {current_user.id}")  # Changed from logging.info to print
    user_chatbots = DataRefreshService.refresh_user_data(current_user.id)
    print(f"Refreshed data for user {current_user.id}. Found {len(user_chatbots)} chatbots.")  # Changed from logging.info to print
    return redirect(url_for('main.dashboard'))