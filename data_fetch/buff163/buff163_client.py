from buff163_unofficial_api import Buff163API
from keys.BUFF163 import BUFF163_KEY

class Buff163Client:
    def __init__(self):
        self.api = Buff163API(session_cookie=BUFF163_KEY)
        print("Buff163Client initialized with " + BUFF163_KEY)

    def get_item_info(self, item_id):
        return self.api.get_item_info(item_id)

    def get_item(self, item_id):
        out = self.api.get_item(900565)
        print(out.sell_min_price)
        print(out.buy_max_price)
        return out.sell_min_price
