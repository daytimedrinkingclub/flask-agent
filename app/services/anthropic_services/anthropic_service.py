import os
import anthropic

def load_prompt(filename):
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', filename)
    with open(prompt_path, 'r') as file:
        return file.read().strip()

prompts = {
    "consult_subhash": load_prompt("consult_subhash.txt"),
    "curl_command_writer": load_prompt("curl_command_writer.txt"),
}

class AnthropicService:
    @staticmethod
    def prompt_selector(tool_name):
        return prompts.get(tool_name, "")

    @staticmethod
    def call_anthropic(tool_name, user_message):
        prompt = AnthropicService.prompt_selector(tool_name)
        response = anthropic.Anthropic().messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            system=prompt,
            temperature=0.2,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        return response.content[0].text