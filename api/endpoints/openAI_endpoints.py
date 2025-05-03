from fastapi import APIRouter, HTTPException
from model.data_request import ConversationRequest
from service.openAI_service import OpenAIService


router = APIRouter()

@router.post("/process")
async def process_conversation(data: ConversationRequest):
    service = OpenAIService()
    try:
        service.message_logic(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

