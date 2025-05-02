import requests
import time
from typing import Dict, List, Optional
from datetime import datetime
from keys.BUFF163 import BUFF163_KEY
from buff163_unofficial_api import Buff163API
from currency_converter import CurrencyConverter

BASE_URL = 'https://buff.163.com/api/market'

class Buff163Wrapper:
    def __init__(self):
        self.buff_client = Buff163API(session_cookie=BUFF163_KEY)
        self._rate_limit = 1.0  # seconds between requests
        self._last_request = 0.0

        self.__converter = CurrencyConverter()

    def __convert_price(self, cny_price: int) -> float:
        return round(self.__converter.convert(cny_price, 'CNY', 'USD'), 2)
        
    def __rate_limit(self) -> None:
        """Ensure we don't exceed rate limits"""
        now = time.time()
        if now - self._last_request < self._rate_limit:
            time.sleep(self._rate_limit - (now - self._last_request))
        self._last_request = time.time()
        
    # Gets the current featured market items from buff
    def get_featured_market(self) -> List[Dict]:
        """Get featured items from the market"""
        self.__rate_limit()
        market_items = self.buff_client.get_featured_market()
        returned = {}
        for item in market_items:
            returned[item.name] = {
                "id": item.id,
                "currency": "USD",
                "timestamp": datetime.now().isoformat(),
                "buy_max_price": self.__convert_price(item.buy_max_price),
                "buy_num": item.buy_num,
                "sell_min_price": self.__convert_price(item.sell_min_price),
                "sell_num": item.sell_num
            }
        return returned
    
    # Gets the price of an item from buff
    def get_item_price(self, item_id: int) -> float:
        self.__rate_limit()
        item = self.buff_client.get_item(900565)
        print(item.market_hash_name)
        return item
    
    def get_sell_orders(self, item_id: int) -> List[Dict]:
        self.__rate_limit()

        endpoint = f'{BASE_URL}/goods/sell_order'
        params = {
            'game': 'csgo',
            'goods_id': item_id,
            'page_num': 1,
            'sort_by': 'price.desc',
            'allow_tradable_cooldown': 1,
            '_': int(time.time() * 1000)
        }
        headers = {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': f'Device-Id={BUFF163_KEY}'
        }
        response = requests.get(endpoint, params=params, headers=headers)
        for item in response.json()['data']['items']:
            print(item)
        return response.json()
