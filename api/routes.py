from fastapi import APIRouter
from api.endpoints import openAI_endpoints

router = APIRouter()

router.include_router(openAI_endpoints.router, prefix="/api/v1")
