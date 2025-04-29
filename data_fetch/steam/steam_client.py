import requests
import time
import json
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime
from keys.STEAMAPIS import STEAMAPIS_KEY
from keys.STEAMWEB import STEAMWEB_KEY
from keys.STEAMLOGIN import STEAMLOGIN_KEY
import pickle
import random

# Adds the corresponding appid to each game
class Games(Enum):
    CS2 = 730
    RUST = 252490
    PUBG = 578080

# TODO: fix crazy rate limiter
class SteamClient:
    def __init__(self):
        self.base_url = "https://steamcommunity.com/market"
        self.cookie = { 'steamLoginSecure': STEAMLOGIN_KEY } # use your own cookie
        self.rate_limit = 0.5  # seconds between requests
        self.last_request = 0.0
    
    # Testing steam API
    def get_all_items(self, game: Games) -> List[str]:
        """
        Get all items for a game by making batched requests to Steam's market API.
        Uses smaller batch sizes and random delays to avoid rate limiting.
        
        Args:
            game: The game to get items for
            
        Returns:
            List of item hash names
        """
        all_item_names = []
        
        try:
            # Initial request to get total count
            self._rate_limit()
            all_items_get = requests.get(
                f'{self.base_url}/search/render/?search_descriptions=0&sort_column=default&sort_dir=desc&appid={game.value}&norender=1&count=100',
                cookies=self.cookie
            )
            all_items_get.raise_for_status()
            all_items = json.loads(all_items_get.content)
            
            if not all_items or 'total_count' not in all_items:
                print(f"Error: Invalid response from Steam API: {all_items}")
                return []
                
            total_items = all_items['total_count']
            print(f"Total items to fetch: {total_items}")

            # Fetch items in smaller batches of 50 to avoid missing items due to position changes
            for curr_pos in range(0, 1150, 50):
                self._rate_limit()  # This now uses random delay between 0.5-2.5 seconds
                
                all_items_get = requests.get(
                    f'{self.base_url}/search/render/?start={curr_pos}&count=100&search_descriptions=0&sort_column=default&sort_dir=desc&appid={game.value}&norender=1&count=5000',
                    cookies=self.cookie
                )
                print(f'Items {curr_pos} out of {total_items} code: {all_items_get.status_code}')
                
                all_items_get.raise_for_status()
                all_items = json.loads(all_items_get.content)
                
                if not all_items or 'results' not in all_items:
                    print(f"Error: Invalid response from Steam API for batch {curr_pos}: {all_items}")
                    continue
                    
                for item in all_items['results']:
                    all_item_names.append(item['hash_name'])
            
            # Remove duplicates that might occur due to position changes during fetching
            all_item_names = list(set(all_item_names))
            print(f"Total unique items found: {len(all_item_names)}")
            
            return all_item_names
            
        except requests.exceptions.RequestException as e:
            print(f"Error making request to Steam API: {str(e)}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error decoding Steam API response: {str(e)}")
            return []
        except Exception as e:
            print(f"Unexpected error in get_all_items: {str(e)}")
            return []

    def get_popular_items(self, game: Games) -> List[str]:
        """
        Get popular items for a game
        """
        self._rate_limit()
        endpoint = f"{self.base_url}/popular"
        # example request: GET https://steamcommunity.com/market/popular?country=NL&language=english&currency=3&norender=1&start=0&count=98
        params = {
            'country': 'NL',
            'language': 'english',
            'currency': '3',
            'norender': '1',
            'start': '0',
            'count': '98'
        }
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        print(data)
        return data['items']
        
    def get_price_overview(self, market_hash_name: str) -> Optional[Dict]:
        
        """
        Get price overview for a specific item
        example request: GET https://steamcommunity.com/market/priceoverview/?country=NL&currency=3&appid=578080&market_hash_name=Raglan%20T-shirt%20%28Red-White%29

        """
        self._rate_limit()
        endpoint = f"{self.base_url}/priceoverview"
        params = {
            'country': 'US',
            'currency': '1',
            'appid': '730', # hardcoded for now
            'market_hash_name': market_hash_name
        }
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        print(data)
        return data
    
    def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        time.sleep(random.uniform(0.5, 2.5))
        
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
            print('get_item_price')
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
            # TODO: getting a lot of these...
            print(f"Error fetching data from Steam: {str(e)}")
            return None
            
    def get_item_orders(self, market_hash_name: str) -> Optional[Dict]:
        """
        Get buy and sell orders for a specific item
        """
        self._rate_limit()

        print('get_item_orders')
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