from ...extensions import db
from ...models.models import User
from ...services.bot9_data.token_service import TokenService

class UserDataService:
    @staticmethod
    def create_user(username, password_hash, bot9_token):
        user = User(username=username, password_hash=password_hash)
        db.session.add(user)
        db.session.flush()  # This assigns an ID to the user without committing
        TokenService.save_bot9_token(user.id, bot9_token)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)