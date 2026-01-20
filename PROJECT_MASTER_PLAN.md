# PROJECT_MASTER_PLAN.md

## Executive Summary
We are building a **Polymarket Trading Bot** designed for a "broke college student" budget, aiming for a **Minimum Viable Product (MVP)** within **1 week**. The bot will leverage **Whale Tracking** to identify smart money moves and an **AI Agent Swarm** (via OpenRouter) to validate these moves before trading. This approach combines the speed of automation with the intelligence of LLM consensus.

## Core Strategy
The system follows the **RBI Framework** (Research, Backtest, Implement) and focuses on "following the winners."

### 1. Whale Tracking (The "Signal")
*   **Concept**: Monitoring Polymarket for large trades (e.g., >$500) or activity from known profitable wallets ("Whales").
*   **Hypothesis**: Smart money moves first. We detect the move, validating it before the broader market catches up.
*   **Filtering**: Ignore high-noise/efficient markets (like major Sports games or Crypto prices) if they are too competitive. Focus on "Information Markets" (politics, news, obscure events) where AI has an edge.

### 2. AI Swarm Consensus (The "Filter")
*   **Concept**: When a Whale trade is detected, send the market question and context to a "Swarm" of AI Agents via OpenRouter (e.g., DeepSeek, Claude, Llama).
*   **Consensus**: If a majority (e.g., 4 out of 6) agree that the Whale's position makes sense, generate a **BUY** signal.
*   **Reasoning**: This reduces false positives from "dumb whales" or market manipulation.

### 3. RBI Framework
*   **Research**: Manually or semi-automatically identify strategies (done: Whale + Swarm).
*   **Backtest**: validate strategy logic (or use paper trading for forward testing in this rapid MVP).
*   **Implement**: Deploy the verified logic into the live bot.

## Technical Architecture

**Stack**: Python + FastAPI + OpenRouter

```mermaid
graph TD
    A[Polymarket API (Gamma)] -->|Real-time Data| B(Whale/Signal Detector)
    B -->|Potential Trade > $500| C{AI Agent Swarm}
    
    subgraph OpenRouter
    D[DeepSeek]
    E[Claude 3.5]
    F[Llama 3]
    end
    
    C -->|Query| D
    C -->|Query| E
    C -->|Query| F
    
    D -->|Vote| G[Consensus Engine]
    E -->|Vote| G
    F -->|Vote| G
    
    G -->|Broad Consensus > 66%| H[Execution Engine]
    H -->|Place Order| A
```

*   **Language**: Python (Typesafe, Async).
*   **Backend**: FastAPI (High performance, easy documentation).
*   **LLM Provider**: OpenRouter (Access to best-in-class models cheaply).
*   **Database**: Simple JSON/SQLite for MVP (keep costs zero).

## Video Learnings & Alpha
*   **"Combinatorial Intelligence"**: One model might be wrong, but a swarm of varied models (DeepSeek for logic, Claude for nuance) is rarely wrong.
*   **24/7 Advantage**: Humans sleep; bots don't. The edge is often in being awake when news breaks.
*   **Cost Efficiency**: OpenRouter allows paying only for what we use, avoiding expensive monthly subscriptions for multiple discrete APIs.
*   **Focus**: Don't try to predict *everything*. Predict valid moves initiated by successful players.

## Week 1 Roadmap (MVP)

*   **Day 1: Foundation**
    *   Set up Python environment (FastAPI, Pydantic).
    *   Connect to Polymarket (Gamma) API to fetch markets and recent trades.
*   **Day 2: The Watcher**
    *   Implement `WhaleDetector` service.
    *   Filter for trades > $500.
*   **Day 3: The Brain (OpenRouter)**
    *   Set up OpenRouter integration.
    *   Create prompt templates for market analysis.
*   **Day 4: The Swarm**
    *   Implement the "Consensus" logic (Aggregating AI votes).
    *   Connect Detector -> Swarm -> Output.
*   **Day 5: Paper Trading**
    *   Run the bot in "Read-Only" mode.
    *   Log all "Would Buy" signals and track their theoretical performance.
*   **Day 6: Refinement**
    *   Adjust prompts and thresholds based on Day 5 data.
    *   Add basic error handling and rate limiting.
*   **Day 7: Launch**
    *   Final code review.
    *   Go live (or "Hardened Paper Mode").

## Success Metrics
1.  **Metric**: **Signal Quality**.
    *   *Target*: > 60% of "Consensus Trades" end up profitable (ITM) after 24h.
2.  **Metric**: **Uptime**.
    *   *Target*: Bot runs for 24h without crashing.
3.  **Metric**: **Cost**.
    *   *Target*: Operational costs (LLM tokens) < $5/day.
