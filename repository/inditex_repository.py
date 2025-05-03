import requests
import os

class InditexRepository():
    def __init__(self):
        self.url = os.getenv("INDITEX_API_BACKEND_URL")
    def fetch_data(self, response_json):
        response = requests.post(self.url, json=response_json)
        response.raise_for_status()
        return response.json()
        
