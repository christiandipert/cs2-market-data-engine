import requests
import time
from typing import Dict, List, Optional
from datetime import datetime

# TODO: fix
class SteamClient:
    def __init__(self):
        self.base_url = "https://steamcommunity.com/market"
        self.rate_limit = 0.5  # seconds between requests
        self.last_request = 0.0
        
    def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        now = time.time()
        if now - self.last_request < self.rate_limit:
            time.sleep(self.rate_limit - (now - self.last_request))
        self.last_request = time.time()
        
    def get_item_price(self, market_hash_name: str) -> Optional[Dict]:
        """
        Get price overview for a specific item
        """
        self._rate_limit()
        endpoint = f"{self.base_url}/priceoverview"
        params = {
            'appid': '730',  # CS2 app ID
            'market_hash_name': market_hash_name,
            'currency': '1'  # USD
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                return {
                    'name': market_hash_name,
                    'lowest_price': float(data['lowest_price'].replace('$', '')),
                    'median_price': float(data['median_price'].replace('$', '')),
                    'volume': int(data['volume'].replace(',', '')),
                    'last_updated': datetime.now().isoformat()
                }
            return None
        except Exception as e:
            print(f"Error fetching data from Steam: {str(e)}")
            return None
            
    def get_item_orders(self, market_hash_name: str) -> Optional[Dict]:
        """
        Get buy and sell orders for a specific item
        """
        self._rate_limit()
        # First get the item_nameid
        listing_url = f"{self.base_url}/listings/730/{market_hash_name}"
        try:
            response = requests.get(listing_url)
            response.raise_for_status()
            # Extract item_nameid from the page
            # This is a simplified version - in practice you'd need to parse the HTML
            # or use a more reliable method to get the item_nameid
            item_nameid = "123456"  # Placeholder - implement actual extraction
            
            # Now get the order book
            endpoint = f"{self.base_url}/itemordershistogram"
            params = {
                'country': 'US',
                'language': 'english',
                'currency': '1',
                'item_nameid': item_nameid,
                'two_factor': '0'
            }
            
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('success'):
                return {
                    'highest_buy_order': float(data.get('highest_buy_order', 0)),
                    'lowest_sell_order': float(data.get('lowest_sell_order', 0)),
                    'buy_orders': data.get('buy_order_graph', []),
                    'sell_orders': data.get('sell_order_graph', [])
                }
            return None
        except Exception as e:
            print(f"Error fetching order data from Steam: {str(e)}")
            return None 