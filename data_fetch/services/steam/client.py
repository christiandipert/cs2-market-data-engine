import requests
import time
import json
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime
from data_fetch.keys.STEAMAPIS import STEAMAPIS_KEY
from data_fetch.keys.STEAMWEB import STEAMWEB_KEY
from data_fetch.keys.STEAMLOGIN import STEAMLOGIN_KEY
import pickle

class Games(Enum):
    CS2 = 730
    RUST = 252490
    PUBG = 578080

class SteamClient:
    def __init__(self):
        self.api_key = STEAMAPIS_KEY
        self.web_key = STEAMWEB_KEY
        self.login_key = STEAMLOGIN_KEY
        self.base_url = "https://api.steamapis.com"
        self.rate_limit = 1.0  # seconds between requests
        self.last_request = 0.0
        
    def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        now = time.time()
        if now - self.last_request < self.rate_limit:
            time.sleep(self.rate_limit - (now - self.last_request))
        self.last_request = time.time()
        
    def get_all_items(self, game: Games) -> List[str]:
        """Get all items for a game"""
        self._rate_limit()
        endpoint = f"{self.base_url}/market/items/{game.value}"
        params = {'api_key': self.api_key}
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                return [item['market_hash_name'] for item in data.get('data', [])]
            return []
        except Exception as e:
            print(f"Error fetching items from Steam: {str(e)}")
            return []
            
    def get_popular_items(self, game: Games) -> List[str]:
        """Get popular items for a game"""
        self._rate_limit()
        endpoint = f"{self.base_url}/market/items/{game.value}/popular"
        params = {'api_key': self.api_key}
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                return [item['market_hash_name'] for item in data.get('data', [])]
            return []
        except Exception as e:
            print(f"Error fetching popular items from Steam: {str(e)}")
            return []
            
    def get_price_overview(self, market_hash_name: str) -> Optional[Dict]:
        """Get price overview for a specific item"""
        self._rate_limit()
        endpoint = f"{self.base_url}/market/priceoverview"
        params = {
            'api_key': self.api_key,
            'market_hash_name': market_hash_name,
            'appid': 730  # CS2
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                return {
                    'lowest_price': float(data.get('lowest_price', 0)),
                    'volume': int(data.get('volume', 0)),
                    'median_price': float(data.get('median_price', 0)),
                    'last_updated': datetime.now().isoformat()
                }
            return None
        except Exception as e:
            print(f"Error fetching price overview from Steam: {str(e)}")
            return None
            
    def get_item_price(self, market_hash_name: str) -> Optional[Dict]:
        """Get current price data for an item"""
        self._rate_limit()
        endpoint = f"{self.base_url}/market/item/{market_hash_name}"
        params = {'api_key': self.api_key}
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                item = data.get('data', {})
                return {
                    'lowest_price': float(item.get('lowest_price', 0)),
                    'highest_price': float(item.get('highest_price', 0)),
                    'volume': int(item.get('volume', 0)),
                    'last_updated': datetime.now().isoformat()
                }
            return None
        except Exception as e:
            print(f"Error fetching item price from Steam: {str(e)}")
            return None
            
    def get_item_orders(self, market_hash_name: str) -> Optional[Dict]:
        """Get buy and sell orders for an item"""
        self._rate_limit()
        endpoint = f"{self.base_url}/market/item/{market_hash_name}/orders"
        params = {'api_key': self.api_key}
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                orders = data.get('data', {})
                return {
                    'buy_orders': orders.get('buy_orders', []),
                    'sell_orders': orders.get('sell_orders', []),
                    'last_updated': datetime.now().isoformat()
                }
            return None
        except Exception as e:
            print(f"Error fetching item orders from Steam: {str(e)}")
            return None 