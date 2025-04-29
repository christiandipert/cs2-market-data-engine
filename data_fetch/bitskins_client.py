import requests
import os
import time
import hmac
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from keys.BITSKINS_KEYS import BITSKINS_API_KEY

class BitskinsClient:
    def __init__(self):
        self.api_key = os.getenv('BITSKINS_API_KEY')
        self.secret = os.getenv('BITSKINS_SECRET')
        self.base_url = "https://bitskins.com/api/v1"
        self.rate_limit = 1.0  # seconds between requests
        self.last_request = 0.0
        
    def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        now = time.time()
        if now - self.last_request < self.rate_limit:
            time.sleep(self.rate_limit - (now - self.last_request))
        self.last_request = time.time()
        
    def _generate_signature(self, nonce: int) -> str:
        """Generate HMAC signature for API authentication"""
        message = f"{self.api_key}{nonce}"
        return hmac.new(
            self.secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
    def get_item_price(self, market_hash_name: str) -> Optional[Dict]:
        """
        Get the current bid and ask prices for a specific item
        """
        self._rate_limit()
        nonce = int(time.time())
        signature = self._generate_signature(nonce)
        
        endpoint = f"{self.base_url}/get_price_data_for_items_on_sale"
        params = {
            'app_id': '730',  # CS2 app ID
            'market_hash_name': market_hash_name,
            'code': nonce,
            'api_key': self.api_key,
            'signature': signature
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                items = data.get('data', {}).get('items', [])
                if items:
                    item = items[0]  # Get the first item
                    return {
                        'name': market_hash_name,
                        'lowest_price': float(item.get('lowest_price', 0)),
                        'highest_price': float(item.get('highest_price', 0)),
                        'volume': int(item.get('total_items', 0)),
                        'last_updated': datetime.now().isoformat()
                    }
            return None
        except Exception as e:
            print(f"Error fetching data from Bitskins: {str(e)}")
            return None

    def get_market_trends(self, market_hash_names: List[str]) -> Dict:
        """
        Get market trends for multiple items
        """
        trends = {
            'rising': [],
            'falling': [],
            'stable': []
        }
        
        for name in market_hash_names:
            item_data = self.get_item_price(name)
            if item_data:
                # Simple trend analysis based on price spread
                spread = item_data['highest_price'] - item_data['lowest_price']
                if spread > 0.1:  # Arbitrary threshold
                    trends['rising'].append(name)
                elif spread < -0.1:
                    trends['falling'].append(name)
                else:
                    trends['stable'].append(name)
        
        return trends 