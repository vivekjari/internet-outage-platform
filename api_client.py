import requests
from config import CLOUDFLARE_API_TOKEN


class APIClient:

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }

    def get(self, url, params=None):
        response = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        return response.json()