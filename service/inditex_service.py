from repository.inditex_repository import InditexRepository
import requests

class InditexService():
    def __init__(self):
        self.repository = InditexRepository()
    def get_data(self,response_json):
        return self.repository.fetch_data(response_json)
