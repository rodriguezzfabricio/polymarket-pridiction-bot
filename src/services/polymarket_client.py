"""
Polymarket API Client - Unified interface for market and trade data.

This is our "eyes" - we use this to see what's happening on Polymarket.
Without this, we're trading blind.

HOW THIS WORKS:
---------------
1. Gamma API (gamma-api.polymarket.com) - Public market data (prices, volume)
2. CLOB API (clob.polymarket.com) - Trade data via py-clob-client library

WHY TWO APIs?
-------------
- Gamma API: No auth needed, gives us market info
- CLOB API: Needs wallet auth, gives us trade data (for whale watching)

USAGE:
------
    # Without private key - markets only
    async with PolymarketClient() as client:
        markets = await client.get_markets()

    # With private key - markets AND trades
    async with PolymarketClient(private_key="0x...") as client:
        markets = await client.get_markets()
        trades = await client.get_recent_trades()  # Now works!
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any

import httpx

from src.models.market import Market, Trade, TradeSide

# CLOB client import - optional, only used if private_key provided
try:
    from py_clob_client.client import ClobClient
    CLOB_AVAILABLE = True
except ImportError:
    CLOB_AVAILABLE = False
    ClobClient = None  # type: ignore

# Set up logging - this is how we keep track of what's happening
logger = logging.getLogger(__name__)

# Polymarket's public API endpoints
GAMMA_API_BASE_URL = "https://gamma-api.polymarket.com"
DATA_API_BASE_URL = "https://data-api.polymarket.com"  # Public trade data for whale watching


class PolymarketClientError(Exception):
    """Custom exception for Polymarket API errors."""

    pass


class PolymarketClient:
    """
    Async client for the Polymarket Gamma API.

    This class handles all communication with Polymarket. It:
    - Makes HTTP requests
    - Handles errors gracefully
    - Converts raw JSON into our Python objects

    PATTERN: "Context Manager"
    --------------------------
    We use `async with` to ensure connections are properly closed:

        async with PolymarketClient() as client:
            data = await client.get_markets()

    This is better than manually calling .close() because it works
    even if an error happens.
    """

    def __init__(
        self,
        base_url: str = GAMMA_API_BASE_URL,
        timeout: float = 30.0,
        private_key: str | None = None,
    ):
        """
        Initialize the Polymarket client.

        Args:
            base_url: The API base URL (default: Gamma API)
            timeout: How long to wait for responses (seconds)
            private_key: Your Polygon wallet private key (enables trade data)
        """
        self.base_url = base_url
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

        # CLOB client for trade data (only if private key provided)
        self._clob_client: ClobClient | None = None
        self._executor = ThreadPoolExecutor(max_workers=2)

        if private_key:
            if not CLOB_AVAILABLE:
                logger.warning(
                    "py-clob-client not installed. Run: pip install py-clob-client"
                )
            else:
                self._init_clob_client(private_key)

    def _init_clob_client(self, private_key: str) -> None:
        """
        Initialize the CLOB client with authentication.

        This sets up the py-clob-client library which handles all the
        complex authentication (EIP-712 signing, API credentials, etc.)
        """
        try:
            # Normalize private key (add 0x if missing)
            if not private_key.startswith("0x"):
                private_key = f"0x{private_key}"

            self._clob_client = ClobClient(
                host="https://clob.polymarket.com",
                key=private_key,
                chain_id=137,  # Polygon mainnet
            )

            # Generate API credentials (the library handles L1 auth for us)
            creds = self._clob_client.create_or_derive_api_creds()
            self._clob_client.set_api_creds(creds)

            logger.info("CLOB client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize CLOB client: {e}")
            self._clob_client = None

    async def __aenter__(self) -> "PolymarketClient":
        """Enter the async context - create the HTTP client."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"Accept": "application/json"},
        )
        logger.info(f"PolymarketClient connected to {self.base_url}")

        if self._clob_client:
            logger.info("CLOB client ready for trade data")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the async context - close the HTTP client."""
        if self._client:
            await self._client.aclose()

        # Shutdown the thread executor
        self._executor.shutdown(wait=False)

        logger.info("PolymarketClient connection closed")

    async def _get(self, endpoint: str, params: dict | None = None) -> Any:
        """
        Make a GET request to the API.

        This is a helper method - it handles the common stuff so our
        other methods can focus on their specific logic.

        Args:
            endpoint: The API endpoint (e.g., "/markets")
            params: Query parameters (e.g., {"limit": 10})

        Returns:
            The JSON response data

        Raises:
            PolymarketClientError: If the request fails
        """
        if not self._client:
            raise PolymarketClientError("Client not initialized. Use 'async with'.")

        try:
            response = await self._client.get(endpoint, params=params)
            response.raise_for_status()  # Raises exception for 4xx/5xx status
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise PolymarketClientError(f"API error: {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            raise PolymarketClientError(f"Request failed: {e}") from e

    async def get_markets(
        self,
        limit: int = 100,
        active: bool = True,
        closed: bool = False,
    ) -> list[Market]:
        """
        Fetch available markets from Polymarket.

        Args:
            limit: Maximum number of markets to return
            active: Only return active (tradeable) markets
            closed: Include closed markets

        Returns:
            List of Market objects
        """
        logger.info(f"Fetching markets (limit={limit}, active={active})")

        params = {
            "limit": limit,
            "active": str(active).lower(),
            "closed": str(closed).lower(),
        }

        data = await self._get("/markets", params=params)

        # The API returns a list of market dictionaries
        # We convert each one to our Market model
        markets = []
        for item in data:
            try:
                market = self._parse_market(item)
                markets.append(market)
            except Exception as e:
                # Log but don't crash - some markets might have weird data
                logger.warning(f"Failed to parse market {item.get('id', 'unknown')}: {e}")

        logger.info(f"Fetched {len(markets)} markets")
        return markets

    async def get_market(self, market_id: str) -> Market | None:
        """
        Fetch a single market by ID.

        Args:
            market_id: The market's unique identifier

        Returns:
            Market object or None if not found
        """
        logger.info(f"Fetching market {market_id}")

        try:
            data = await self._get(f"/markets/{market_id}")
            return self._parse_market(data)
        except PolymarketClientError:
            logger.warning(f"Market {market_id} not found")
            return None

    async def get_recent_trades(
        self,
        limit: int = 100,
    ) -> list[Trade]:
        """
        Fetch recent PUBLIC trades from Polymarket Data API.

        Uses the public data-api.polymarket.com endpoint which returns
        ALL trades (not just user's trades). Perfect for whale watching!

        Args:
            limit: Maximum number of trades to return

        Returns:
            List of Trade objects, newest first
        """
        if not self._client:
            raise PolymarketClientError("Client not initialized. Use 'async with'.")

        try:
            params: dict[str, int] = {"limit": limit}

            # Use our existing httpx client to fetch from Data API
            response = await self._client.get(
                f"{DATA_API_BASE_URL}/trades",
                params=params
            )
            response.raise_for_status()
            raw_trades = response.json()

            # Convert to our Trade model using existing parser
            trades = []
            for item in raw_trades[:limit]:
                try:
                    trade = self._parse_trade(item)
                    trades.append(trade)
                except Exception as e:
                    logger.warning(f"Failed to parse trade: {e}")

            logger.info(f"Fetched {len(trades)} trades from Data API")
            return trades

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching trades: {e.response.status_code}")
            raise PolymarketClientError(f"Data API error: {e.response.status_code}") from e
        except Exception as e:
            logger.error(f"Failed to fetch trades: {e}")
            raise PolymarketClientError(f"Data API error: {e}") from e

    async def get_market_trades(
        self,
        market_id: str,
        limit: int = 100,
    ) -> list[Trade]:
        """
        Fetch trades for a specific market from Polymarket Data API.

        Uses the public data-api.polymarket.com endpoint filtered by market.

        Args:
            market_id: The market's condition_id to get trades for
            limit: Maximum number of trades

        Returns:
            List of Trade objects for this market
        """
        if not self._client:
            raise PolymarketClientError("Client not initialized. Use 'async with'.")

        try:
            params: dict[str, int | str] = {
                "limit": limit,
                "market": market_id,  # Filter by market condition_id
            }

            response = await self._client.get(
                f"{DATA_API_BASE_URL}/trades",
                params=params
            )
            response.raise_for_status()
            raw_trades = response.json()

            # Convert to our Trade model using existing parser
            trades = []
            for item in raw_trades[:limit]:
                try:
                    trade = self._parse_trade(item)
                    trades.append(trade)
                except Exception as e:
                    logger.warning(f"Failed to parse trade: {e}")

            logger.info(f"Fetched {len(trades)} trades for market {market_id}")
            return trades

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching market trades: {e.response.status_code}")
            raise PolymarketClientError(f"Data API error: {e.response.status_code}") from e
        except Exception as e:
            logger.error(f"Failed to fetch market trades: {e}")
            raise PolymarketClientError(f"Data API error: {e}") from e

    def _parse_market(self, data: dict) -> Market:
        """
        Convert raw API data into a Market object.

        The API might return data in a different format than we want,
        so we do the conversion here in one place.
        """
        # Handle different possible field names from the API
        outcome_prices = []
        if "outcomePrices" in data:
            # API returns prices as strings like '["0.65", "0.35"]'
            prices = data["outcomePrices"]
            if isinstance(prices, str):
                import json
                prices = json.loads(prices)
            outcome_prices = [float(p) for p in prices]
        elif "outcomes" in data and isinstance(data["outcomes"], list):
            # Some responses have outcomes with embedded prices
            for outcome in data["outcomes"]:
                if isinstance(outcome, dict) and "price" in outcome:
                    outcome_prices.append(float(outcome["price"]))

        # Parse outcomes list
        outcomes = ["Yes", "No"]  # Default
        if "outcomes" in data:
            raw_outcomes = data["outcomes"]
            if isinstance(raw_outcomes, str):
                import json
                outcomes = json.loads(raw_outcomes)
            elif isinstance(raw_outcomes, list):
                if raw_outcomes and isinstance(raw_outcomes[0], str):
                    outcomes = raw_outcomes

        # Parse end date
        end_date = None
        if data.get("endDate"):
            try:
                end_date = datetime.fromisoformat(
                    data["endDate"].replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                pass

        return Market(
            id=str(data.get("id", "")),
            condition_id=str(data.get("conditionId", data.get("condition_id", ""))),
            question=data.get("question", ""),
            description=data.get("description", ""),
            outcomes=outcomes,
            outcome_prices=outcome_prices,
            volume=float(data.get("volume", 0) or 0),
            liquidity=float(data.get("liquidity", 0) or 0),
            end_date=end_date,
            active=data.get("active", True),
            slug=data.get("slug", ""),
        )

    def _parse_trade(self, data: dict) -> Trade:
        """
        Convert raw API data into a Trade object.
        """
        # Parse timestamp
        timestamp = datetime.now()  # Fallback
        if data.get("timestamp"):
            try:
                # Handle Unix timestamp (seconds or milliseconds)
                ts = data["timestamp"]
                if isinstance(ts, (int, float)):
                    if ts > 1e12:  # Milliseconds
                        ts = ts / 1000
                    timestamp = datetime.fromtimestamp(ts)
                else:
                    timestamp = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

        # Parse trade side
        side_str = str(data.get("side", "BUY")).upper()
        side = TradeSide.BUY if side_str == "BUY" else TradeSide.SELL

        return Trade(
            id=str(data.get("id", "")),
            market_id=str(data.get("market", data.get("market_id", ""))),
            asset_id=str(data.get("asset_id", data.get("assetId", ""))),
            side=side,
            price=float(data.get("price", 0) or 0),
            size=float(data.get("size", 0) or 0),
            outcome=str(data.get("outcome", "")),
            timestamp=timestamp,
            maker_address=str(data.get("maker_address", data.get("makerAddress", ""))),
            taker_address=str(data.get("taker_address", data.get("takerAddress", ""))),
        )
