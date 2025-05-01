import requests
from keys.STEAMWEBAPI import STEAMWEBAPI_KEY
from enum import Enum
from services.steam.client import Games

class SteamWebAPIClient:
        
    def __init__(self):
        self.base_url = "https://steamwebapi.com/steam/api"
        self.key = STEAMWEBAPI_KEY

    def get_item(self, item_id: str, game: Games):
        endpoint = f"{self.base_url}/item"
        params = {
            "key": self.key,
            "market_hash_name": item_id,
            "game": "csgo" if game == Games.CS2 else game.value
        }
        response = requests.get(endpoint, params=params)
        print(response.json())
        return response.json()
