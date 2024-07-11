import requests
import logging

from ...extensions import db
from ...models.models import Chatbot, ChatbotInstructionCategory, ChatbotInstruction, ChatbotAction

class Bot9DataService:
    @staticmethod
    def fetch_bot9_chatbots(bot9_token):
        url = 'https://apiv1.bot9.ai/api/auth/chatbot/'
        headers = {
            'accept': 'application/json, text/plain, */*',
            'authorization': f'Bearer {bot9_token}'
        }
        response = requests.get(url, headers=headers)
        return response.json()

    @staticmethod
    def save_bot9_chatbots(user_id, chatbots_data):
        try:
            # Get existing chatbots for the user
            existing_chatbots = Chatbot.query.filter_by(user_id=user_id).all()
            existing_chatbot_ids = {chatbot.bot9_chatbot_id for chatbot in existing_chatbots}
            
            # Update or create chatbots
            for chatbot in chatbots_data:
                existing_chatbot = Chatbot.query.filter_by(bot9_chatbot_id=chatbot['id'], user_id=user_id).first()
                if existing_chatbot:
                    existing_chatbot.bot9_chatbot_name = chatbot['name']
                    existing_chatbot.bot9_chatbot_url = chatbot['url']
                else:
                    new_chatbot = Chatbot(
                        bot9_chatbot_id=chatbot['id'],
                        bot9_chatbot_name=chatbot['name'],
                        bot9_chatbot_url=chatbot['url'],
                        user_id=user_id
                    )
                    db.session.add(new_chatbot)
            
            db.session.commit()
            return True, "Chatbots updated successfully"
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error in save_bot9_chatbots: {str(e)}")
            return False, f"Error storing chatbots: {str(e)}"
    
    @staticmethod
    def save_bot9_instructions(bot9_chatbot_id, instruction_categories):
        try:
            # Check if the chatbot still exists
            chatbot = Chatbot.query.filter_by(bot9_chatbot_id=bot9_chatbot_id).first()
            if not chatbot:
                logging.warning(f"Attempted to save instructions for non-existent chatbot: {bot9_chatbot_id}")
                return False, "Chatbot does not exist"

            # Update or create instruction categories and instructions
            for category in instruction_categories:
                existing_category = ChatbotInstructionCategory.query.filter_by(
                    bot9_chatbot_id=bot9_chatbot_id,
                    bot9_instruction_category_id=category.get('id')
                ).first()

                if existing_category:
                    existing_category.bot9_instruction_category_name = category.get('name', 'Unnamed Category')
                    existing_category.bot9_instruction_category_description = category.get('description', '')
                else:
                    new_category = ChatbotInstructionCategory(
                        bot9_chatbot_id=bot9_chatbot_id,
                        bot9_instruction_category_id=category.get('id'),
                        bot9_instruction_category_name=category.get('name', 'Unnamed Category'),
                        bot9_instruction_category_description=category.get('description', '')
                    )
                    db.session.add(new_category)
                    db.session.flush()
                    existing_category = new_category

                for instruction in category.get('instructions', []):
                    existing_instruction = ChatbotInstruction.query.filter_by(
                        bot9_chatbot_id=bot9_chatbot_id,
                        bot9_instruction_id=instruction.get('id')
                    ).first()

                    if existing_instruction:
                        existing_instruction.bot9_instruction_name = instruction.get('instructionName', 'Unnamed Instruction')
                        existing_instruction.bot9_instruction_text = instruction.get('instructionText', '')
                        existing_instruction.is_active = instruction.get('isActive', True)
                        existing_instruction.category_id = existing_category.id
                    else:
                        new_instruction = ChatbotInstruction(
                            bot9_chatbot_id=bot9_chatbot_id,
                            bot9_instruction_id=instruction.get('id'),
                            bot9_instruction_name=instruction.get('instructionName', 'Unnamed Instruction'),
                            bot9_instruction_text=instruction.get('instructionText', ''),
                            is_active=instruction.get('isActive', True),
                            category_id=existing_category.id
                        )
                        db.session.add(new_instruction)
            
            db.session.commit()
            return True, "Instructions and categories updated successfully"
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error in save_bot9_instructions: {str(e)}")
            return False, f"Error updating instructions and categories: {str(e)}"

    @staticmethod
    def fetch_bot9_chatbot_instructions(chatbot_id, bot9_token):
        url = f"https://apiv1.bot9.ai/api/rules/v2/{chatbot_id}/instructions"
        headers = {
            'accept': 'application/json, text/plain, */*',
            'authorization': f'Bearer {bot9_token}'
        }
        response = requests.get(url, headers=headers)
        return response.json()


    @staticmethod
    def fetch_bot9_actions(bot9_chatbot_id, bot9_token):
        url = f"https://apiv1.bot9.ai/api/rules/{bot9_chatbot_id}/custom-actions"
        headers = {
            'accept': 'application/json, text/plain, */*',
            'authorization': f'Bearer {bot9_token}',
        }
        response = requests.get(url, headers=headers)
        return response.json()

    @staticmethod
    def save_bot9_actions(bot9_chatbot_id, actions):
        try:
            # First, remove all existing actions for this chatbot
            ChatbotAction.query.filter_by(bot9_chatbot_id=bot9_chatbot_id).delete()
            
            # Then add the new actions
            for action in actions:
                new_action = ChatbotAction(
                    bot9_chatbot_id=bot9_chatbot_id,
                    bot9_action_id=action['id'],
                    bot9_action_name=action['name'],
                    bot9_action_description=action.get('description', ''),
                    bot9_action_type=action.get('type', ''),
                    bot9_action_meta=action.get('meta', '')
                )
                db.session.add(new_action)
            
            db.session.commit()
            return True, "Actions saved successfully"
        except Exception as e:
            db.session.rollback()
            return False, f"Error storing actions: {str(e)}"

    @staticmethod
    def get_bot9_chatbot(user_id):
        chatbots = Chatbot.query.filter_by(user_id=user_id).all()
        return [
            {
                'bot9_chatbot_id': chatbot.bot9_chatbot_id,
                'bot9_chatbot_name': chatbot.bot9_chatbot_name,
                'bot9_chatbot_url': chatbot.bot9_chatbot_url,
                'instructions': [],  # Will be populated later
                'actions': []  # Will be populated later
            }
            for chatbot in chatbots
        ]

    @staticmethod
    def get_chatbot_instructions(bot9_chatbot_id):
        instructions = ChatbotInstruction.query.filter_by(bot9_chatbot_id=bot9_chatbot_id).all()
        return [
            {
                'bot9_instruction_id': instruction.bot9_instruction_id,
                'bot9_instruction_name': instruction.bot9_instruction_name,
                'bot9_instruction_text': instruction.bot9_instruction_text
            }
            for instruction in instructions
        ]

    @staticmethod
    def get_chatbot_actions(bot9_chatbot_id):
        return [
            {
                'bot9_action_id': action.bot9_action_id,
                'bot9_action_name': action.bot9_action_name,
                'bot9_action_description': action.bot9_action_description,
                'bot9_action_type': action.bot9_action_type
            }
            for action in ChatbotAction.query.filter_by(bot9_chatbot_id=bot9_chatbot_id).all()
        ]