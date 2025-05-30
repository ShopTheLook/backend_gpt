from repository.mongodb_repository import MongoDBRepository
from model.data_request import ConversationRequest


class MongoDBService:
    def __init__(self):
        self.mongo_repository = MongoDBRepository()

    def add_message(self, data: ConversationRequest):
        self.mongo_repository.add_message(data.timestamp, data.uid, data.message)

    def get_messages(self, uid: str):
        return self.mongo_repository.get_messages(uid)

    def drop_messages(self, uid: str):
        self.mongo_repository.reset_messages(uid)

    pass
