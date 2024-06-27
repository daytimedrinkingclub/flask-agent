import os
import json
import requests
from .data_service import DataService

class BotnineService:
    @staticmethod
    def create_action(chat_id, action_name, curl_file_name, description):
        # Read the curl file
        bot9_token = DataService.get_bot9_token(chat_id)
        chatbot_id = DataService.get_chatbot_id(chat_id)


        # Parse the curl content
        botnine_api_payload = BotnineService.build_payload(curl_file_name, action_name, description)


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
    def build_payload(curl_file_name, action_name, description):
        curl_file_path = os.path.join(os.path.dirname(__file__), curl_file_name)
        with open(curl_file_path, 'r') as file:
            curl_content = file.read().strip()

        print(f"curl_content: {curl_content}")

        # Parse curl command
        curl_parts = curl_content.split()
        curl_method = ""
        curl_url = ""
        curl_headers = {}
        curl_body = ""

        i = 1  # Skip 'curl'
        while i < len(curl_parts):
            if curl_parts[i] == '-X':
                curl_method = curl_parts[i + 1]
                i += 2
            elif curl_parts[i] == '-H':
                header = curl_parts[i + 1].split(':', 1)  # Split on first colon only
                if len(header) == 2:
                    curl_headers[header[0].strip()] = header[1].strip()
                i += 2
            elif curl_parts[i] == '-d':
                curl_body = curl_parts[i + 1].strip("'")
                i += 2
            elif curl_parts[i].startswith('http'):
                curl_url = curl_parts[i]
                i += 1
            else:
                i += 1

        # Extract path and query parameters
        url_parts = curl_url.split('?')
        base_url = url_parts[0]
        curl_pathParams = [param for param in base_url.split('/') if '{' in param and '}' in param]
        curl_queryParams = []
        if len(url_parts) > 1:
            curl_queryParams = [param.split('=')[0] for param in url_parts[1].split('&')]

        # Parse the body
        body_params = []
        try:
            body_json = json.loads(curl_body)
            for key, value in body_json.items():
                body_params.append({
                    "key": key,
                    "value": f"{{{{{key}}}}}",  # Double braces for escaping
                    "type": "string"
                })
        except json.JSONDecodeError:
            # If JSON parsing fails, add a raw body parameter
            body_params.append({
                "key": "raw_body",
                "value": curl_body,
                "type": "string"
            })

        payload = {
            "name": action_name,
            "description": description,
            "meta": {
                "method": curl_method,
                "url": base_url.replace("${", "{{").replace("}", "}}"),  # Replace ${} with {{}}
                "headers": {k: v.replace("${", "{{").replace("}", "}}") for k, v in curl_headers.items()},
                "pathParams": curl_pathParams,
                "queryParams": curl_queryParams,
                "body": body_params
            },
            "actionType": "http_request",
            "isSideEffect": False
        }
        print(f"payload: {payload}")
        return payload