import os
import json
import requests
from .data_service import DataService

class BotnineService:
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
        return json.dumps(response.json())
    

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
        