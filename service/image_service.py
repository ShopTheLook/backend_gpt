from model.image_request import ImageRequest
from repository.image_repository import ImageRepository


class ImageService:
    def __init__(self):
        self.image_repo = ImageRepository()

    def image_logic(self, im: ImageRequest):
        return self.image_repo.handle_image(im)

    pass
