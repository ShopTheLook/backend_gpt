from pydantic import BaseModel

class ConversationRequest(BaseModel):
    uid: str
    timestamp: int 
    message: str
