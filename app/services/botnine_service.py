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
        botnine_api_payload = BotnineService.build_payload(chat_id, action_name, description)


        # Make the API request
        url = f"https://apiv1.bot9.ai/api/rules/{chatbot_id}/custom-actions"
        headers = {
            'authorization': f'Bearer {bot9_token}',
            'content-type': 'application/json'
        }
        print(f"botnine_api_payload: {botnine_api_payload}")
        response = requests.post(url, headers=headers, json=botnine_api_payload)
        print(response.json())
        return json.dumps(response.json())
    

    @staticmethod
    def build_payload(chat_id, action_name, description):
        curl_data_str = DataService.get_curl_data(chat_id, action_name)
        curl_data = json.loads(curl_data_str)
        
        base_url = curl_data['url']
        curl_method = curl_data['method']
        curl_headers = curl_data['headers']
        curl_body = curl_data['body']

        # Extract path and query parameters
        url_parts = base_url.split('?')
        curl_pathParams = [param for param in url_parts[0].split('/') if '{' in param and '}' in param]
        curl_queryParams = []
        if len(url_parts) > 1:
            curl_queryParams = [param.split('=')[0] for param in url_parts[1].split('&')]

        # Parse the body
        body_params = [
            {
                "key": key,
                "value": f"{{{{{key}}}}}",
                "type": "string"
            } for key in curl_body.keys()
        ]

        payload = {
            "name": action_name,
            "description": description,
            "meta": {
                "method": curl_method,
                "url": base_url.replace("${", "{{").replace("}", "}}"),
                "headers": {k: v.replace("${", "{{").replace("}", "}}") for k, v in curl_headers.items()},
                "pathParams": curl_pathParams,
                "queryParams": curl_queryParams,
                "body": body_params
            },
            "actionType": "http_request",
            "isSideEffect": False
        }
        print(f"payload: \n\n--------------------\n{payload}\n--------------------\n")
        return payload