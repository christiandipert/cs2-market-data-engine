from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from core.market_fetcher import MarketFetcher
from core.storage import MarketStorage
from services.steam.client import Games
from services.steam_experimental.steam_experimental_client import SteamExperimentalClient
from fastapi.responses import JSONResponse
import json

app = FastAPI(
    title="CS2 Market Data API",
    description="API for fetching and analyzing CS2 market data",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
market_fetcher = MarketFetcher()
storage = MarketStorage()

@app.get("/")
async def root():
    return {"message": "CS2 Market Data API"}

@app.get("/buff/sell_orders/{item_id}")
async def get_buff_sell_orders(query: str):
    """
    Get sell orders for an item from buff
    """
    try:
        item_id = int(query)
        return market_fetcher.get_buff_163_sell_orders(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID")

@app.get("/buff/item/{item}")
async def get_buff_item_price(query: str):
    """
    Get the price of an item from buff
    """
    try:
        item = int(query)
        return market_fetcher.get_buff_163_item_price(item)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID")

@app.get("/buff/featured")
async def get_buff_featured_items():
    """
    Get featured items for a game. Uses buff163api. Works
    """
    return market_fetcher.get_buff_163_featured()

@app.get("/items")
async def get_all_items():
    """
    Get all items for a game. Uses steam client api
    """
    return market_fetcher.get_all_items(Games.CS2)

# Uses steammarket wrapper
@app.get("/priceoverview/{market_hash_name}")
async def get_price_overview(query: str):
    """
    Get price overview for a specific item. Uses steam client api
    """
    return market_fetcher.steam_price_overview(query)

@app.get("/orderladder/{market_hash_name}")
async def get_order_ladder(market_hash_name: str):
    """
    Get order ladder for a specific item. Uses steam experimental client api
    """
    df = market_fetcher.get_steam_order_ladder(market_hash_name, levels=40)
    return JSONResponse(content=json.loads(df.to_json(orient='split')))

@app.get("/arbitrage")
async def get_arbitrage_opportunities():
    """Get current arbitrage opportunities"""
    # Will query engine/ c++ bindings for arb
    try:
        # placeholder
        return {"message": "Arbitrage opportunities endpoint"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 