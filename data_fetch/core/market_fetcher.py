from typing import Dict, List, Optional
from datetime import datetime
from services.steam.client import SteamClient, Games
from services.bitskins.client import BitskinsClient
from services.buff163.buff163_client import Buff163Wrapper
import pandas as pd
from services.steam_experimental.steam_experimental_client import SteamExperimentalClient
import tkinter as tk

class MarketFetcher:
    def __init__(self):
        self.steam_client = SteamClient()
        self.bitskins_client = BitskinsClient()
        self.buff163_client = Buff163Wrapper()
        self.steam_experimental_client = SteamExperimentalClient()

    # Gets the current featured market items from buff
    def get_buff_163_featured(self):
        return self.buff163_client.get_featured_market()
    
    def get_buff_163_sell_orders(self, item_id: int) -> List[Dict]:
        return self.buff163_client.get_sell_orders(item_id)
    
    # Gets the price of an item from buff
    def get_buff_163_item_price(self, item_id: int) -> float:
        return self.buff163_client.get_item_price(item_id)

    # Steam market data
    def get_market_data(self, market_hash_name: str) -> Optional[Dict]:
        """
        Get combined market data from both Steam and Bitskins
        """
        steam_data = self.steam_client.get_item_price(market_hash_name)
        bitskins_data = self.bitskins_client.get_item_price(market_hash_name)

        if not steam_data and not bitskins_data:
            return None

        return {
            'name': market_hash_name,
            'steam': steam_data,
            'bitskins': bitskins_data,
            'last_updated': datetime.now().isoformat()
        }

    def steam_popular_items(self, game: Games) -> List[str]:
        """
        Get popular items for a game
        """
        return self.steam_client.get_popular_items(game)

    def get_steam_order_ladder(self, market_hash_name: str, levels: int = 30, refresh_interval: int = 20) -> pd.DataFrame:
        df = self.steam_experimental_client.get_order_ladder(market_hash_name, refresh_interval)
        # If the DataFrame has both bids and asks, filter to top N levels for each
        if hasattr(df, 'head'):
            return df.head(levels)
        return df

    def steam_price_overview(self, market_hash_name: str) -> Optional[Dict]:
        """
        Get price overview for a specific item
        """
        return self.steam_client.get_price_overview(market_hash_name)

    def get_all_items(self, game: Games) -> List[str]:
        """
        Get all items for a game
        """
        result = self.steam_client.get_all_items(game)
        print(result)
        return result

    def get_arbitrage_opportunities(self, market_hash_names: List[str]) -> List[Dict]:
        """
        Find arbitrage opportunities between Steam and Bitskins
        """
        opportunities = []

        for name in market_hash_names:
            data = self.get_market_data(name)
            if not data:
                continue

            steam_price = data['steam']['lowest_price'] if data['steam'] else None
            bitskins_price = data['bitskins']['lowest_price'] if data['bitskins'] else None

            if steam_price and bitskins_price:
                # Calculate potential profit after fees
                steam_fee = 0.15  # 15% Steam fee
                bitskins_fee = 0.05  # 5% Bitskins fee

                # Steam to Bitskins arbitrage
                steam_to_bitskins_profit = bitskins_price * (1 - bitskins_fee) - steam_price

                # Bitskins to Steam arbitrage
                bitskins_to_steam_profit = steam_price * (1 - steam_fee) - bitskins_price

                if steam_to_bitskins_profit > 0 or bitskins_to_steam_profit > 0:
                    opportunities.append({
                        'name': name,
                        'steam_price': steam_price,
                        'bitskins_price': bitskins_price,
                        'steam_to_bitskins_profit': steam_to_bitskins_profit,
                        'bitskins_to_steam_profit': bitskins_to_steam_profit,
                        'last_updated': data['last_updated']
                    })

        # Sort by highest potential profit
        opportunities.sort(key=lambda x: max(x['steam_to_bitskins_profit'], x['bitskins_to_steam_profit']), reverse=True)
        return opportunities 