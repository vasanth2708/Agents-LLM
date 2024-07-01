import requests
import os

class GoogleBard:
    def __init__(self):
        self.api_key = "AIzaSyBHSOlL7Ic2fFQeE_JXnIyu2xsTlyZevOw"
        self.api_url = "https://api.bard.google.com/v1/generate"

    def generate(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": prompt,
            ""
            "max_tokens": 150
        }
        response = requests.post(self.api_url, headers=headers, json=data)
        print(response)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")