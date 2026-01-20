# FastAPI route handlers
from src.api.routes.markets import router as markets_router
from src.api.routes.markets import trades_router

__all__ = ["markets_router", "trades_router"]
