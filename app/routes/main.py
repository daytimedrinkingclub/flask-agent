# app/routes/main.py
from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_login import login_required, current_user
from ..services.anthropic_chat import AnthropicChat
from ..services.data_service import DataService

bp = Blueprint('main', __name__)


@bp.route('/chats')
@login_required
def chats():
    user_chats = DataService.get_chats_with_summary(current_user.id)
    return render_template('main/chats.html', chats=user_chats)


@bp.route('/chat/new', methods=['POST'])
@login_required
def new_chat():
    data = request.get_json()
    botnine_chatbot_id = data.get('botnine_chatbot_id')
    if not botnine_chatbot_id:
        return jsonify(error="BotNine Chatbot ID is required"), 400
    
    try:
        # Create a new chat
        chat_id = DataService.create_chat(current_user.id, botnine_chatbot_id)
        return jsonify(redirect_url=url_for('main.chat', chat_id=chat_id))
    except Exception as e:
        return jsonify(error=str(e)), 500

@bp.route('/chat/<uuid:chat_id>')
@login_required
def chat(chat_id):
    chat = DataService.get_chat_by_id(str(chat_id))
    if not chat or chat.user_id != current_user.id:
        return redirect(url_for('main.chats'))
    conversation = DataService.load_conversation(str(chat_id))
    bot9_token = DataService.get_botnine_token(current_user.id)
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
    chat = DataService.get_chat_by_id(str(chat_id))
    if not chat or chat.user_id != current_user.id:
        return jsonify(error="Unauthorized"), 403
    conversation = DataService.load_conversation(str(chat_id))
    return jsonify(conversation=conversation)