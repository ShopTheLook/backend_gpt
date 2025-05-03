from model.data_request import ConversationRequest
from repository.openAI_repository import OpenAIRepository

class OpenAIService():
    def __init__(self):
        self.repository = OpenAIRepository()
    def message_logic(self, data: ConversationRequest):
        # TODO: error check time
        return self.repository.handle_message(data)