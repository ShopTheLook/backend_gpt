from fastapi import APIRouter, HTTPException
from model.data_request import ConversationRequest
from model.image_request import ImageRequest
from service.openAI_service import OpenAIService
from service.image_service import ImageService


router = APIRouter()


@router.post("/process")
async def process_conversation(data: ConversationRequest | ImageRequest):
    # try:
    if isinstance(data, ConversationRequest):
        service = OpenAIService()
        return service.message_logic(data)
    else:
        service = ImageService()
        return service.image_logic(data)


# except Exception as e:
# raise HTTPException(status_code=500, detail=str(e))
