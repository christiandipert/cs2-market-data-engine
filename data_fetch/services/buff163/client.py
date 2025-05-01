import requests
import time
from typing import Dict, List, Optional
from datetime import datetime
from data_fetch.keys.BUFF163 import BUFF163_KEY

class Buff163Client:
    def __init__(self):
        self.api_key = BUFF163_KEY
        self.base_url = "https://buff.163.com/api"
        self.rate_limit = 1.0  # seconds between requests
        self.last_request = 0.0
        
    def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        now = time.time()
        if now - self.last_request < self.rate_limit:
            time.sleep(self.rate_limit - (now - self.last_request))
        self.last_request = time.time()
        
    def get_featured_market(self) -> List[Dict]:
        """Get featured items from the market"""
        self._rate_limit()
        endpoint = f"{self.base_url}/market/goods"
        params = {
            'game': 'csgo',
            'page_num': 1,
            'page_size': 20,
            'sort_by': 'price.desc',
            'use_suggestion': 0,
            '_': int(time.time() * 1000)
        }
        headers = {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': f'Device-Id={self.api_key}'
        }
        
        try:
            response = requests.get(endpoint, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') == 'OK':
                items = data.get('data', {}).get('items', [])
                return [{
                    'name': item.get('market_hash_name'),
                    'price': float(item.get('price', 0)),
                    'volume': int(item.get('volume', 0)),
                    'last_updated': datetime.now().isoformat()
                } for item in items]
            return []
        except Exception as e:
            print(f"Error fetching featured items from Buff163: {str(e)}")
            return [] 