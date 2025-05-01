from buff163_unofficial_api import Buff163API # pyright: ignore
from keys.BUFF163 import BUFF163_KEY
from currency_converter import CurrencyConverter # pyright: ignore

class Buff163Client:
    def __init__(self):
        self.converter = CurrencyConverter()
        try:
            self.api = Buff163API(session_cookie=BUFF163_KEY)
        except Exception as e:
            print(f"Failed to initialize Buff163Client: {e}")
        print("Buff163Client initialized")

    def __convert(self, cny: int) -> float:
        return round(self.converter.convert(cny, 'CNY', 'USD'), 2)

    # Works well
    def get_featured_market(self):
        """
        Fetches the featured market data from Buff163 API and converts the prices to USD.

        Returns:
            dict: A dictionary containing the item IDs as keys and their prices in USD as values.
        """
        featured = self.api.get_featured_market()
        prices = {}
        for item in featured:
            # prices[item['id']] = self.converter.convert(item['price'], 'CNY', 'USD')
            # item attributes
            """
                    buy_max_price: str,
                    buy_num: int,
                    can_bargain: bool,
                    goods_info: Union[GoodsInfo, dict],
                    id: int,
                    market_hash_name: str,
                    market_min_price: int,
                    name: str,
                    quick_price: str,
                    sell_min_price: str,
                    sell_num: int,
                    sell_reference_price: str,
                    short_name: str,
                    steam_market_url: str,
                    transacted_num: int,
                    data: bytes = bytes(),
            """
            print(f"""
                ITEM: {item.name} (ID: {item.id})
                MAX BID: {self.__convert(item.buy_max_price)} x{item.buy_num}
                LOWEST ASK: {self.__convert(item.sell_min_price)} x{item.sell_num}
            """)
        return prices
