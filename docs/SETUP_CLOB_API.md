# Setting Up CLOB API for Whale Watching

## The Problem

Right now your bot can fetch **markets** (questions, prices) but NOT **trades** (who's buying/selling).

For whale watching, you NEED trade data. That's where the CLOB API comes in.

---

## What is CLOB?

**CLOB = Central Limit Order Book**

It's Polymarket's trading engine. The CLOB API gives you:
- All trades happening in real-time
- Trade size (the $$$ amount - critical for whale detection!)
- Who traded (wallet addresses)
- Price they paid
- Timestamp

---

## Two Options to Get Trade Data

### Option 1: CLOB API (Official, Requires Auth)

**Step 1:** Create a Polymarket Account
- Go to https://polymarket.com
- Connect a wallet (MetaMask, etc.)

**Step 2:** Get API Credentials
- Check Polymarket's docs: https://docs.polymarket.com/
- Look for "CLOB API" or "Developer API"
- You'll need:
  - API Key
  - API Secret (or Private Key)
  - Possibly a passphrase

**Step 3:** Implement Authentication in Your Bot
- Update `src/services/polymarket_client.py`
- Add authentication headers to requests
- Implement the `get_recent_trades()` method properly

**Example of what you'll need to add:**
```python
# In polymarket_client.py
CLOB_API_BASE_URL = "https://clob.polymarket.com"

async def get_recent_trades(self, limit: int = 100) -> list[Trade]:
    """Fetch real trades using CLOB API"""
    headers = {
        "Authorization": f"Bearer {self.api_key}",  # Your API key
        # Other auth headers from Polymarket docs
    }
    
    response = await self._client.get(
        f"{CLOB_API_BASE_URL}/trades",
        headers=headers,
        params={"limit": limit}
    )
    
    # Parse the trades
    trades = [self._parse_trade(item) for item in response.json()]
    return trades
```

---

### Option 2: Public Trade Data (No Auth, But Limited)

If you can't get CLOB API access, there are alternatives:

**A) Polymarket's Public Endpoints**
- Some trade data might be available on the Gamma API
- Check: `https://gamma-api.polymarket.com/trades`
- May be limited or delayed

**B) The Graph Protocol**
- Polymarket data might be indexed on The Graph
- GraphQL endpoint for historical trades
- Free but may not be real-time

**C) Direct Blockchain Monitoring**
- Polymarket runs on Polygon blockchain
- Monitor the smart contract directly
- Pros: Free, real-time
- Cons: Complex, requires blockchain knowledge

---

## Recommended Path Forward

### For Learning (Right Now):
1. ✅ You already have market data working
2. Use **mock trade data** for testing your whale detection logic
3. Get your bot's logic perfect with fake data first

### For Production (Later):
1. Research Polymarket's official CLOB API documentation
2. Get API credentials
3. Implement authentication in `polymarket_client.py`
4. Test with real trade data

---

## Next Steps

### Immediate (While You Research CLOB):
1. **Build your whale detection logic** with mock data
2. Perfect your alerts and notifications
3. Test patterns like "3 whales buy YES within 5 minutes"

### When You're Ready:
1. Sign up for Polymarket
2. Get CLOB API credentials
3. I'll help you implement the authentication
4. Connect real trade data

---

## Key Takeaway

**You have TWO separate APIs:**

| API | What It Does | Status | Auth Needed |
|-----|--------------|--------|-------------|
| **Gamma API** | Markets, prices, volume | ✅ Working | ❌ No |
| **CLOB API** | Trade data (whale watching) | ❌ Not setup | ✅ Yes |

**For whale watching to work, you MUST get the CLOB API set up.**

---

## Resources

- Polymarket Docs: https://docs.polymarket.com/
- CLOB API Info: Check their developer section
- Discord/Support: They may have a developer Discord

---

## Questions?

**Q: Can I whale watch without CLOB?**  
A: Not really. You need trade data to see whale activity. Markets alone just show current prices.

**Q: Is CLOB API free?**  
A: Check their docs. Many API providers have free tiers for developers.

**Q: What if I can't get CLOB access?**  
A: Try alternatives (The Graph, blockchain monitoring) or focus on price movement analysis instead of whale detection.
