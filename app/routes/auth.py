# app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.models import User, Token
from ..services.user_service import UserService
from ..services.token_service import TokenService
from ..services.bot9_data_service import Bot9DataService

bp = Blueprint('auth', __name__)

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        bot9_token = request.form['token']

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('auth.signup'))
        
        # Check if botnine_token already exists
        existing_token = Token.query.filter_by(bot9_token=bot9_token).first()
        if existing_token:
            flash('Bot9 api key already exists. Please use a different key.')
            return redirect(url_for('auth.signup'))
        
        # Create new user
        password_hash = generate_password_hash(password)
        new_user = UserService.create_user(username, password_hash, bot9_token)
        
        if new_user:
            login_user(new_user)
            return redirect(url_for('main.dashboard'))
        
    return render_template('auth/signup.html')

@bp.route('/login', methods=['GET', 'POST']) 
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=remember)

        # Fetch Bot9 token
        bot9_token = TokenService.get_bot9_token(user.id)
        if bot9_token:
            # Fetch and store chatbots
            success = Bot9DataService.fetch_and_store_bot9_chatbots(user.id, bot9_token)
            if not success:
                flash('Failed to fetch chatbot information. Some features may be limited.')

        return redirect(url_for('main.dashboard'))
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))