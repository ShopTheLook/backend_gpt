from pydantic import BaseModel


class ImageRequest(BaseModel):
    uid: str
    timestamp: int
    imageUrl: str
