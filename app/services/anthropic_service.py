import os
import anthropic


prompts = {
    "consult_subhash": 
    """
    You are the techinal lead for bot9.ai an AI based support software, you are tasked to provide assitance to the support queries our onboarding team
    bot9.ai is software that helps businesses automate customer support using AI language models like ChatGPT
    It automatically generates support articles by finding info on the web
    Business owners can give the AI instructions on how to assist customers
    End users get support through a chat widget on the business's website (e.g. Shopify store)
    The AI can get real-time data (e.g. order info) and take actions via custom API integrations the business owner sets up
    Custom actions are created by importing curl commands or providing API details (endpoint, headers, parameters, JSON body) in the bot9 dashboard
    Supports GET, POST, PUT, DELETE requests
    """,
    "curl_command_writer":
    """
    You are task is to write REST API curls for the user, the user will provide available data and return them only and only with one cuerl command
    """,

}

class AnthropicService:
    @staticmethod
    def prompt_selector(tool_name):
        if tool_name == "consult_subhash":
            return prompts["consult_subhash"]
        elif tool_name == "curl_command_writer":
            return prompts["curl_command_writer"]

        

    def call_anthropic(tool_name, user_message):
        prompt = AnthropicService.prompt_selector(tool_name)
        response = anthropic.Anthropic().messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2000,
            system=prompt,
            temperature=0,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        return response.content[0].text