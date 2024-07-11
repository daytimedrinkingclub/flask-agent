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
    return render_template('pages/dashboard.html', chatbots=user_chatbots)

@bp.route('/start_analysis', methods=['POST'])
@login_required
def start_analysis():
    bot9_chatbot_id = request.form.get('chatbot_id')
    analysis_id = ChatService.create_chat(current_user.id, bot9_chatbot_id)
    MessageService.save_message(analysis_id, "user", content="Start the analysis")
    flash('Analysis started successfully', 'success')
    return redirect(url_for('main.dashboard'))

@bp.route('/chat/<uuid:chatbot_id>')
@login_required
def chat(chatbot_id):
    chat_status = StatusService.get_chat_status(str(chatbot_id))
    return render_template('pages/dashboard.html', chatbot_id=chatbot_id, chat_status=chat_status)

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
    status = StatusService.get_chat_status(chatbot_id)
    return jsonify(status=status)


@bp.route('/refresh_data')
@login_required
def refresh_data():
    user_chatbots, message = DataRefreshService.refresh_user_data(current_user.id)
    if user_chatbots:
        flash('Your data has been refreshed successfully.', 'success')
        for chatbot in user_chatbots:
            try:
                chatbot_id = chatbot.get('bot9_chatbot_id') or chatbot.get('id')
                if not chatbot_id:
                    raise ValueError(f"No valid chatbot ID found in chatbot data: {chatbot}")
                chatbot['instructions'] = Bot9DataService.get_chatbot_instructions(chatbot_id)
                chatbot['actions'] = Bot9DataService.get_chatbot_actions(chatbot_id)
            except Exception as e:
                flash(f'Error refreshing data: {e}', 'error')
        return render_template('pages/dashboard.html', chatbots=user_chatbots)
    else:
        flash(f'Failed to refresh data: {message}', 'error')
        return redirect(url_for('main.dashboard'))