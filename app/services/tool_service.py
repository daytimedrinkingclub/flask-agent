import os
import re
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
    def write_to_file(file_name, positive_news, negative_news, positive_news_sources, negative_news_sources):
        # Ensure the file has a .txt extension
        if not file_name.endswith('.txt'):
            file_name += '.txt'
        
        file_content = f"Positive News: {positive_news}\nNegative News: {negative_news}\nPositive News Sources: {positive_news_sources}\nNegative News Sources: {negative_news_sources}"

        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Current directory: {current_dir}")
        # Create the full file path
        file_path = os.path.join(current_dir, file_name)
        print(f"File created at path: {file_path}")
        # Create and write to the text file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(file_content)
        
        return f"File '{file_name}' has been created in the current directory and the content has been written successfully."

# This class can be called to process the tool use and call the required tool and return the tool result
class ToolsHandler:
    @staticmethod
    def process_tool_use(tool_name, tool_input, tool_use_id, chat_id):
        print(f"process_tool_use functioned called")
        if tool_name == "positive_news_analysis":
            user_message = f"{tool_input['news_data']}"
            result = AnthropicService.call_anthropic(tool_name, user_message)
            DataService.save_message(chat_id, "user", content=result, tool_use_id=tool_use_id, tool_result=result)
            return result
        elif tool_name == "web_search":
            result = SearchService.search(tool_input["query"])
            DataService.save_message(chat_id, "user", content=result, tool_use_id=tool_use_id, tool_result=result)
            return result
        elif tool_name == "negative_news_analysis":
            user_message = f"{tool_input['news_data']}"
            result = AnthropicService.call_anthropic(tool_name, user_message)
            DataService.save_message(chat_id, "user", content=result, tool_use_id=tool_use_id, tool_result=result)
            return result
        elif tool_name == "update_news_data":
            result = Tools.write_to_file(tool_input["positive_news"], tool_input["negative_news"], tool_input["postive_news_sources"], tool_input["negative_news_sources"])
            DataService.save_message(chat_id, "user", content=result, tool_use_id=tool_use_id, tool_result=result)
            return result
        else:
            return "Error: Invalid tool name"