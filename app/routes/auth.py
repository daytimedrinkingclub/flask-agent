# app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from ..services.data_service import DataService
from ..models.models import User, Token

bp = Blueprint('auth', __name__)

@bp.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        botnine_token = request.form['token']

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('auth.signup'))
        
        # Check if botnine_token already exists
        existing_token = Token.query.filter_by(botnine_token=botnine_token).first()
        if existing_token:
            flash('BotNine token already exists. Please use a different token.')
            return redirect(url_for('auth.signup'))
        
        # Create new user
        password_hash = generate_password_hash(password)
        new_user = DataService.create_user(username, password_hash, botnine_token)
        
        if new_user:
            login_user(new_user)
            return redirect(url_for('main.chats'))
        
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
        return redirect(url_for('main.chats'))
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))