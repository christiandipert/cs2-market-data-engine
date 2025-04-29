# redis client goes here. Should interface all steam/bitskins requests with redis

import redis
from typing import Dict, Optional

class RedisClient:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)

    def get_item_price(self, market_hash_name: str) -> Optional[Dict]:
        # TODO: implement
        pass

    def get_item_orders(self, market_hash_name: str) -> Optional[Dict]:
        # TODO: implement
        pass
