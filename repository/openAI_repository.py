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
        promt_json = {}
        for i in range(3):
            promt_str = self.do_promt(input)
            try:
                promt_json = json.loads(promt_str)
                break
            except json.JSONDecodeError:
                if i == 2:
                    print(promt_str)
                    return "Failed to process request"

        if "error" in promt_json or "top" not in promt_json or "bottom" not in promt_json:
            if "error" in promt_json and promt_json["error"] == "gender":
                # enviar "Inclou per a quin gènere és l'outfit."
                return "Please specify for which gender the outfit is"
                #self.whats_service.send_msg(
                    #data.uid, "Please specify for which gender the outfit is"
                #)
            elif "error" in promt_json and promt_json["error"] == "object":
                return "Please give more detail for the outfit description"
                #self.whats_service.send_msg(
                    #data.uid, "Please give more detail for the outfit description"
                #)
            elif len(messages) > 3:
                self.mongo_service.drop_messages(data.uid)
                self.whats_service.send_msg(data.uid, "Too many failures, try again")
                return "Too many promt failures, resetting. Try again"
            else:
                return "Please be more specific with your request"

        # enviar a inditex promt_json
        # processar promt_json return

        # return promt_json
        self.mongo_service.drop_messages(data.uid)
        #self.whats_service.send_msg(
            #data.uid, f"top: {promt_json['top']}, bottom: {promt_json['bottom']}"
        #)
        return f"top: {promt_json['top']}, bottom: {promt_json['bottom']}"

    def do_promt(self, prompt: str) -> str:
        response = self.oai_client.responses.parse(
            model="gpt-4.1",
            instructions="""You are an Outfit Designer. You will be given a set of plain‑text constraints describing a person and their outfit preferences.
            Output Schema
            Your entire response must be a single JSON object and nothing else. There are three possible cases:
            Valid outfit
            {
                "top":   "<gender> <top_type> <color>",
                "bottom":"<gender> <bottom_type> <color>"
            }
            <gender> is either "man" or "woman".
            <top_type> is one of: "shirt", "blouse", "jacket", "sweater", "tank", etc.
            <bottom_type> is one of: "pants", "shorts", "skirt", "jeans", "trousers", etc.
            <color> is a basic color name in lowercase (e.g. "black", "red", "navy", "beige", etc.).
            All three elements are separated by a single space; do not include extra whitespace or punctuation.
            Missing gender
            If the constraints do not specify “man” or “woman”, output:
            {
                "error": "gender"
            }
            Missing outfit information
            If there is no information from which you can choose a top or bottom (e.g. no mention of style, season, formality, etc.), output:
            {
                "error": "outfit"
            }
            """,
            input=prompt,
        )
        return response.output_text
