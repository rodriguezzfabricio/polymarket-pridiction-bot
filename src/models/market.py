"""
Market and Trade models for Polymarket data.

These Pydantic models define the SHAPE of data we expect from the Polymarket API.
Think of them as contracts: if the data doesn't match, we'll know immediately.

WHY PYDANTIC?
-------------
1. Automatic validation - bad data gets rejected early
2. Type hints - your IDE can help you
3. Serialization - easy to convert to/from JSON
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TradeSide(str, Enum):
    """
    Which side of a trade someone took.

    BUY = They bought shares (betting something WILL happen)
    SELL = They sold shares (betting something WON'T happen, or taking profit)
    """

    BUY = "BUY"
    SELL = "SELL"


class Outcome(BaseModel):
    """
    A possible outcome for a market.

    Example: For "Will it rain tomorrow?"
    - Outcome 1: "Yes" with token_id "abc123"
    - Outcome 2: "No" with token_id "def456"
    """

    outcome: str = Field(..., description="The outcome name, e.g., 'Yes' or 'No'")
    price: float = Field(
        ..., ge=0.0, le=1.0, description="Current price (0-1, represents probability)"
    )


class Market(BaseModel):
    """
    A prediction market from Polymarket.

    A market is essentially a question that people bet on.
    Example: "Will Bitcoin hit $100k by end of 2025?"

    People buy "Yes" or "No" shares. Prices move based on demand.
    If "Yes" is at $0.70, the crowd thinks there's a 70% chance.
    """

    id: str = Field(..., description="Unique market identifier")
    condition_id: str = Field(..., description="Condition ID for trading")
    question: str = Field(..., description="The market question being bet on")
    description: str = Field(default="", description="Detailed market description")
    outcomes: list[str] = Field(
        default_factory=lambda: ["Yes", "No"],
        description="Possible outcomes (usually Yes/No)",
    )
    outcome_prices: list[float] = Field(
        default_factory=list, description="Current prices for each outcome"
    )
    volume: float = Field(default=0.0, ge=0, description="Total trading volume in USD")
    liquidity: float = Field(default=0.0, ge=0, description="Available liquidity in USD")
    end_date: datetime | None = Field(
        default=None, description="When the market resolves"
    )
    active: bool = Field(default=True, description="Whether market is still tradeable")
    slug: str = Field(default="", description="URL-friendly market identifier")

    @property
    def yes_price(self) -> float | None:
        """Get the current 'Yes' price (probability) if available."""
        if self.outcome_prices and len(self.outcome_prices) > 0:
            return self.outcome_prices[0]
        return None

    @property
    def no_price(self) -> float | None:
        """Get the current 'No' price if available."""
        if self.outcome_prices and len(self.outcome_prices) > 1:
            return self.outcome_prices[1]
        return None


class Trade(BaseModel):
    """
    A single trade that happened on Polymarket.

    This is the core data for whale watching - we look for big trades
    and try to understand what smart money is doing.

    KEY FIELDS:
    - size: How much money (in USD) was traded. Big number = potential whale.
    - side: BUY or SELL. Whale buying = bullish signal.
    - price: What probability they bought at. Buying at 0.30 means they think
             something has a better than 30% chance of happening.
    """

    id: str = Field(..., description="Unique trade identifier")
    market_id: str = Field(..., description="Which market this trade is for")
    asset_id: str = Field(default="", description="Token/asset being traded")
    side: TradeSide = Field(..., description="BUY or SELL")
    price: float = Field(
        ..., ge=0.0, le=1.0, description="Trade price (0-1, probability)"
    )
    size: float = Field(..., ge=0, description="Trade size in USD")
    outcome: str = Field(default="", description="Which outcome was traded (Yes/No)")
    timestamp: datetime = Field(..., description="When the trade happened")
    maker_address: str = Field(default="", description="Wallet that made the order")
    taker_address: str = Field(default="", description="Wallet that took the order")

    @property
    def is_whale_trade(self) -> bool:
        """
        Quick check: Is this a whale trade?

        We define "whale" as > $500 for MVP.
        In production, you might want this threshold configurable.
        """
        return self.size >= 500.0


class MarketWithTrades(BaseModel):
    """
    A market bundled with its recent trades.

    Useful for the whale detector - we want to see both the market
    (what's being bet on) and the trades (who's betting what).
    """

    market: Market
    trades: list[Trade] = Field(default_factory=list)
