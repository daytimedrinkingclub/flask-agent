import os
import re
import json
from .data_service import DataService
from .search_service import SearchService
from .anthropic_service import AnthropicService
from .botnine_service import BotnineService
# This class is called by the Toolhandler function
class Tools:
    @staticmethod
    def load_tools():
        tools_dir = os.path.join(os.path.dirname(__file__), "tools")
        tools = []
        for file_name in os.listdir(tools_dir):
            if file_name.endswith(".json"):
                file_path = os.path.join(tools_dir, file_name)
                with open(file_path, "r") as file:
                    tool_data = json.load(file)
                    tools.append(tool_data)
        print(f"Tools loaded and returned {len(tools)} tools")
        return tools
    
    @staticmethod
    def curl_tool():
        tools_dir = os.path.join(os.path.dirname(__file__), "tools/curl_converter.json")
        tools = []
        with open(tools_dir, "r") as file:
            tool_data = json.load(file)
            tools.append(tool_data)
        print(f"Tools loaded and returned {len(tools)} tools")
        return tools

# This class can be called to process the tool use and call the required tool and return the tool result
class ToolsHandler:
    @staticmethod
    def process_tool_use(tool_name, tool_input, tool_use_id, chat_id):
        print(f"process_tool_use functioned called")
        if tool_name == "consult_subhash":
            user_message = f"{tool_input['question']}"
            result = AnthropicService.call_anthropic(tool_name, user_message)
            DataService.save_message(chat_id, "user", content=result, tool_use_id=tool_use_id, tool_result=result)
            return result
        elif tool_name == "web_search":
            result = SearchService.search(tool_input["query"])
            DataService.save_message(chat_id, "user", content=result, tool_use_id=tool_use_id, tool_result=result)
            return result
        elif tool_name == "curl_command_writer":
            user_message = f"{tool_input['endpoint_details']}\n Method: {tool_input['method_details']}\n Headers: {tool_input['header_details']}\n Parameters: {tool_input['parameter_details']}\n Body: {tool_input['body_details']}\n Additional Info: {tool_input['additional_details']}"
            result = AnthropicService.call_anthropic(tool_name, user_message)
            DataService.save_message(chat_id, "user", content=result, tool_use_id=tool_use_id, tool_result=result)
            return result
        elif tool_name == "create_botnine_action":
            action_status = BotnineService.create_action(chat_id, tool_input["action_name"], tool_input["action_description"])
            DataService.save_message(chat_id, "user", content=action_status, tool_use_id=tool_use_id, tool_result=action_status)
            return action_status
        elif tool_name == "create_botnine_instruction":
            instruction_status = BotnineService.create_botnine_instruction(chat_id, tool_input["instruction_name"], tool_input["instruction_description"], tool_input.get("bot9_chatbot_id"))
            DataService.save_message(chat_id, "user", content=instruction_status, tool_use_id=tool_use_id, tool_result=instruction_status)
            return instruction_status
        elif tool_name == "write_curl_to_database":
            result = DataService.write_curl_to_database(chat_id, tool_input["curl_as_json"], tool_input["action_name"])
            DataService.save_message(chat_id, "user", content=result, tool_use_id=tool_use_id, tool_result=result)
            return result
        else:
            return "Error: Invalid tool name"