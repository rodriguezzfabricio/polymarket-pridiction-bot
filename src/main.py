"""
Polymarket Trading Bot - FastAPI Application Entry Point.

This module initializes the FastAPI application and defines the root endpoints.

HOW THIS FILE WORKS:
-------------------
1. We create the FastAPI "app" - this is our web server
2. We register "routers" - groups of related endpoints
3. When someone hits an endpoint, FastAPI routes it to the right function

LIFESPAN:
---------
The `lifespan` function runs code at startup and shutdown.
Useful for: connecting to databases, warming up caches, cleanup, etc.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from src.api.routes.markets import router as markets_router
from src.api.routes.markets import trades_router
from src.core.config import get_settings

# Set up logging so we can see what's happening
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.

    Handles startup and shutdown events for the FastAPI application.

    Args:
        app: The FastAPI application instance.

    Yields:
        None
    """
    # Startup
    settings = get_settings()
    print(f"Starting {settings.APP_NAME}...")
    print(f"Running on http://{settings.API_HOST}:{settings.API_PORT}")
    print(f" Debug mode: {settings.DEBUG}")

    yield

    # Shutdown
    print(f"Shutting down {settings.APP_NAME}...")


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Trading bot for Polymarket prediction markets",
    version="0.1.0",
    lifespan=lifespan,
)

# Register our routers (groups of endpoints)
# This is like adding pages to a website
app.include_router(markets_router)  # Adds /markets endpoints
app.include_router(trades_router)   # Adds /trades endpoints


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        dict: Health status of the application.
    """
    return {"status": "healthy"}
