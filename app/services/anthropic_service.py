import os
import anthropic


prompts = {
    "positive_news_prompt": 
    """
    Your task is to analyse the news data provided and write a detailed optimistic summary of the news if possible.
    """,
    "negative_news_prompt":
    """
    Your task is to analyse the news data provided and write a detailed pessimistic summary of the news if possible.
    """
}

class AnthropicService:
    @staticmethod
    def prompt_selector(tool_name):
        if tool_name == "positive_news_analysis":
            return prompts["positive_news_prompt"]
        elif tool_name == "negative_news_analysis":
            return prompts["negative_news_prompt"]

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