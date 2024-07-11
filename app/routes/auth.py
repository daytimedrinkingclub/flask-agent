from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from ..models.models import User, Token
from ..services.user_data.user_service import UserDataService
from ..services.bot9_data.bot9_data_service import Bot9DataService

bp = Blueprint('auth', __name__)

@bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        bot9_token = request.form['token']

        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('auth.signup'))
        
        if Token.query.filter_by(bot9_token=bot9_token).first():
            flash('Bot9 API key already exists. Please use a different key.')
            return redirect(url_for('auth.signup'))
        
        new_user = UserDataService.create_user(username, generate_password_hash(password), bot9_token)
        if new_user:
            login_user(new_user)
            return redirect(url_for('main.dashboard'))
        
    return render_template('pages/auth/signup.html')

@bp.route('/login', methods=['GET', 'POST']) 
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = 'remember' in request.form
        
        try:
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password_hash, password):
                login_user(user, remember=remember)
                Bot9DataService.get_bot9_chatbot(user.id)
                return redirect(url_for('main.dashboard'))
            else:
                flash('Please check your login details and try again.')
        except Exception as e:
            current_app.logger.error(f"Error in login route: {str(e)}")
            flash('An error occurred. Please try again later.')
    
    return render_template('pages/auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))