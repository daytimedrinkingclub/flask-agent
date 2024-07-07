from sqlalchemy.exc import IntegrityError
from datetime import datetime
import requests
import logging
from typing import List, Dict, Any, Tuple
from ..extensions import db
from ..models.models import Chatbot, Chat, ChatbotInstruction, ChatbotAction
from .token_service import TokenService

class Bot9DataService:
    @staticmethod
    def fetch_and_store_bot9_chatbots(user_id: str, bot9_token: str) -> Tuple[bool, str]:
        logging.info(f"Fetching chatbots for user {user_id}")
        url = 'https://apiv1.bot9.ai/api/auth/chatbot/'
        headers = {
            'accept': 'application/json, text/plain, */*',
            'authorization': f'Bearer {bot9_token}'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            logging.info(f"Response status code: {response.status_code}")
            chatbots_data: List[Dict[str, Any]] = response.json()

            # Prepare bulk update/insert
            to_update = []
            to_insert = []
            for chatbot in chatbots_data:
                existing_chatbot = Chatbot.query.filter_by(
                    bot9_chatbot_id=chatbot['id'],
                    user_id=user_id
                ).first()

                if existing_chatbot:
                    existing_chatbot.chatbot_name = chatbot['name']
                    existing_chatbot.chatbot_url = chatbot['url']
                    to_update.append(existing_chatbot)
                else:
                    new_chatbot = Chatbot(
                        bot9_chatbot_id=chatbot['id'],
                        bot9_chatbot_name=chatbot['name'],
                        bot9_chatbot_url=chatbot['url'],
                        user_id=user_id
                    )
                    to_insert.append(new_chatbot)

            # Bulk update and insert
            if to_update:
                db.session.bulk_save_objects(to_update)
            if to_insert:
                db.session.bulk_save_objects(to_insert)
            
            db.session.commit()
            logging.info(f"Chatbots updated for user {user_id}")
            return True, "Chatbots updated successfully"
        except requests.RequestException as e:
            logging.error(f"Error fetching chatbots: {str(e)}")
            return False, f"Error fetching chatbots: {str(e)}"
        except Exception as e:
            logging.error(f"Error storing chatbots: {str(e)}")
            db.session.rollback()
            return False, f"Error storing chatbots: {str(e)}"

    @staticmethod
    def get_user_chatbots(user_id):
        chatbots = Chatbot.query.filter_by(user_id=user_id).all()
        return chatbots

    @staticmethod
    def get_and_store_bot9_instructions(user_id):
        print(f"Getting instructions for user {user_id}")
        chatbots = Bot9DataService.get_user_chatbots(user_id)
        for chatbot in chatbots:
            bot9_token = TokenService.get_bot9_token(user_id)
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
                for category in instructions_data:
                    try:
                        existing_category = ChatbotInstruction.query.filter_by(
                            bot9_instruction_category_id=category['id'],
                            chatbot_id=chatbot.id
                        ).first()
                        
                        if existing_category:
                            existing_category.bot9_instruction_category_name = category['name']
                            existing_category.bot9_instruction_category_description = category['description']
                            existing_category.updated_at = datetime.utcnow()
                        else:
                            new_category = ChatbotInstruction(
                                bot9_chatbot_id=chatbot.id,
                                bot9_instruction_category_id=category['id'],
                                bot9_instruction_category_name=category['name'],
                                bot9_instruction_category_description=category['description']
                            )
                            db.session.add(new_category)
                        
                        db.session.commit()
                    except IntegrityError:
                        db.session.rollback()
                        print(f"Category {category['id']} already exists, skipping...")

                    for instruction in category['instructions']:
                        try:
                            existing_instruction = ChatbotInstruction.query.filter_by(
                                bot9_instruction_id=instruction['id'],
                                bot9_chatbot_id=chatbot.id
                            ).first()
                            
                            if existing_instruction:
                                existing_instruction.bot9_instruction_name = instruction['instructionName']
                                existing_instruction.bot9_instruction_text = instruction['instructionText']
                                existing_instruction.updated_at = datetime.utcnow()
                            else:
                                new_instruction = ChatbotInstruction(
                                    bot9_chatbot_id=chatbot.id,
                                    bot9_instruction_id=instruction['id'],
                                    bot9_instruction_name=instruction['instructionName'],
                                    bot9_instruction_text=instruction['instructionText'],
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
        print(f"Getting instructions for chatbot {chatbot_id}")
        return ChatbotInstruction.query.filter_by(bot9_chatbot_id=chatbot_id).first()
    
    
    @staticmethod
    def get_bot9_chatbot_id(user_id):
        chat = Chat.query.filter(Chat.user_id == user_id).first()
        if chat:
            return chat.bot9_chatbot_id
        return None
    
    @staticmethod
    def fetch_and_save_bot9_actions(user_id):
        print(f"Fetching actions for user {user_id}")
        chatbots = Bot9DataService.get_user_chatbots(user_id)
        for chatbot in chatbots:
            bot9_token = TokenService.get_bot9_token(user_id)
            url = f"https://apiv1.bot9.ai/api/actions/v2/{chatbot.bot9_chatbot_id}/actions/"
            headers = {
                'accept': 'application/json, text/plain, */*',
                'authorization': f'Bearer {bot9_token}'
            }