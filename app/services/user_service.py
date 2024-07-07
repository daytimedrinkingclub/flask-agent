# app/services/user_service.py
from ..extensions import db
from ..models.models import User
from .token_service import TokenService

class UserService:
    @staticmethod
    def create_user(username, password_hash, bot9_token):
        user = User(username=username, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        TokenService.save_bot9_token(user.id, bot9_token)
        return user

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.filter_by(id=user_id).first()