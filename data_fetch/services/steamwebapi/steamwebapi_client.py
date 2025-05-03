import requests
from keys.STEAMWEBAPI import STEAMWEBAPI_KEY
from enum import Enum
from services.steam.client import Games
import json
import tkinter as tk

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

    def display_order_ladder_table(self, df_json):
        self.output_text.grid_remove()
        self.order_ladder_table.grid()
        for row in self.order_ladder_table.get_children():
            self.order_ladder_table.delete(row)
        try:
            df = json.loads(df_json)
            # If df is a string, parse again
            if isinstance(df, str):
                df = json.loads(df)
            columns = df.get('columns', [])
            data = df.get('data', [])
            for row in data:
                row = (row + [None]*6)[:6]
                self.order_ladder_table.insert('', tk.END, values=row)
        except Exception as e:
            self.display_result(f"Error displaying order ladder: {str(e)}")
