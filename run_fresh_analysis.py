#!/usr/bin/env python3
"""
Run TradingAgents analysis with fresh data (no cached data).
This script bypasses the interactive CLI and runs the complete flow programmatically.
"""

import load_env  # Load .env file
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from datetime import datetime, timedelta

def run_fresh_analysis():
    """Run complete TradingAgents analysis with fresh online data."""
    
    # Configuration for fresh data analysis
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "openai"
    config["backend_url"] = "https://api.openai.com/v1"
    config["deep_think_llm"] = "gpt-4o"
    config["quick_think_llm"] = "gpt-4o-mini"
    config["max_debate_rounds"] = 2  # More thorough analysis
    config["online_tools"] = True    # Force online data only
    
    # Use a recent date to ensure fresh data
    analysis_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    ticker = "TSLA"  # Tesla for analysis
    
    print(f"🚀 Starting TradingAgents Analysis")
    print(f"📊 Ticker: {ticker}")
    print(f"📅 Date: {analysis_date}")
    print(f"🌐 Using fresh online data only")
    print(f"🤖 LLM Provider: {config['llm_provider']}")
    print(f"🧠 Deep Model: {config['deep_think_llm']}")
    print(f"⚡ Quick Model: {config['quick_think_llm']}")
    print(f"💬 Debate Rounds: {config['max_debate_rounds']}")
    print("=" * 60)
    
    # Initialize TradingAgents with debug mode for detailed output
    ta = TradingAgentsGraph(
        selected_analysts=["market", "social", "news", "fundamentals"],
        debug=True,
        config=config
    )
    
    print(f"\n🔄 Running analysis for {ticker} on {analysis_date}...")
    print("This will use fresh data from:")
    print("• Yahoo Finance (live stock data)")
    print("• OpenAI web search (real-time news & social sentiment)")
    print("• Google News (recent articles)")
    print("• Live technical indicators")
    print("\n" + "=" * 60)
    
    # Run the analysis
    final_state, decision = ta.propagate(ticker, analysis_date)
    
    print("\n" + "=" * 60)
    print("🎯 FINAL TRADING DECISION")
    print("=" * 60)
    print(f"Decision: {decision}")
    print("=" * 60)
    
    return final_state, decision

if __name__ == "__main__":
    try:
        final_state, decision = run_fresh_analysis()
        print(f"\n✅ Analysis completed successfully!")
        print(f"📈 Final recommendation: {decision}")
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
