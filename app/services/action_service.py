# app/services/action_service.py
from ..extensions import db
from ..models.models import ActionCurl

class ActionService:
    @staticmethod
    def write_curl_to_database(chat_id, curl_data, action_name):
        new_curl = ActionCurl(chat_id=chat_id, curl_as_json=curl_data, action_name=action_name)
        db.session.add(new_curl)
        db.session.commit()
        return f"Action added to database with action_name='{new_curl.action_name}'"
    
    @staticmethod
    def get_curl_from_database(chat_id):
        return ActionCurl.query.filter_by(chat_id=chat_id).all()
