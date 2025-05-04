from model.data_request import ConversationRequest
from service.mongodb_service import MongoDBService
from service.inditex_service import InditexService
from service.whats_service import WhatsService
from openai import OpenAI
import json
from fastapi import HTTPException


class OpenAIRepository:
    def __init__(self):
        self.oai_client = OpenAI()
        self.mongo_service = MongoDBService()
        self.whats_service = WhatsService()
        self.inditex_service = InditexService()

    def handle_message(self, data: ConversationRequest):
        # self.mongo_service.add_message(data)
        # messages = [x["msg"] for x in self.mongo_service.get_messages(data.uid)]
        # input = " ".join(messages)
        promt_json = {}
        for i in range(3):
            promt_str = self.do_promt(data.message)
            try:
                promt_json = json.loads(promt_str)
                break
            except json.JSONDecodeError:
                if i == 2:
                    print(promt_str)
                    raise HTTPException(
                        status_code=500, detail="Failed to process request"
                    )

        if (
            "error" in promt_json
            or "top" not in promt_json
            or "bottom" not in promt_json
        ):
            if "error" in promt_json:
                # enviar "Inclou per a quin gènere és l'outfit."
                raise HTTPException(
                    status_code=422,
                    detail=promt_json["error"],
                )
                # self.whats_service.send_msg(
                # data.uid, "Please specify for which gender the outfit is"
                # )
            # elif len(messages) > 3:
            # self.mongo_service.drop_messages(data.uid)
            # self.whats_service.send_msg(data.uid, "Too many failures, try again")
            # raise HTTPException(
            # status_code=422,
            # detail="Too many promt failures, resetting. Please try again",
            # )
            else:
                raise HTTPException(
                    status_code=422, detail="Please be more specific with your request"
                )

        # enviar a inditex promt_json
        # processar promt_json return

        # return promt_json
        self.mongo_service.drop_messages(data.uid)
        # self.whats_service.send_msg(
        # data.uid, f"top: {promt_json['top']}, bottom: {promt_json['bottom']}"
        # )
        # return f"{promt_json['top']}"
        inditex_data = self.inditex_service.get_data(promt_json)
        return inditex_data

    def do_promt(self, prompt: str) -> str:
        response = self.oai_client.responses.parse(
            model="gpt-4.1",
            instructions="""You are an Outfit Designer. You will be given a set of plain‑text constraints describing a person and their outfit preferences.
            Your entire response must be a single JSON object and nothing else. The base case is:
            {
                "top":   "<gender> <top_type> <color>",
                "bottom":"<gender> <bottom_type> <color>"
            }
            <gender> is either "man" or "woman". You can use information inside the input to infer the gender.
            <top_type> is one of: "shirt", "blouse", "jacket", "sweater", "tank", etc.
            <bottom_type> is one of: "pants", "shorts", "skirt", "jeans", "trousers", etc.
            <color> is a basic color name in lowercase (e.g. "black", "red", "navy", "beige", etc.).
            The only exception to the top/bottom rule is dresses, where both top and bottom will both be a dress and may be different.
            All three elements are separated by a single space; do not include extra whitespace or punctuation.
            If the constraints are not sufficient to specify all of the fields above, return the following JSON object
            specifying why the error occured:
            {
                "error": "<error_cause>"
            }
            <error_cause> is the reason why the preferred output was not selected, in a user friendly format.
            """,
            input=prompt,
        )
        return response.output_text


def img_reply_promt(client, input, img_url):
    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": """You are given an image of a clothing item and a text description of what parts of that item to change.
                                You must output a textual description of the clothing peiece that would result from applying all the changes in the text
                                to the image's clothing item.""",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": img_url,
                    },
                    {"type": "input_text", "text": input},
                ],
            },
        ],
    )

    return response.output_text
