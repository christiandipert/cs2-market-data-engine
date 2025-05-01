import requests
from keys.STEAMAPIS import STEAMAPIS_KEY
from services.steam.client import Games

class SteamAPIsClient:
    def __init__(self):
        self.base_url = "https://api.steamapis.com"
        self.key = STEAMAPIS_KEY

    def get_all_items(self, game: Games):
        endpoint = f"{self.base_url}/market/items/{game.value}"
        params = {
            "api_key": self.key
        }
        response = requests.get(endpoint, params=params)
        print("GOT RESPONSE: " + str(response.json()))
        return response.json()

