"""
REAL API Demo - How to Actually Connect to Polymarket

This shows you how to use REAL APIs to get LIVE data from Polymarket.
No more fake data - this connects to the actual internet APIs!

APIS YOU NEED TO KNOW ABOUT:
============================

1. GAMMA API (Public - No Auth Required) ✅
   - URL: https://gamma-api.polymarket.com
   - What it gives: Market data (questions, prices, volume)
   - Already implemented in: src/services/polymarket_client.py
   - Example: GET /markets returns all active markets

2. CLOB API (Requires API Key) 🔒
   - URL: https://clob.polymarket.com
   - What it gives: Trade data (who bought what, when, how much)
   - Status: NOT YET IMPLEMENTED (see lines 186-234 in polymarket_client.py)
   - You'll need: API credentials from Polymarket
   - This is what you need for WHALE WATCHING!

3. WebSocket API (Real-time) ⚡
   - For live updates as trades happen
   - Optional - batch polling works fine for MVP
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.polymarket_client import PolymarketClient


async def demo_1_get_real_markets():
    """
    Demo 1: Fetch REAL markets from Polymarket
    
    This actually calls the internet! No fake data!
    """
    print("=" * 70)
    print("DEMO 1: Fetching REAL Markets from Polymarket")
    print("=" * 70)
    print("📡 Connecting to https://gamma-api.polymarket.com...")
    print()
    
    # Use the client as a context manager (best practice)
    async with PolymarketClient() as client:
        # Fetch up to 5 markets for this demo
        markets = await client.get_markets(limit=5, active=True)
        
        print(f"✅ Successfully fetched {len(markets)} REAL markets!\n")
        
        # Display each market
        for i, market in enumerate(markets, 1):
            print(f"Market {i}: {market.question}")
            print(f"  ID: {market.id}")
            print(f"  Yes Price: {market.yes_price if market.yes_price else 'N/A'}")
            print(f"  No Price: {market.no_price if market.no_price else 'N/A'}")
            print(f"  Volume: ${market.volume:,.0f}")
            print(f"  Active: {market.active}")
            print(f"  URL: https://polymarket.com/event/{market.slug}")
            print()


async def demo_2_check_for_whales():
    """
    Demo 2: Try to get whale trades (will show what's missing)
    
    This demonstrates why you need the CLOB API for whale watching.
    """
    print("=" * 70)
    print("DEMO 2: Attempting to Fetch Whale Trades")
    print("=" * 70)
    
    async with PolymarketClient() as client:
        # Try to get trades (this will show the limitation)
        trades = await client.get_recent_trades(limit=10)
        
        if not trades:
            print("⚠️  No trades returned!")
            print()
            print("WHY? Trade data requires the CLOB API with authentication.")
            print()
            print("TO FIX THIS, YOU NEED:")
            print("1. Sign up at https://polymarket.com")
            print("2. Get API credentials from their developer portal")
            print("3. Implement CLOB client authentication")
            print("4. Then you can fetch real whale trades!")
            print()
            print("For now, markets work great (Demo 1 above).")
            print("Whale watching needs the authenticated API.")


async def demo_3_what_real_bot_would_do():
    """
    Demo 3: What your actual bot will do when fully set up
    """
    print("=" * 70)
    print("DEMO 3: Full Bot Flow (What You're Building Toward)")
    print("=" * 70)
    
    async with PolymarketClient() as client:
        # Step 1: Get some markets
        print("Step 1: Fetching markets...")
        markets = await client.get_markets(limit=3)
        print(f"✅ Found {len(markets)} markets\n")
        
        if markets:
            market = markets[0]
            print(f"Analyzing: {market.question}")
            print(f"Current Yes price: {market.yes_price}\n")
            
            # Step 2: Try to get trades for this market
            print("Step 2: Fetching whale trades...")
            trades = await client.get_market_trades(market.id, limit=10)
            
            if not trades:
                print("⚠️  No trades (CLOB API needed)\n")
                print("WHEN WORKING, YOUR BOT WOULD:")
                print("  1. Filter for whale trades (size >= $500)")
                print("  2. Check if multiple whales are buying")
                print("  3. Alert you if there's a pattern!")
                print("  4. You could auto-trade based on whale activity")
            else:
                # This will run once CLOB is set up
                whale_trades = [t for t in trades if t.is_whale_trade]
                print(f"🐋 Found {len(whale_trades)} whale trades!")


def explain_apis():
    """Print a clear explanation of what APIs you need"""
    print("\n")
    print("=" * 70)
    print("🎓 WHAT YOU LEARNED")
    print("=" * 70)
    print()
    print("API #1: GAMMA API (✅ ALREADY WORKING)")
    print("  - URL: https://gamma-api.polymarket.com")
    print("  - Auth: None required (public)")
    print("  - Data: Market info (questions, prices, volume)")
    print("  - File: src/services/polymarket_client.py")
    print("  - Status: ✅ Working! Run Demo 1 above to test")
    print()
    print("API #2: CLOB API (🔒 NEEDS SETUP)")
    print("  - URL: https://clob.polymarket.com") 
    print("  - Auth: API Key required")
    print("  - Data: Trade data (who bought what for how much)")
    print("  - Status: ❌ Not implemented yet")
    print("  - Why you need it: For whale watching!")
    print()
    print("HOW TO GET TRADE DATA:")
    print("  1. Create account at polymarket.com")
    print("  2. Get API credentials (check their docs)")
    print("  3. Extend polymarket_client.py to authenticate with CLOB")
    print("  4. Implement get_recent_trades() and get_market_trades()")
    print()
    print("ALTERNATIVE (If you can't get CLOB access):")
    print("  - Use their public data exports")
    print("  - Scrape trade data (against TOS, not recommended)")
    print("  - Use WebSocket to listen for trades (may still need auth)")
    print()
    print("YOUR NEXT STEP:")
    print("  Research Polymarket's CLOB API documentation")
    print("  Link: https://docs.polymarket.com/ (check for API section)")
    print("=" * 70)


async def main():
    """Run all demos"""
    print("\n🚀 POLYMARKET REAL API DEMO\n")
    
    # Demo 1: Actually works!
    await demo_1_get_real_markets()
    
    input("\nPress Enter to continue to Demo 2...")
    print("\n")
    
    # Demo 2: Shows what's missing
    await demo_2_check_for_whales()
    
    input("\nPress Enter to continue to Demo 3...")
    print("\n")
    
    # Demo 3: The full picture
    await demo_3_what_real_bot_would_do()
    
    # Explanation
    explain_apis()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
