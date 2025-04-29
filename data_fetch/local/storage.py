import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# TODO: use redis instead of this defunct solution
class MarketStorage:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.cache_duration = timedelta(hours=1)  # Cache data for 1 hour
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
    def _get_cache_path(self, market_hash_name: str) -> str:
        """Get the cache file path for an item"""
        return os.path.join(self.cache_dir, f"{market_hash_name}.json")
        
    def _is_cache_valid(self, cache_path: str) -> bool:
        """Check if cache is still valid"""
        if not os.path.exists(cache_path):
            return False
            
        with open(cache_path, 'r') as f:
            data = json.load(f)
            cache_time = datetime.fromisoformat(data['last_updated'])
            return datetime.now() - cache_time < self.cache_duration
            
    def get_cached_data(self, market_hash_name: str) -> Optional[Dict]:
        """Get cached data for an item if it exists and is valid"""
        cache_path = self._get_cache_path(market_hash_name)
        
        if not self._is_cache_valid(cache_path):
            return None
            
        with open(cache_path, 'r') as f:
            return json.load(f)
            
    def cache_data(self, market_hash_name: str, data: Dict) -> None:
        """Cache market data for an item"""
        cache_path = self._get_cache_path(market_hash_name)
        
        with open(cache_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    def get_historical_data(self, market_hash_name: str, days: int = 30) -> List[Dict]:
        """Get historical price data for an item"""
        historical_data = []
        cache_path = self._get_cache_path(market_hash_name)
        
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                data = json.load(f)
                if 'history' in data:
                    cutoff_date = datetime.now() - timedelta(days=days)
                    historical_data = [
                        point for point in data['history']
                        if datetime.fromisoformat(point['timestamp']) > cutoff_date
                    ]
                    
        return historical_data
        
    def update_historical_data(self, market_hash_name: str, current_data: Dict) -> None:
        """Update historical data with current market data"""
        cache_path = self._get_cache_path(market_hash_name)
        historical_data = []
        
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                data = json.load(f)
                if 'history' in data:
                    historical_data = data['history']
                    
        # Add current data point to history
        historical_data.append({
            'timestamp': current_data['last_updated'],
            'steam_price': current_data['steam']['lowest_price'] if current_data['steam'] else None,
            'bitskins_price': current_data['bitskins']['lowest_price'] if current_data['bitskins'] else None
        })
        
        # Update cache with new history
        current_data['history'] = historical_data
        self.cache_data(market_hash_name, current_data) 