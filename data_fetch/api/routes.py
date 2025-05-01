from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from data_fetch.core.market_fetcher import MarketFetcher
from data_fetch.core.storage import MarketStorage
from data_fetch.services.steam.client import Games

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

@app.get("/priceoverview")
async def get_price_overview(query: str):
    """
    Get price overview for a specific item. Uses steam client api
    """
    print("GOT REQUEST FOR " + query)
    return market_fetcher.steam_price_overview(query)

@app.get("/arbitrage")
async def get_arbitrage_opportunities():
    """Get current arbitrage opportunities"""
    # Will query engine/ c++ bindings for arb
    try:
        # placeholder
        return {"message": "Arbitrage opportunities endpoint"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 