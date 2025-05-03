from model.data_request import ConversationRequest
from service.mongodb_service import MongoDBService
from openai import OpenAI
import json
from fastapi import HTTPException


class OpenAIRepository:
    def __init__(self):
        self.oai_client = OpenAI()
        self.mongo_service = MongoDBService()

    def handle_message(self, data: ConversationRequest):
        self.mongo_service.add_message(data)
        messages = [x["msg"] for x in self.mongo_service.get_messages(data.uid)]
        input = " ".join(messages)
        promt_str = self.do_promt(input)
        print(promt_str)
        try:
            promt_json = json.loads(promt_str)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Wrong chatgpt output")

        if "error" in promt_json:
            if promt_json["error"] == "gender":
                # enviar "Inclou per a quin gènere és l'outfit."
                pass
            elif promt_json["error"] == "object":
                # enviar "Especifica millor com vols que sigui l'outfit"
                pass

            return "promt error"

        # enviar a inditex promt_json
        # processar promt_json return

        # return promt_json
        return "done"

    def do_promt(self, prompt: str) -> str:
        response = self.oai_client.responses.create(
            model="gpt-4.1-mini",
            instructions="""You are an outfit designer. You are given constraints on which you must base your outfit.
            From the given constraints you must deduce gender, and a top and bottom clothing items.
            If all the necessary data is present, you return a json object containing two fields: a "top" field with
            which contains a string of three space-separated words, "man"/"woman", the top clothing piece type and its color.
            The second field is "bottom" and aslo contains three space-separated words: "man"/"woman", the bottom clothing piece type and its color.
            If no gender is specified, return a json object containing an error field with "gender".
            If no information that may be used to determine the type of outfit, return a json object containing an error field with \"outfit\"""",
            input=prompt,
        )
        return response.output_text
