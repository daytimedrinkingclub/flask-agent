import os
import json
import requests
from datetime import datetime

from .data_service import DataService

class BotnineService:
    @staticmethod
    def get_chatbots_data(chat_id):
        bot9_token = DataService.get_bot9_token(chat_id)
        url = f"https://apiv1.bot9.ai/api/chatbots"
        headers = {
            'authorization': f'Bearer {bot9_token}'
        }
        response = requests.get(url, headers=headers)
        return response.json()

    @staticmethod
    def create_action(chat_id, action_name, description):
        # Read the curl file
        bot9_token = DataService.get_bot9_token(chat_id)
        chatbot_id = DataService.get_chatbot_id(chat_id)


        # Parse the curl content
        print(f"chat_id: {chat_id}, action_name: {action_name}, description: {description}")
        botnine_api_payload = BotnineService.build_payload(chat_id, action_name, description)
        print(f"botnine_api_payload: {botnine_api_payload}")

        # Make the API request
        url = f"https://apiv1.bot9.ai/api/rules/{chatbot_id}/custom-actions"
        headers = {
            'authorization': f'Bearer {bot9_token}',
            'content-type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, json=botnine_api_payload)
        print(f"response: {response.json()}")
        
        if response.status_code == 201:
            response_data = response.json()
            create_action_name = response_data['name']
            return f"Action successfully created with name: {create_action_name}"
        else:
            return f"Error creating action: {response.text}"
    

    @staticmethod
    def build_payload(chat_id, action_name, description):
        curl_data_str = DataService.get_curl_data(chat_id, action_name)
        curl_data = json.loads(curl_data_str)
        
        base_url = curl_data['url']
        curl_method = curl_data['method']
        curl_headers = curl_data['headers']
        curl_params = curl_data.get('params', {})
        curl_body = curl_data.get('body', {})

        # Extract path parameters
        path_parts = base_url.split('/')
        curl_pathParams = [
            {
                "key": param.strip('${}'),
                "value": f"{{{{{param.strip('${}')}}}}}", 
                "description": "",
                "type": "string"
            }
            for param in path_parts if param.startswith('${') and param.endswith('}')
        ]
        
        # Update base_url to use double curly brackets
        base_url = '/'.join([f"{{{{{p.strip('${}')}}}}}" if p.startswith('${') and p.endswith('}') else p for p in path_parts])

        payload = {
            "name": action_name,
            "description": description,
            "meta": {
                "method": curl_method,
                "url": base_url,
                "headers": {k: f"{{{{{v.strip('${}')}}}}}" if v.startswith('${') else v for k, v in curl_headers.items()},
                "logoURL": "",
                "code": "",
                "denoDeploymentId": "",
            },
            "actionType": "http_request",
            "isSideEffect": False
        }

        # Only add pathParams if there are any
        if curl_pathParams:
            payload['meta']['pathParams'] = curl_pathParams

        if curl_method.upper() == 'GET':
            payload['meta']['queryParams'] = [
                {
                    "key": key,
                    "value": f"{{{{key}}}}",
                    "description": f"Parameter: {key}",
                    "type": "string"  # Simplified type handling
                } for key in curl_params.keys()
            ]
        elif curl_method.upper() in ['POST', 'PUT', 'PATCH']:
            payload['meta']['body'] = [
                {
                    "key": key,
                    "value": f"{{{{{value.strip('${}')}}}}}" if isinstance(value, str) and value.startswith('${') else value,
                    "description": f"{key} Description",
                    "type": "string"  # Simplified type handling
                } for key, value in curl_body.items()
            ]
        elif curl_method.upper() == 'DELETE':
            # DELETE method doesn't have a body
            pass

        print(f"payload: \n\n--------------------\n{payload}\n--------------------\n")
        return payload
        
    @staticmethod
    def create_botnine_instruction(chat_id, instruction_name, instruction_description):
        # Read the curl file
        bot9_token = DataService.get_bot9_token(chat_id)
        chatbot_id = DataService.get_chatbot_id(chat_id)

        # Prepare the API endpoint
        url = f"https://apiv1.bot9.ai/api/rules/{chatbot_id}/instructions"

        # Prepare the headers
        headers = {
            'accept': 'application/json, text/plain, */*',
            'authorization': f'Bearer {bot9_token}',
            'content-type': 'application/json'
        }

        # Prepare the payload
        payload = {
            "instructionName": instruction_name,
            "instructionText": instruction_description
        }

        try:
            # Make the API call
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for non-200 status codes

            # Return the response JSON if successful
            response_data = response.json()
            instruction_id = response_data['id']
            instruction_name = response_data['instructionName']
            return f"Instruction successfully created with name: {instruction_name} and id: {instruction_id}"

        except requests.RequestException as e:
            # Handle any errors that occur during the request
            return f"Error creating Bot9 instruction: {str(e)}"
