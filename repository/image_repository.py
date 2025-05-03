from model.image_request import ImageRequest
from repository.inditex_repository import InditexRepository


class ImageRepository:
    def __init__(self):
        self.inditex_rep = InditexRepository()

    def handle_image(self, im: ImageRequest):
        return self.inditex_rep.visual_data(im.imageUrl)
