"""
Example: How Trade and Market Classes Work Together

This file demonstrates how to use the Market and Trade models in real code.
Perfect for understanding the relationship between these two classes!
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from src.models.market import Market, Trade, TradeSide, MarketWithTrades


def example_1_basic_usage():
    """Example 1: Creating a Market and Some Trades"""
    print("=" * 60)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 60)
    
    # Create a market
    market = Market(
        id="market_btc_100k",
        condition_id="0x1234abcd",
        question="Will Bitcoin hit $100k by Dec 31, 2025?",
        description="Resolves YES if BTC >= $100,000 on Dec 31, 2025",
        outcomes=["Yes", "No"],
        outcome_prices=[0.30, 0.70],  # 30% Yes, 70% No
        volume=2_450_000.0,  # $2.45M traded so far
        liquidity=150_000.0,
        slug="bitcoin-100k-2025"
    )
    
    print(f"Market: {market.question}")
    print(f"Current Yes price: {market.yes_price} (30% chance)")
    print(f"Current No price: {market.no_price} (70% chance)")
    print(f"Total volume: ${market.volume:,.0f}")
    print()
    
    # Create some trades on this market
    trades = [
        Trade(
            id="trade_1",
            market_id=market.id,  # Links to the market above!
            side=TradeSide.BUY,
            price=0.30,
            size=5_000.0,  # $5,000 - This is a WHALE!
            outcome="Yes",
            timestamp=datetime(2025, 1, 19, 14, 30),
            maker_address="0xAB12...34CD",
            taker_address="0xEF56...78GH"
        ),
        Trade(
            id="trade_2",
            market_id=market.id,  # Same market!
            side=TradeSide.BUY,
            price=0.32,
            size=3_500.0,  # Another whale!
            outcome="Yes",
            timestamp=datetime(2025, 1, 19, 14, 35),
            maker_address="0x1234...5678",
            taker_address="0xABCD...EFGH"
        ),
        Trade(
            id="trade_3",
            market_id=market.id,
            side=TradeSide.SELL,
            price=0.68,
            size=200.0,  # Regular trade (not a whale)
            outcome="No",
            timestamp=datetime(2025, 1, 19, 14, 40),
            maker_address="0x9999...1111",
            taker_address="0x2222...3333"
        ),
    ]
    
    # Print all trades
    for i, trade in enumerate(trades, 1):
        whale_emoji = "🐋" if trade.is_whale_trade else "🐟"
        print(f"Trade {i} {whale_emoji}:")
        print(f"  Side: {trade.side.value}")
        print(f"  Size: ${trade.size:,.0f}")
        print(f"  Price: {trade.price} ({trade.price * 100:.0f}%)")
        print(f"  Outcome: {trade.outcome}")
        print(f"  Is Whale? {trade.is_whale_trade}")
        print()


def example_2_whale_detection():
    """Example 2: Detecting Whale Trades (Your Bot's Main Job!)"""
    print("=" * 60)
    print("EXAMPLE 2: Whale Detection")
    print("=" * 60)
    
    # Simulate some trades on a market
    trades = [
        Trade(id="t1", market_id="m1", side=TradeSide.BUY, price=0.30, 
              size=5_000.0, outcome="Yes", timestamp=datetime.now()),
        Trade(id="t2", market_id="m1", side=TradeSide.BUY, price=0.32, 
              size=3_500.0, outcome="Yes", timestamp=datetime.now()),
        Trade(id="t3", market_id="m1", side=TradeSide.SELL, price=0.68, 
              size=200.0, outcome="No", timestamp=datetime.now()),
        Trade(id="t4", market_id="m1", side=TradeSide.BUY, price=0.35, 
              size=100.0, outcome="Yes", timestamp=datetime.now()),
    ]
    
    # Filter for whale trades only
    whale_trades = [t for t in trades if t.is_whale_trade]
    
    print(f"Total trades: {len(trades)}")
    print(f"Whale trades (>=$500): {len(whale_trades)}")
    print()
    
    # Analyze whale behavior
    if whale_trades:
        print("🐋 WHALE ACTIVITY DETECTED!")
        for trade in whale_trades:
            action = "bought" if trade.side == TradeSide.BUY else "sold"
            print(f"  - Whale {action} ${trade.size:,.0f} of {trade.outcome} at {trade.price:.2%}")
        
        # Are whales bullish or bearish?
        whale_buys = sum(1 for t in whale_trades if t.side == TradeSide.BUY)
        whale_sells = sum(1 for t in whale_trades if t.side == TradeSide.SELL)
        
        print()
        print(f"Whale sentiment: {whale_buys} BUYs vs {whale_sells} SELLs")
        if whale_buys > whale_sells:
            print("📈 BULLISH SIGNAL - Whales are buying!")
        else:
            print("📉 BEARISH SIGNAL - Whales are selling!")


def example_3_market_with_trades():
    """Example 3: Using MarketWithTrades (Bundle Everything Together)"""
    print("=" * 60)
    print("EXAMPLE 3: MarketWithTrades")
    print("=" * 60)
    
    # Create a market
    market = Market(
        id="market_trump_2024",
        condition_id="0xabcd",
        question="Will Trump win 2024 election?",
        outcomes=["Yes", "No"],
        outcome_prices=[0.55, 0.45],
        volume=10_000_000.0
    )
    
    # Create trades for this market
    trades = [
        Trade(id="t1", market_id=market.id, side=TradeSide.BUY, 
              price=0.55, size=10_000.0, outcome="Yes", timestamp=datetime.now()),
        Trade(id="t2", market_id=market.id, side=TradeSide.SELL, 
              price=0.45, size=7_500.0, outcome="No", timestamp=datetime.now()),
    ]
    
    # Bundle them together!
    market_with_trades = MarketWithTrades(
        market=market,
        trades=trades
    )
    
    print(f"Market: {market_with_trades.market.question}")
    print(f"Yes price: {market_with_trades.market.yes_price}")
    print(f"Number of trades: {len(market_with_trades.trades)}")
    print()
    
    # Analyze the bundled data
    whale_count = sum(1 for t in market_with_trades.trades if t.is_whale_trade)
    total_whale_volume = sum(t.size for t in market_with_trades.trades if t.is_whale_trade)
    
    print(f"Whale trades: {whale_count}")
    print(f"Total whale volume: ${total_whale_volume:,.0f}")


def example_4_real_bot_logic():
    """Example 4: Realistic Bot Logic (What Your Bot Will Actually Do)"""
    print("=" * 60)
    print("EXAMPLE 4: Real Bot Logic")
    print("=" * 60)
    
    # Simulate fetching market data from Polymarket API
    market = Market(
        id="market_btc",
        condition_id="0x1234",
        question="Will Bitcoin hit $100k by end of 2025?",
        outcomes=["Yes", "No"],
        outcome_prices=[0.30, 0.70],
        volume=5_000_000.0
    )
    
    # Simulate recent trades (what you'd get from API)
    recent_trades = [
        Trade(id="t1", market_id=market.id, side=TradeSide.BUY, 
              price=0.30, size=8_000.0, outcome="Yes", 
              timestamp=datetime(2025, 1, 19, 14, 30)),
        Trade(id="t2", market_id=market.id, side=TradeSide.BUY, 
              price=0.31, size=6_000.0, outcome="Yes", 
              timestamp=datetime(2025, 1, 19, 14, 33)),
        Trade(id="t3", market_id=market.id, side=TradeSide.BUY, 
              price=0.32, size=12_000.0, outcome="Yes", 
              timestamp=datetime(2025, 1, 19, 14, 35)),
    ]
    
    # YOUR BOT'S LOGIC:
    print("🤖 BOT ANALYZING MARKET...")
    print(f"Market: {market.question}")
    print(f"Current Yes price: {market.yes_price:.2%}")
    print()
    
    # Step 1: Find whale trades
    whale_trades = [t for t in recent_trades if t.is_whale_trade]
    print(f"✅ Found {len(whale_trades)} whale trades in last 5 minutes")
    
    # Step 2: Check if they're all buying the same thing
    yes_whales = [t for t in whale_trades if t.outcome == "Yes" and t.side == TradeSide.BUY]
    total_whale_money = sum(t.size for t in yes_whales)
    
    print(f"✅ {len(yes_whales)} whales bought YES")
    print(f"✅ Total whale volume: ${total_whale_money:,.0f}")
    print()
    
    # Step 3: Make a decision
    if len(yes_whales) >= 3 and total_whale_money >= 20_000:
        print("🚨 STRONG BULLISH SIGNAL!")
        print("   Multiple whales aggressively buying YES")
        print("   → BOT RECOMMENDATION: Consider buying YES")
        print(f"   → If whales are right, YES should move from {market.yes_price:.2%} to much higher")
    else:
        print("⏸️  No strong signal yet, keep monitoring...")


if __name__ == "__main__":
    # Run all examples
    example_1_basic_usage()
    print("\n" * 2)
    
    example_2_whale_detection()
    print("\n" * 2)
    
    example_3_market_with_trades()
    print("\n" * 2)
    
    example_4_real_bot_logic()
    print("\n" * 2)
    
    print("=" * 60)
    print("🎓 KEY LEARNINGS:")
    print("=" * 60)
    print("1. Market = The question being bet on")
    print("2. Trade = One person placing one bet")
    print("3. trade.market_id links a Trade to a Market")
    print("4. trade.is_whale_trade filters for big money (>=$500)")
    print("5. Your bot watches for multiple whales buying the same thing")
    print("6. MarketWithTrades bundles everything together")
    print("=" * 60)
