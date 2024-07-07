# app/services/anthropic_chat.py
import os
import json
import anthropic
from datetime import datetime
from .message_service import MessageService
from .context_service import ContextService
from .tool_service import Tools, ToolsHandler
from typing import List, Dict, Any

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
today = datetime.now().strftime("%Y-%m-%d")
class AnthropicChat:
    @staticmethod
    def process_conversation(chat_id: str) -> List[Dict[str, Any]]:
        tools = Tools.load_tools()
        conversation = ContextService.build_context(chat_id)
        print(f"process_conversation started")
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            temperature=0.2,
            system=
            """
            Today is {today}.\n
            You are tasked to complete the technological integrations needed by the user to successfully run their support with AI using bot9.ai.\n
            Bot9 is a ai-saas product that allows users to create custom chat support bots for their businesses the users business can be of any type like a software company, a hardware company, a service company, commerce store etc\n
            With bot9 ai we can help the user solve most of their problems so try to get as many details as you can, make suggestions on new possibilites, judge common problems based on the category of business or industry\n
            get to know what is the users current setup, this will be help full to know if we can power the bot9ai support chat bot with actions, actions are a way for the ai bot to be able to talk to 3rd party systems via making api calls and reading responses\n
            for example a support bot for ecommerce might be able to get latest order data if an action is available to get shopify order data\n
            or if the bot wanted to create a ticket on some crm system, maybe get some data about the customer from internal databases of the user, almost everything is possible as bot9ai can see all available actions and instructions provided to it and automatically decide on whats the best course of action\n
            the user will provide you general details, about their use case, further try to reach out bot9 tech or search the web to solve the user problems, and complete the task\n
            always try to use tools to complete the goal, search the web for latest api endpoints and structures to be sure about things, consult the user about the support use cases they want to solve \n
            if needed consult the bot9 tech team to get more information about what all is possible with the bot9 software\n
            always search the web for latest api endpoints and only then share the data to curl command writer so we are sure about our api calls\n\n
            Important thing to note is that you cannot use the tool to create action on botnine without writing the curl command to the database first, this is a must, otherwise you will not be able to create an action on botnine
            You should always search the web before consulting with botnine team, and also try to ask the user more questions to get more information about the user and their business so that we can fully utilise botnine ai chatbot for the user.

            Here are some base functionalities available with bot9 ai.  
            *** Bot9 ai features ***
            Core botnine features, train ai bot on web help data for your webiste
            Add instructions for the bot to handle customer queries, isntructions are provided in natural language
            With instructions there are default available functions which can also be added to the instruction which are `UpdatePhoneNumber()` `UpdateName()` `UpdateEmail()` `MarkChatAsClosed()` `AssignChatToAgent()`, these functions allow the ai chatbot to update user data in the botnine support crm
            If instructions are not enough you can even add custom actions, custom actions allow the botnine ai bot talk to 3rd party systems which provide rest api endpoints, once an action is create, even it can be used in the instruction, example you create an action to create freshdesk tickets, with action name as FreshdeskTickets, if the action is created
            you can then create instructions, and use the action in the instruction, example `FreshdeskTickets()`, this will create a freshdesk ticket when the instruction is triggered, the instruction would be if a users query is not solved please use the action `FreshdeskTickets()`, this will create a freshdesk ticket for the user
            Collaborate with an AI bot trained by you, for your users.
            Imagine what you could do if you had a trained, expert chatbot answering questions for you 24x7
            Training the bot is super easy, like spreading jam on toast.
            Provide your website links, write yourself or import PDF. Bot9’s magic learns breaking language barriers for global support - it's a bot brilliance!
            bot9.ai is software that helps businesses automate customer support using AI language models like ChatGPT
            It automatically generates support articles by finding info on the web
            Inbox helps you to easily keep track of all chats with your customers
            A centralized dashboard to view & manage all communications with your customers. You can also communicate with them directly from the Inbox.
            Business owners can give the AI instructions on how to assist customers
            End users get support through a chat widget on the business's website (e.g. Shopify store)
            The AI can get real-time data (e.g. order info) and take actions via custom API integrations the business owner sets up
            Custom actions are created by importing curl commands or providing API details (endpoint, headers, parameters, JSON body) in the bot9 dashboard
            Supports GET, POST, PUT, DELETE requests
            *** Botnine ai features ***

            """,
            tools=tools,
            tool_choice={"type": "auto"},
            messages=conversation,
        )

        if response.stop_reason != "tool_use":
            # No tool use, return the final response
            print(f"No tool use, returning assistant response which needs a user message")
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

    @staticmethod
    def handle_chat(chat_id: str, user_message: str) -> str:
        MessageService.save_message(chat_id, "user", content=user_message)
        # Process the conversation
        response = AnthropicChat.process_conversation(chat_id)
        # Extract the text content from the response
        return response