from pymongo import MongoClient, ASCENDING
from datetime import datetime
import os


class MongoDBRepository:
    def __init__(self) -> None:
        mongo_url = os.getenv("MONGODB_URL")
        self.mongo_client = MongoClient(mongo_url)

    def add_message(self, time, uid: str, msg: str):
        db = self.mongo_client["u_msg"]
        usr_collection = db[uid]
        usr_collection.insert_one(
            {
                "msg": msg,
                "time": datetime.now(),
            }
        )

    def get_messages(self, uid: str):
        db = self.mongo_client["u_msg"]
        usr_collection = db[uid]
        return usr_collection.find().sort("time", ASCENDING)

    pass
