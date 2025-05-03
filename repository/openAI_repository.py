from model.data_request import ConversationRequest
from openai import OpenAI

class OpenAIRepository():
    def __init__(self):
        self.oai_client = OpenAI()
    def handle_message(self, data: ConversationRequest):
        return "done"

    def do_promt(self, prompt: str) -> str:
        response = self.oai_client.responses.create(
            model="gpt-4.1-nano",
            instructions="""You are an outfit designer. You are given constraints on which you must base your outfit.
            From the given constraints you must deduce gender, and a top and bottom clothing items.
            If all the necessary data is present, you return a json object containing two fields: a "top" field with
            which contains three words, "man"/"woman", the top clothing piece type and its color. The second field is "bottom" and
            also contains three words: "man"/"woman", the bottom clothing piece type and its color.
            If no gender is specified, return a json object containing an error field with "gender".""",
            input=prompt,
        )
        return response.output_text