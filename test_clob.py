"""
Test script for CLOB API integration.

Run this to verify your setup is working:
    python test_clob.py

Before running:
1. pip install -r requirements.txt
2. Copy .env.example to .env
3. Add your POLYGON_WALLET_PRIVATE_KEY to .env
"""

import asyncio
import sys

from src.core.config import get_settings
from src.services.polymarket_client import PolymarketClient


async def main():
    print("=" * 50)
    print("CLOB API Integration Test")
    print("=" * 50)

    # Load settings
    settings = get_settings()

    # Check if private key is configured
    if not settings.POLYGON_WALLET_PRIVATE_KEY:
        print("\nERROR: POLYGON_WALLET_PRIVATE_KEY not set!")
        print("\nTo fix this:")
        print("1. Copy .env.example to .env")
        print("2. Add your private key (from MetaMask) to .env")
        print("   POLYGON_WALLET_PRIVATE_KEY=your_key_here")
        print("\nHow to get your private key from MetaMask:")
        print("  - Open MetaMask")
        print("  - Click the three dots menu")
        print("  - Account Details → Export Private Key")
        print("  - Enter password and copy the key")
        sys.exit(1)

    print(f"\nPrivate key configured: {'*' * 8}...{settings.POLYGON_WALLET_PRIVATE_KEY[-4:]}")

    # Test 1: Initialize client
    print("\n[TEST 1] Initializing client with CLOB auth...")
    try:
        async with PolymarketClient(
            private_key=settings.POLYGON_WALLET_PRIVATE_KEY
        ) as client:
            print("✓ Client initialized successfully")

            # Test 2: Fetch markets (this doesn't need auth)
            print("\n[TEST 2] Fetching markets (Gamma API)...")
            markets = await client.get_markets(limit=3)
            print(f"✓ Fetched {len(markets)} markets")
            for m in markets[:3]:
                print(f"  - {m.question[:50]}...")

            # Test 3: Fetch trades (this needs CLOB auth)
            print("\n[TEST 3] Fetching trades (CLOB API)...")
            trades = await client.get_recent_trades(limit=10)

            if trades:
                print(f"✓ Fetched {len(trades)} trades")
                print("\nRecent trades:")
                for trade in trades[:5]:
                    whale = " [WHALE]" if trade.is_whale_trade else ""
                    print(
                        f"  ${trade.size:>10.2f} {trade.side.value:4} "
                        f"@ {trade.price:.2f}{whale}"
                    )
            else:
                print("! No trades returned (this might be normal if there's no recent activity)")

            print("\n" + "=" * 50)
            print("ALL TESTS PASSED!")
            print("=" * 50)
            print("\nYour CLOB API integration is working.")
            print("You can now fetch real trade data for whale watching.")

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print("\nPossible issues:")
        print("1. Invalid private key - check it's correct")
        print("2. Network issues - check your internet connection")
        print("3. py-clob-client not installed - run: pip install py-clob-client")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
