from pydantic import BaseModel

class ConversationRequest(BaseModel):
    uid: str
    time: str
    message: str