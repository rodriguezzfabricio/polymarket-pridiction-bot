"""
CLOB API specific data models.

These models represent data structures specific to the CLOB API,
including authentication credentials and raw API responses.
"""

from pydantic import BaseModel, Field


class ClobApiCredentials(BaseModel):
    """
    L2 API credentials for CLOB authentication.

    These credentials are generated from your wallet's private key (L1 auth)
    and used to sign all subsequent CLOB API requests (L2 auth).
    """

    api_key: str = Field(..., description="API key UUID", alias="apiKey")
    api_secret: str = Field(..., description="Base64 encoded secret", alias="secret")
    passphrase: str = Field(..., description="API passphrase")

    class Config:
        populate_by_name = True  # Allow both snake_case and camelCase


class ClobTradeResponse(BaseModel):
    """
    Raw trade data from CLOB API.

    This represents the structure of trade data as returned by the CLOB API.
    We convert this to our standard Trade model after parsing.
    """

    id: str = Field(..., description="Unique trade identifier")
    market: str = Field(..., description="Market ID")
    asset_id: str = Field(..., description="Token/asset being traded", alias="assetId")
    side: str = Field(..., description="BUY or SELL")
    price: str = Field(..., description="Trade price as decimal string")
    size: str = Field(..., description="Trade size as decimal string")
    timestamp: int = Field(..., description="Unix timestamp")
    maker_address: str | None = Field(
        default=None, description="Wallet that made the order", alias="makerAddress"
    )
    taker_address: str | None = Field(
        default=None, description="Wallet that took the order", alias="takerAddress"
    )
    outcome: str | None = Field(default=None, description="Which outcome was traded")

    class Config:
        populate_by_name = True  # Allow both snake_case and camelCase
