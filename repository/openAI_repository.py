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
                    raise HTTPException(
                        status_code=500, detail="Failed to process request"
                    )

        if (
            "error" in promt_json
            or "top" not in promt_json
            or "bottom" not in promt_json
        ):
            if "error" in promt_json and promt_json["error"] == "gender":
                # enviar "Inclou per a quin gènere és l'outfit."
                raise HTTPException(
                    status_code=422,
                    detail="Please specify for which gender the outfit is",
                )
                # self.whats_service.send_msg(
                # data.uid, "Please specify for which gender the outfit is"
                # )
            elif "error" in promt_json and promt_json["error"] == "object":
                raise HTTPException(
                    status_code=422,
                    detail="Please give more detail for the outfit description",
                )
                # self.whats_service.send_msg(
                # data.uid, "Please give more detail for the outfit description"
                # )
            elif len(messages) > 3:
                self.mongo_service.drop_messages(data.uid)
                self.whats_service.send_msg(data.uid, "Too many failures, try again")
                raise HTTPException(
                    status_code=422,
                    detail="Too many promt failures, resetting. Please try again",
                )
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
        return {
            "top": {
                "name": "VESTIDO MIDI CON FRUNZIMIENTOS",
                "images": [
                    "https://static.zara.net/assets/public/7587/f989/308843249a30/943c1e461c25/02544324300-a1/02544324300-a1.jpg?ts=1745336480873&w=563",
                    "https://static.zara.net/assets/public/bab4/5761/f02145d6b898/671db378a49e/02544324300-e2/02544324300-e2.jpg?ts=1745416307689&w=563",
                    "https://static.zara.net/assets/public/1b0d/8aad/63f841d88376/0fec0cf93741/02544324300-e3/02544324300-e3.jpg?ts=1745416307940&w=563",
                    # ... más URLs de imágenes
                ],
                "price": 39.95,
                "link": "https://www.zara.com/es/ca/vestit-midi-amb-frunziments-p02544324.html?v1=446341665",
            },
            "bottom": {
                "name": "TEJANOS ZW COLLECTION BOOTCUT FULL LENGTH MID WAIST",
                "images": [
                    "https://static.zara.net/assets/public/6f84/6475/5ba6455e98bf/1c3573c54e70/08307050428-p/08307050428-p.jpg?ts=1733411264519&w=563",
                    "https://static.zara.net/assets/public/7de6/9978/115a4953b0fe/cb0b1c3be6e5/08307050428-a3/08307050428-a3.jpg?ts=1733411264739&w=563",
                    "https://static.zara.net/assets/public/3ec6/1e2a/13ac46858929/35bee5f29701/07223049428-000-e2/07223049428-000-e2.jpg?ts=1739804668806&w=563",
                    # ... más URLs de imágenes
                ],
                "price": 29.95,
                "link": "https://www.zara.com/es/ca/texans-zw-collection-bootcut-full-length-mid-waist-p07223049.html?v1=422669650",
            },
        }
        # return f"{promt_json['top']}"
        """
        inditex_data = self.inditex_service.get_data(promt_json)
        # return inditex_data
        ret = ""
        if "error" not in inditex_data["top"]:
            ret += f"Upper-body clothing piece: {inditex_data['top']['name']}, price: {inditex_data['top']['price']}€, shop link: {inditex_data['top']['link']}\n"
        if "error" not in inditex_data["bottom"]:
            ret += f"Lower-body clothing piece: {inditex_data['bottom']['name']}, price: {inditex_data['bottom']['price']}€, shop link: {inditex_data['bottom']['link']}"
        if ret == "":
            raise HTTPException(
                status_code=500, detail="Failed to fetch product details"
            )
        else:
            return ret
        """

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
