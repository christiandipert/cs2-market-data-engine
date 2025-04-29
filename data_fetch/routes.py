from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from market_fetcher import MarketFetcher
from local.storage import MarketStorage

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

@app.get("/items/{market_hash_name}")
async def get_item_data(market_hash_name: str):
    """
    Get current market data for a specific item
    """
    try:
        # Check cache first
        cached_data = storage.get_cached_data(market_hash_name)
        if cached_data:
            return cached_data
            
        # Fetch fresh data if not in cache
        data = market_fetcher.get_market_data(market_hash_name)
        if not data:
            raise HTTPException(status_code=404, detail="Item not found")
            
        # Cache the data
        storage.cache_data(market_hash_name, data)
        storage.update_historical_data(market_hash_name, data)
        
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/items/{market_hash_name}/history")
async def get_item_history(market_hash_name: str, days: int = 30):
    """
    Get historical price data for an item
    """
    try:
        history = storage.get_historical_data(market_hash_name, days)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/arbitrage")
async def get_arbitrage_opportunities():
    """Get current arbitrage opportunities"""
    # Will query engine/ c++ bindings for arb
    try:
        # placeholder
        return {"message": "Arbitrage opportunities endpoint"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 