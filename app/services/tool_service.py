import os
import re
import csv
import json
from .data_service import DataService
from .search_service import SearchService
from .anthropic_service import AnthropicService
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
        print(f"Loadoded tools \n\n --------------------{tools} \n\n -----------")
        return tools
    
    @staticmethod
    def write_to_file(ai_tool_name, ai_tool_description, ai_tool_link, ai_tool_category):
        file_name = 'output.csv'
        
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Current directory: {current_dir}")
        # Create the full file path
        file_path = os.path.join(current_dir, file_name)
        print(f"File path: {file_path}")
        
        # Check if the file exists, if not create it
        file_exists = os.path.isfile(file_path)
        
        # Open the file in append mode if it exists, or write mode if it doesn't
        mode = 'a' if file_exists else 'w'
        with open(file_path, mode, newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["ai_tool_name", "ai_tool_description", "ai_tool_link", "ai_tool_category"])
            writer.writerow([ai_tool_name, ai_tool_description, ai_tool_link, ", ".join(ai_tool_category)])
        
        action = "updated" if file_exists else "created"
        return f"File '{file_name}' has been {action} in the current directory and the content has been written successfully."

# This class can be called to process the tool use and call the required tool and return the tool result
class ToolsHandler:
    @staticmethod
    def process_tool_use(tool_name, tool_input, tool_use_id, chat_id):
        print(f"process_tool_use functioned called")
        if tool_name == "update_research_data":
            user_message = f"{tool_input['ai_tool_name'], tool_input['ai_tool_description'], tool_input['ai_tool_link'], tool_input['ai_tool_category']}"
            ai_tool_name = tool_input['ai_tool_name']
            ai_tool_description = tool_input['ai_tool_description']
            ai_tool_link = tool_input['ai_tool_link']
            ai_tool_category = tool_input['ai_tool_category']
            result = Tools.write_to_file(ai_tool_name, ai_tool_description, ai_tool_link, ai_tool_category)
            DataService.save_message(chat_id, "user", content=result, tool_use_id=tool_use_id, tool_result=result)
            return result
        elif tool_name == "web_search":
            result = SearchService.search(tool_input["query"])
            DataService.save_message(chat_id, "user", content=result, tool_use_id=tool_use_id, tool_result=result)
            return result
        else:
            return "Error: Invalid tool name"