from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from ..services.bot9_data.bot9_data_service import Bot9DataService
from ..services.chat_data.chat_service import ChatService
from ..services.chat_data.message_service import MessageService
from ..services.user_data.data_refresh_service import DataRefreshService
from ..services.user_data.status_service import StatusService

bp = Blueprint('main', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    user_chatbots = Bot9DataService.get_bot9_chatbot(current_user.id) or []
    if not user_chatbots:
        flash('You have no chatbots yet. Please refresh your data to start chatting.')
    for chatbot in user_chatbots:
        chatbot['instructions'] = Bot9DataService.get_chatbot_instructions(chatbot['bot9_chatbot_id'])
        chatbot['actions'] = Bot9DataService.get_chatbot_actions(chatbot['bot9_chatbot_id'])
        chatbot['status'] = StatusService.get_analysis_status(chatbot['bot9_chatbot_id'])
    return render_template('pages/dashboard.html', chatbots=user_chatbots)

@bp.route('/start_analysis', methods=['POST'])
@login_required
def start_analysis():
    bot9_chatbot_id = request.form.get('chatbot_id')
    ChatService.create_analysis_chat(current_user.id, bot9_chatbot_id)
    flash('Analysis started successfully', 'success')
    return redirect(url_for('main.dashboard'))

@bp.route('/chat/<uuid:chatbot_id>')
@login_required
def chat(chatbot_id):
    analysis_status = StatusService.get_analysis_status(str(chatbot_id))
    return render_template('pages/dashboard.html', chatbot_id=chatbot_id, analysis_status=analysis_status)

@bp.route('/chat/<uuid:chat_id>/send_message', methods=['POST'])
@login_required
def send_message(chat_id):
    user_message = request.form.get('user_input')
    if MessageService.save_message(str(chat_id), "user", content=user_message):
        flash('Input received successfully', 'success')
    else:
        flash('Failed to process input', 'error')
    return redirect(url_for('main.chat', chat_id=chat_id))

@bp.route('/analysis/<string:chatbot_id>/analysis_status')
@login_required
def get_analysis_status(chatbot_id):
    status = StatusService.get_analysis_status(chatbot_id)
    return jsonify(status=status, chatbotId=chatbot_id)


@bp.route('/refresh_data', methods=['POST'])
@login_required
def refresh_data():
    user_chatbots, message = DataRefreshService.refresh_user_data(current_user.id)
    if user_chatbots:
        chatbots_data = []
        for chatbot in user_chatbots:
            try:
                chatbot_id = chatbot.get('bot9_chatbot_id') or chatbot.get('id')
                if not chatbot_id:
                    raise ValueError(f"No valid chatbot ID found in chatbot data: {chatbot}")
                chatbot_data = {
                    'bot9_chatbot_id': chatbot_id,
                    'bot9_chatbot_name': chatbot.get('bot9_chatbot_name', 'Unnamed Chatbot'),
                    'instructions': Bot9DataService.get_chatbot_instructions(chatbot_id),
                    'actions': Bot9DataService.get_chatbot_actions(chatbot_id)
                }
                chatbots_data.append(chatbot_data)
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)}), 400
        return jsonify({'success': True, 'chatbots': chatbots_data})
    else:
        return jsonify({'success': False, 'message': message}), 400