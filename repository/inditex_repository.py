from model.image_request import ImageRequest
import requests
import os


class InditexRepository:
    def __init__(self):
        self.url = os.getenv("INDITEX_API_BACKEND_URL")

    def fetch_data(self, response_json):
        response = requests.post(self.url + "/search", json=response_json)
        response.raise_for_status()
        return response.json()

    def visual_data(self, url):
        response = requests.post(self.url + "/search/visual", json={"url": url})
        response.raise_for_status()
        return response.json()
