from typing import Dict, List, Optional
from datetime import datetime

class MarketStorage:
    def __init__(self):
        self.cache: Dict[str, Dict] = {}
        self.history: Dict[str, List[Dict]] = {}

    def store_item_data(self, market_hash_name: str, data: Dict):
        """Store current item data"""
        self.cache[market_hash_name] = {
            **data,
            'last_updated': datetime.now().isoformat()
        }

    def get_item_data(self, market_hash_name: str) -> Optional[Dict]:
        """Get cached item data"""
        return self.cache.get(market_hash_name)

    def store_price_history(self, market_hash_name: str, price_data: Dict):
        """Store historical price data"""
        if market_hash_name not in self.history:
            self.history[market_hash_name] = []
        self.history[market_hash_name].append({
            **price_data,
            'timestamp': datetime.now().isoformat()
        })

    def get_price_history(self, market_hash_name: str, days: int = 30) -> List[Dict]:
        """Get price history for an item"""
        if market_hash_name not in self.history:
            return []
        
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        return [
            entry for entry in self.history[market_hash_name]
            if datetime.fromisoformat(entry['timestamp']).timestamp() > cutoff
        ] 