from model.data_request import ConversationRequest
from service.mongodb_service import MongoDBService
from service.whats_service import WhatsService
from openai import OpenAI
import json
from fastapi import HTTPException


class OpenAIRepository:
    def __init__(self):
        self.oai_client = OpenAI()
        self.mongo_service = MongoDBService()
        self.whats_service = WhatsService()

    def handle_message(self, data: ConversationRequest):
        self.mongo_service.add_message(data)
        messages = [x["msg"] for x in self.mongo_service.get_messages(data.uid)]
        input = " ".join(messages)
        promt_str = self.do_promt(input)
        print(promt_str)
        try:
            promt_json = json.loads(promt_str)
        except json.JSONDecodeError:
            print(promt_str)
            raise HTTPException(status_code=500, detail="Wrong chatgpt output")

        if "error" in promt_json:
            if promt_json["error"] == "gender":
                # enviar "Inclou per a quin gènere és l'outfit."
                self.whats_service.send_msg(
                    data.uid, "Please specify for which gender the outfit is"
                )
            elif promt_json["error"] == "object":
                self.whats_service.send_msg(
                    data.uid, "Please give more detail for the outfit description"
                )
                pass
            if len(messages) > 3:
                self.mongo_service.drop_messages(data.uid)
                self.whats_service.send_msg(data.uid, "Too many failures, try again")
                return "too many errors"

            return "promt error"

        # enviar a inditex promt_json
        # processar promt_json return

        # return promt_json
        self.whats_service.send_msg(
            data.uid, f"top: {promt_json['top']}, bottom: {promt_json['bottom']}"
        )
        self.mongo_service.drop_messages(data.uid)
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
