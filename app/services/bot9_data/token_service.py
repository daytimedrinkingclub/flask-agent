from ...extensions import db
from ...models.models import Token

class TokenService:
    @staticmethod
    def save_bot9_token(user_id, bot9_token):
        token = Token(user_id=user_id, bot9_token=bot9_token)
        db.session.add(token)
        db.session.commit()
        return token
    
    @staticmethod
    def update_bot9_token(user_id, new_token):
        token = Token.query.filter_by(user_id=user_id).first()
        if token:
            token.bot9_token = new_token
            db.session.commit()
        return token

    @staticmethod
    def get_bot9_token(user_id):
        token = Token.query.filter_by(user_id=user_id).first()
        return token.bot9_token if token else None