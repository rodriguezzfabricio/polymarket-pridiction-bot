"""
Market API Routes - Endpoints to fetch Polymarket data.

These routes let us test our PolymarketClient and will eventually
be used by our trading bot's dashboard (if we build one).

HOW FASTAPI ROUTES WORK:
------------------------
1. We create a "router" - a collection of related endpoints
2. We decorate functions with @router.get("/path") or @router.post("/path")
3. The function runs when someone hits that endpoint
4. Whatever we return gets sent back as JSON

DEPENDENCY INJECTION:
--------------------
Notice we use `async with PolymarketClient()` inside each route.
In production, you might want to share one client across requests.
For MVP, creating a new client each time is simpler and safer.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from src.core.config import get_settings
from src.models.market import Market, Trade
from src.services.polymarket_client import PolymarketClient, PolymarketClientError

logger = logging.getLogger(__name__)

# Create a router for market-related endpoints
# The prefix means all routes here will start with /markets
router = APIRouter(
    prefix="/markets",
    tags=["markets"],  # Groups these in the auto-generated docs
)


@router.get("", response_model=list[Market])
async def get_markets(
    limit: Annotated[int, Query(ge=1, le=500, description="Max markets to return")] = 50,
    active: Annotated[bool, Query(description="Only return active markets")] = True,
) -> list[Market]:
    """
    Fetch available markets from Polymarket.

    This is useful for:
    - Browsing what markets exist
    - Finding markets to analyze
    - Getting market IDs for trade queries

    Example response:
    ```json
    [
        {
            "id": "12345",
            "question": "Will Bitcoin hit $100k by 2025?",
            "outcomes": ["Yes", "No"],
            "outcome_prices": [0.65, 0.35],
            "volume": 1500000.0
        }
    ]
    ```
    """
    logger.info(f"GET /markets called (limit={limit}, active={active})")

    try:
        async with PolymarketClient() as client:
            markets = await client.get_markets(limit=limit, active=active)
            return markets
    except PolymarketClientError as e:
        logger.error(f"Failed to fetch markets: {e}")
        raise HTTPException(status_code=502, detail=f"Polymarket API error: {e}")


@router.get("/{market_id}", response_model=Market)
async def get_market(market_id: str) -> Market:
    """
    Fetch a single market by its ID.

    Use this when you know which market you want details about.
    """
    logger.info(f"GET /markets/{market_id} called")

    try:
        async with PolymarketClient() as client:
            market = await client.get_market(market_id)
            if not market:
                raise HTTPException(status_code=404, detail="Market not found")
            return market
    except PolymarketClientError as e:
        logger.error(f"Failed to fetch market {market_id}: {e}")
        raise HTTPException(status_code=502, detail=f"Polymarket API error: {e}")


@router.get("/{market_id}/trades", response_model=list[Trade])
async def get_market_trades(
    market_id: str,
    limit: Annotated[int, Query(ge=1, le=500, description="Max trades to return")] = 100,
) -> list[Trade]:
    """
    Fetch recent trades for a specific market.

    This shows who's buying/selling and for how much.
    Look for big trades (size > $500) - those are potential whale signals!

    NOTE: Requires POLYGON_WALLET_PRIVATE_KEY in .env
    """
    logger.info(f"GET /markets/{market_id}/trades called (limit={limit})")

    settings = get_settings()

    try:
        async with PolymarketClient(
            private_key=settings.POLYGON_WALLET_PRIVATE_KEY or None
        ) as client:
            trades = await client.get_market_trades(market_id, limit=limit)
            return trades
    except PolymarketClientError as e:
        logger.error(f"Failed to fetch trades for {market_id}: {e}")
        raise HTTPException(status_code=502, detail=f"Polymarket API error: {e}")


# Separate router for trades across all markets
trades_router = APIRouter(
    prefix="/trades",
    tags=["trades"],
)


@trades_router.get("", response_model=list[Trade])
async def get_recent_trades(
    limit: Annotated[int, Query(ge=1, le=500, description="Max trades to return")] = 100,
    min_size: Annotated[
        float, Query(ge=0, description="Minimum trade size in USD")
    ] = 0.0,
) -> list[Trade]:
    """
    Fetch recent trades across ALL markets.

    This is the key endpoint for whale watching!

    Set min_size=500 to only see potential whale trades.

    Example:
        GET /trades?limit=50&min_size=500

    This returns the 50 most recent trades where someone spent $500+.

    NOTE: Requires POLYGON_WALLET_PRIVATE_KEY in .env
    """
    logger.info(f"GET /trades called (limit={limit}, min_size={min_size})")

    settings = get_settings()

    try:
        async with PolymarketClient(
            private_key=settings.POLYGON_WALLET_PRIVATE_KEY or None
        ) as client:
            trades = await client.get_recent_trades(limit=limit)

            # Filter by minimum size if specified
            if min_size > 0:
                trades = [t for t in trades if t.size >= min_size]
                logger.info(f"Filtered to {len(trades)} trades >= ${min_size}")

            return trades
    except PolymarketClientError as e:
        logger.error(f"Failed to fetch trades: {e}")
        raise HTTPException(status_code=502, detail=f"Polymarket API error: {e}")


@trades_router.get("/whales", response_model=list[Trade])
async def get_whale_trades(
    limit: Annotated[int, Query(ge=1, le=500, description="Max trades to check")] = 200,
    threshold: Annotated[
        float, Query(ge=100, description="Whale threshold in USD")
    ] = 500.0,
) -> list[Trade]:
    """
    Get trades that qualify as "whale" trades.

    This is a convenience endpoint that filters for big trades.
    Default threshold is $500 (our MVP whale definition).

    These are the trades we'll eventually send to the AI swarm for analysis!

    NOTE: Requires POLYGON_WALLET_PRIVATE_KEY in .env
    """
    logger.info(f"GET /trades/whales called (limit={limit}, threshold={threshold})")

    settings = get_settings()

    try:
        async with PolymarketClient(
            private_key=settings.POLYGON_WALLET_PRIVATE_KEY or None
        ) as client:
            # Fetch more trades than requested since we'll filter
            trades = await client.get_recent_trades(limit=limit)

            # Filter for whale trades
            whale_trades = [t for t in trades if t.size >= threshold]

            logger.info(
                f"Found {len(whale_trades)} whale trades (>= ${threshold}) "
                f"out of {len(trades)} total"
            )

            return whale_trades
    except PolymarketClientError as e:
        logger.error(f"Failed to fetch whale trades: {e}")
        raise HTTPException(status_code=502, detail=f"Polymarket API error: {e}")
