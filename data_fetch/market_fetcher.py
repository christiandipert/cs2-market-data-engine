from typing import Dict, List, Optional
from steam_client import SteamClient
from bitskins_client import BitskinsClient

class MarketFetcher:
    def __init__(self):
        self.steam_client = SteamClient()
        self.bitskins_client = BitskinsClient()
        
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