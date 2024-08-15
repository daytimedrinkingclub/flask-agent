# import os
# import anthropic
# from .tool_service import Tools


# class CurlService:
#     @staticmethod
#     def call_curl_converter(user_message):
#         tools = Tools.curl_tool()
#         response = anthropic.Anthropic().messages.create(
#             model="claude-3-5-sonnet-20240620",
#             max_tokens=4000,
#             tools=tools,
#             temperature=0,
#             tool_choice={"type": "tool", "name": "curl_converter"},
#             messages=[
#                 {"role": "user", "content": user_message}
#             ]
#         )

        
#         print(f"Tool use detected, processing tool use")
#         tool_use = next(block for block in response.content if block.type == "tool_use")

#         print(f"Tool Name: {tool_use.name}")
#         print(f"Tool Input: {tool_use.input}")
#         tool_input = tool_use.input
#         tool_input_str = str(tool_input)
#         return tool_input_str
    
