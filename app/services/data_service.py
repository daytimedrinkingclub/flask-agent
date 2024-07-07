# app/services/data_service.py
import requests
from ..extensions import db
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from ..models.models import User, Token, Chat, Message, ActionCurls, Chatbots, ChatbotInstructions, ChatbotActions

class DataService:
    @staticmethod
    def create_user(username, password_hash, bot9_token):
        user = User(username=username, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        DataService.save_bot9_token(user.id, bot9_token)
        return user
    
    @staticmethod
    def save_bot9_token(user_id, bot9_token):
        token = Token(user_id=user_id, bot9_token=bot9_token)
        db.session.add(token)
        db.session.commit()
        return token
    
    @staticmethod
    def get_user_by_id(user_id):
        return User.query.filter_by(id=user_id).first()

    @staticmethod
    def get_chat_by_id(chat_id):
        return Chat.query.get(chat_id)
    
    @staticmethod
    def get_chats_by_user_id(user_id):
        return Chat.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def update_bot9_token(user_id, new_token):
        token = Token.query.filter_by(user_id=user_id).first()
        if token:
            token.bot9_token = new_token
            db.session.commit()
        return token

    @staticmethod
    def create_chat(user_id, bot9_chatbot_id):
        new_chat = Chat(user_id=user_id, bot9_chatbot_id=bot9_chatbot_id)
        db.session.add(new_chat)
        db.session.commit()
        print(f"New Chat created with ID: {new_chat.id}")
        return str(new_chat.id)

    @staticmethod
    def save_message(chat_id, role, content, tool_use_id=None, tool_use_input=None, tool_name=None, tool_result=None):
        message = Message(
            chat_id=chat_id,
            role=role,
            content=content,
            tool_name=tool_name,
            tool_use_id=tool_use_id,
            tool_input=tool_use_input,
            tool_result=tool_result
        )
        db.session.add(message)
        db.session.commit()
        return message
    
    @staticmethod
    def load_conversation(chat_id):
        messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.created_at).all()
        conversation = []
        for message in messages:
            if message.role == "user":
                if message.tool_result:
                    conversation.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": message.tool_use_id,
                                "content": message.tool_result
                            }
                        ]
                    })
                else:
                    conversation.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": message.content
                            }
                        ]
                    })
            elif message.role == "assistant":
                if message.tool_name:
                    conversation.append({
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": message.content
                            },
                            {
                                "type": "tool_use",
                                "id": message.tool_use_id,
                                "name": message.tool_name,
                                "input": message.tool_input
                            }
                        ]
                    })
                else:
                    conversation.append({
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": message.content
                            }
                        ]
                    })
        return conversation
    
    
    @staticmethod
    def get_bot9_token(chat_id):
        chat = Chat.query.filter(Chat.id == chat_id).first()
        if chat:
            return Token.query.filter(Token.user_id == chat.user_id).first().bot9_token
        return None
    
    @staticmethod
    def get_bot9_chatbot_id(chat_id):
        chat = Chat.query.filter(Chat.id == chat_id).first()
        if chat:
            return chat.bot9_chatbot_id
        return None
    
    @staticmethod
    def write_curl_to_database(chat_id, curl_data, action_name):
        new_curl = ActionCurls(chat_id=chat_id, curl_as_json=curl_data, action_name=action_name)
        db.session.add(new_curl)
        db.session.commit()
        return f"Action added to database with action_name='{new_curl.action_name}'"
    
    @staticmethod
    def get_curl_data(chat_id, action_name):
        curl_data = ActionCurls.query.filter(ActionCurls.chat_id == chat_id, ActionCurls.action_name == action_name).first()
        return curl_data.curl_as_json


    @staticmethod
    def fetch_and_store_chatbots(user_id, bot9_token):
        print(f"Fetching chatbots for user {user_id}")  # Added print statement
        url = 'https://apiv1.bot9.ai/api/auth/chatbot/'
        headers = {
            'accept': 'application/json, text/plain, */*',
            'authorization': f'Bearer {bot9_token}'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            chatbots_data = response.json()

            for chatbot in chatbots_data:
                existing_chatbot = Chatbots.query.filter_by(
                    bot9_chatbot_id=chatbot['id'],
                    user_id=user_id
                ).first()

                if existing_chatbot:
                    # Update existing chatbot
                    existing_chatbot.chatbot_name = chatbot['name']
                    existing_chatbot.chatbot_url = chatbot['url']
                else:
                    # Create new chatbot
                    new_chatbot = Chatbots(
                        bot9_chatbot_id=chatbot['id'],
                        chatbot_name=chatbot['name'],
                        chatbot_url=chatbot['url'],
                        user_id=user_id
                    )
                    db.session.add(new_chatbot)

            db.session.commit()
            print(f"Chatbots updated for user {user_id}")
            DataService.get_user_chatbots(user_id)
            return True
        except Exception as e:
            print(f"Error fetching or storing chatbots: {str(e)}")
            db.session.rollback()
            return False



    @staticmethod
    def get_user_chatbots(user_id):
        chatbots = Chatbots.query.filter_by(user_id=user_id).all()
        return chatbots
    
    @staticmethod
    def get_and_store_instructions(user_id):
        print(f"Getting instructions for user {user_id}")
        chatbots = DataService.get_user_chatbots(user_id)
        for chatbot in chatbots:
            bot9_token = DataService.get_bot9_token(user_id)
            url = f"https://apiv1.bot9.ai/api/rules/v2/{chatbot.bot9_chatbot_id}/instructions/"
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US,en;q=0.9',
                'authorization': f'Bearer {bot9_token}',
                'origin': 'https://app.bot9.ai'
            }
            response = requests.get(url, headers=headers)
            print(f"Response status code: {response.status_code}")
            if response.status_code == 200:
                instructions_data = response.json()
                print(f"Instructions data: {instructions_data}")
                for category in instructions_data:
                    try:
                        existing_category = ChatbotInstructions.query.filter_by(
                            bot9_instruction_category_id=category['id'],
                            chatbot_id=chatbot.id
                        ).first()
                        
                        if existing_category:
                            existing_category.instruction_category_name = category['name']
                            existing_category.instruction_category_description = category['description']
                            existing_category.updated_at = datetime.utcnow()
                        else:
                            new_category = ChatbotInstructions(
                                chatbot_id=chatbot.id,
                                bot9_instruction_category_id=category['id'],
                                instruction_category_name=category['name'],
                                instruction_category_description=category['description']
                            )
                            db.session.add(new_category)
                        
                        db.session.commit()
                    except IntegrityError:
                        db.session.rollback()
                        print(f"Category {category['id']} already exists, skipping...")

                    for instruction in category['instructions']:
                        try:
                            existing_instruction = ChatbotInstructions.query.filter_by(
                                bot9_instruction_id=instruction['id'],
                                chatbot_id=chatbot.id
                            ).first()
                            
                            if existing_instruction:
                                existing_instruction.instruction_name = instruction['instructionName']
                                existing_instruction.instruction_text = instruction['instructionText']
                                existing_instruction.updated_at = datetime.utcnow()
                            else:
                                new_instruction = ChatbotInstructions(
                                    chatbot_id=chatbot.id,
                                    bot9_instruction_id=instruction['id'],
                                    instruction_name=instruction['instructionName'],
                                    instruction_text=instruction['instructionText'],
                                    bot9_instruction_category_id=category['id']
                                )
                                db.session.add(new_instruction)
                            
                            db.session.commit()
                        except IntegrityError:
                            db.session.rollback()
                            print(f"Instruction {instruction['id']} already exists, skipping...")

                print(f"Instructions updated successfully for chatbot {chatbot.chatbot_name}")
            else:
                print(f"Error fetching instructions for chatbot {chatbot.chatbot_name}: {response.text}")
        
        return "Instructions update process completed"
    
    @staticmethod
    def get_chatbot_instructions(chatbot_id):
        print(f"Getting instructions for chatbot {chatbot_id}")  # Added print statement
        return ChatbotInstructions.query.filter_by(chatbot_id=chatbot_id).all()
    
    
    @staticmethod
    def refresh_user_data(user_id):
        print(f"Starting data refresh for user {user_id}")  # Added print statement
        # Get the user's Bot9 token
        bot9_token = DataService.get_bot9_token(user_id)
        if not bot9_token:
            return False, "Bot9 token not found for user"

        # Fetch and store chatbots
        chatbots_updated = DataService.fetch_and_store_chatbots(user_id, bot9_token)
        print(f"Chatbots updated for user {user_id}: {chatbots_updated}")  # Added print statement
        if not chatbots_updated:
            return False, "Failed to update chatbots"

        # Get and store instructions for each chatbot
        chatbots = Chatbots.query.filter_by(user_id=user_id).all()
        print(f"Found {len(chatbots)} chatbots for user {user_id}")  # Added print statement
        for chatbot in chatbots:
            instructions_result = DataService.get_and_store_instructions(user_id)
            print(f"Instructions updated for chatbot {chatbot.chatbot_name}: {instructions_result}")  # Added print statement
            if "Error" in instructions_result:
                return False, f"Failed to update instructions for chatbot {chatbot.chatbot_name}: {instructions_result}"

        print(f"Data refresh for user {user_id} completed successfully")  # Added print statement
        return True, "User data refreshed successfully"