

class AnthropicChat:
    @staticmethod
    def process_conversation(chat_id: str) -> str:
        # app/services/anthropic_chat.py
        import os
        import json
        import anthropic
        from datetime import datetime
        from ..chat_data.chat_service import ChatService
        from ..chat_data.message_service import MessageService
        from ..chat_data.context_service import ContextService
        from ..tool_handlers.tool_service import Tools, ToolsHandler

        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        today = datetime.now().strftime("%Y-%m-%d")
        tools = Tools.load_tools()
        conversation = ContextService.build_context(chat_id)
        with open('app/services/prompts/system_main.txt', 'r', encoding='utf-8') as file:
            system_prompt = file.read().format(today=today)
        print(f"process_conversation started")
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            temperature=0.2,
            system=system_prompt,
            tools=tools,
            tool_choice={"type": "auto"},
            messages=conversation,
        )

        if response.stop_reason != "tool_use":
            # No tool use, save the message and update chat status
            print(f"No tool use, saving assistant response and updating chat status")
            MessageService.save_message(chat_id, "assistant", content=response.content[0].text)
            return response

        # Handle tool use
        print(f"Tool use detected, processing tool use")
        tool_use = next(block for block in response.content if block.type == "tool_use")

        print(f"Tool Name: {tool_use.name}")
        
        MessageService.save_message(chat_id, "assistant", content=response.content[0].text, tool_use_id=tool_use.id, tool_use_input=tool_use.input, tool_name=tool_use.name)

        tool_result = ToolsHandler.process_tool_use(tool_use.name, tool_use.input, tool_use.id, chat_id)

        print(f"Tool Result received")

        if tool_result:
            # If a tool result is received, build the latest context and call process_conversation again
            print(f"Tool Result received, building context again to simulate the converstaion")
            conversation = ContextService.build_context(chat_id)
            print(f"Context built, new context length: {len(conversation)}")
            return AnthropicChat.process_conversation(chat_id)


def handle_chat(chat_id: str) -> str:

    # Process the conversation with the new user input
    return AnthropicChat.process_conversation(chat_id)