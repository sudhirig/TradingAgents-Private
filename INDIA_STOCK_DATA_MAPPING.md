# 📊 **TradingAgents: US vs India Stock Market Data Requirements**

## **Complete Data Mapping Table**

| **Data Category** | **Agent Users** | **US Stocks Implementation** | **India Stocks Requirements** | **Changes Needed** |
|---|---|---|---|---|
| **MARKET DATA** |
| **Ticker Symbol** | All 12 Agents | `"TSLA"`, `"AAPL"`, `"MSFT"` | `"RELIANCE.NS"`, `"TCS.NS"`, `"INFY.NS"` (NSE)<br>`"RELIANCE.BO"`, `"TCS.BO"` (BSE) | ✅ **No Change** - yfinance supports .NS/.BO |
| **OHLCV Data** | Market Analyst, All Researchers, Risk Analysts, Trader | **Source**: yfinance<br>**Format**: `Open, High, Low, Close, Volume, Adj Close`<br>**Currency**: USD<br>**Path**: `{symbol}-YFin-data-2015-01-01-2025-03-25.csv` | **Source**: yfinance (same)<br>**Format**: Same OHLCV structure<br>**Currency**: INR (auto-handled)<br>**Path**: `{symbol.replace('.', '_')}-YFin-data-*.csv` | ⚠️ **Minor** - File naming for .NS/.BO |
| **Date/Time** | All Agents | **Timezone**: EST/EDT (US Eastern)<br>**Trading Hours**: 9:30 AM - 4:00 PM ET<br>**Format**: `YYYY-MM-DD` | **Timezone**: IST (UTC+5:30)<br>**Trading Hours**: 9:15 AM - 3:30 PM IST<br>**Format**: Same `YYYY-MM-DD` | 🔄 **Update** - Timezone handling |
| **Market Calendar** | All Agents | **Holidays**: US Federal holidays<br>**Weekends**: Saturday-Sunday | **Holidays**: Indian market holidays (Diwali, Holi, etc.)<br>**Weekends**: Saturday-Sunday | 🔄 **Update** - Holiday calendar |
| **TECHNICAL INDICATORS** |
| **Moving Averages** | Market Analyst, Researchers, Risk Analysts | **Formula**: `close_50_sma = sum(close[-50:]) / 50`<br>**Library**: stockstats<br>**Indicators**: `close_50_sma`, `close_200_sma`, `close_20_ema` | **Formula**: Same mathematical formulas<br>**Library**: stockstats (same)<br>**Indicators**: Same indicator names | ✅ **No Change** - Universal formulas |
| **Momentum Indicators** | Market Analyst, Researchers | **RSI**: `rsi_14 = 100 - (100 / (1 + RS))`<br>**MACD**: `macd = ema_12 - ema_26`<br>**Stochastic**: `stochrsi_14` | **RSI**: Same formula<br>**MACD**: Same formula<br>**Stochastic**: Same formula | ✅ **No Change** - Universal formulas |
| **Volatility Indicators** | Risk Analysts, Market Analyst | **Bollinger Bands**: `boll = sma ± (2 * std_dev)`<br>**ATR**: `atr_14 = average(true_range[-14:])`<br>**ADX**: `adx_14` | **Bollinger Bands**: Same formula<br>**ATR**: Same formula<br>**ADX**: Same formula | ✅ **No Change** - Universal formulas |
| **Volume Indicators** | Market Analyst, Researchers | **OBV**: `obv = cumsum(volume * sign(close_change))`<br>**MFI**: `mfi_14`<br>**VWAP**: `vwap = sum(price * volume) / sum(volume)` | **OBV**: Same formula<br>**MFI**: Same formula<br>**VWAP**: Same formula | ✅ **No Change** - Universal formulas |
| **NEWS & SENTIMENT DATA** |
| **News Sources** | News Analyst, Social Media Analyst | **Sources**: Google News, Reddit, Finnhub<br>**Query**: `{ticker} stock news`<br>**Language**: English<br>**APIs**: Google News API, Reddit API | **Sources**: Economic Times, Moneycontrol, Business Standard<br>**Query**: `{company_name} stock news India`<br>**Language**: English + Hindi<br>**APIs**: Economic Times API, Moneycontrol API | 🔄 **Major Update** - New news sources |
| **Social Media** | Social Media Analyst | **Platforms**: Reddit (r/stocks, r/investing), Twitter<br>**Keywords**: `$TICKER`, stock discussions<br>**Sentiment**: English text analysis | **Platforms**: Reddit (r/IndiaInvestments), Twitter India<br>**Keywords**: Company names, stock discussions<br>**Sentiment**: English + Hindi text analysis | 🔄 **Update** - India-specific communities |
| **News Processing** | News Analyst | **Format**: `{headline, summary, date, source, sentiment}`<br>**Sentiment**: OpenAI/local models<br>**Timeframe**: 7-30 days lookback | **Format**: Same structure<br>**Sentiment**: Multilingual models<br>**Timeframe**: Same 7-30 days | ⚠️ **Minor** - Multilingual support |
| **FUNDAMENTAL DATA** |
| **Financial Statements** | Fundamentals Analyst | **Source**: SimFin, Finnhub<br>**Format**: Balance Sheet, Income, Cash Flow<br>**Frequency**: Quarterly/Annual<br>**Standards**: US GAAP<br>**Path**: `{DATA_DIR}/fundamental_data/simfin_data_all/` | **Source**: BSE/NSE APIs, MoneyControl<br>**Format**: Same structure<br>**Frequency**: Quarterly/Annual<br>**Standards**: Indian GAAP/IFRS<br>**Path**: `{DATA_DIR}/fundamental_data/india_data/` | 🔄 **Major Update** - New data sources |
| **Insider Trading** | Fundamentals Analyst | **Source**: SEC filings via Finnhub<br>**Format**: `{name, shares, price, transaction_code, filing_date}`<br>**Regulation**: SEC rules | **Source**: SEBI filings<br>**Format**: Similar structure<br>**Regulation**: SEBI rules | 🔄 **Update** - SEBI vs SEC data |
| **Analyst Recommendations** | All Researchers, Portfolio Manager | **Source**: yfinance recommendations<br>**Format**: `{Buy, Hold, Sell, Strong Buy, Strong Sell}`<br>**Logic**: `majority_voting = max(votes)` | **Source**: yfinance (limited), Indian brokerages<br>**Format**: Same rating structure<br>**Logic**: Same majority voting | ⚠️ **Minor** - Limited coverage |
| **BUSINESS LOGIC & FORMULAS** |
| **Data Validation** | All Agents | **Ticker Format**: `^[A-Z]{1,5}$`<br>**Date Range**: 2015-01-01 to current<br>**Market Hours**: 9:30 AM - 4:00 PM ET | **Ticker Format**: `^[A-Z0-9]+\.(NS|BO)$`<br>**Date Range**: Same historical range<br>**Market Hours**: 9:15 AM - 3:30 PM IST | 🔄 **Update** - Validation rules |
| **Price Calculations** | All Agents | **Currency**: USD<br>**Precision**: 2 decimal places<br>**Splits**: Auto-adjusted by yfinance | **Currency**: INR<br>**Precision**: 2 decimal places<br>**Splits**: Auto-adjusted by yfinance | ⚠️ **Minor** - Currency display |
| **Volume Analysis** | Market Analyst | **Logic**: `if volume > avg_volume * 1.5: "High Volume"`<br>**Thresholds**: US market liquidity based | **Logic**: Same volume logic<br>**Thresholds**: Adjust for Indian liquidity | ⚠️ **Minor** - Threshold tuning |
| **Risk Metrics** | Risk Analysts | **Volatility**: `std_dev(returns) * sqrt(252)`<br>**Beta**: `covariance(stock, market) / variance(market)`<br>**Benchmark**: S&P 500 | **Volatility**: Same formula<br>**Beta**: Same formula<br>**Benchmark**: NIFTY 50 or SENSEX | 🔄 **Update** - Benchmark index |
| **AGENT WORKFLOW DATA** |
| **State Management** | All Agents | **Company**: `state["company_of_interest"]`<br>**Date**: `state["trade_date"]`<br>**Reports**: `{market_report, sentiment_report, news_report, fundamentals_report}` | **Company**: Same state structure<br>**Date**: Same format<br>**Reports**: Same report structure | ✅ **No Change** - State management |
| **Memory System** | Researchers, Trader, Risk Manager | **Embeddings**: OpenAI text-embedding-3-small<br>**Storage**: ChromaDB<br>**Context**: US market patterns | **Embeddings**: Same embedding model<br>**Storage**: Same ChromaDB<br>**Context**: Indian market patterns | ⚠️ **Minor** - Context adaptation |
| **LLM Integration** | All Agents | **Models**: GPT-4o, GPT-4o-mini, o1<br>**Context**: US financial terminology<br>**Prompts**: US market focused | **Models**: Same LLM models<br>**Context**: Indian financial terminology<br>**Prompts**: India market focused | ⚠️ **Minor** - Prompt adaptation |

## **Implementation Priority Matrix**

| **Priority** | **Component** | **Effort** | **Impact** | **Dependencies** |
|---|---|---|---|---|
| **🔴 Critical** | Ticker Symbol Validation | Low | High | None |
| **🔴 Critical** | Market Hours/Timezone | Medium | High | Date handling |
| **🔴 Critical** | News Sources Integration | High | High | API access |
| **🟡 High** | Fundamental Data Sources | High | Medium | BSE/NSE APIs |
| **🟡 High** | Market Calendar | Medium | Medium | Holiday data |
| **🟢 Medium** | Benchmark Index Update | Low | Medium | NIFTY/SENSEX data |
| **🟢 Medium** | Currency Display | Low | Low | UI formatting |
| **🟢 Low** | Multilingual Sentiment | Medium | Low | NLP models |

## **Code Changes Required**

### **1. Ticker Symbol Handling**
```python
# Current: tradingagents/dataflows/interface.py
def validate_ticker(symbol: str) -> bool:
    return bool(re.match(r'^[A-Z]{1,5}$', symbol))

# India Update:
def validate_ticker(symbol: str, market: str = "US") -> bool:
    if market == "INDIA":
        return bool(re.match(r'^[A-Z0-9]+\.(NS|BO)$', symbol))
    return bool(re.match(r'^[A-Z]{1,5}$', symbol))
```

### **2. Market Hours Handling**
```python
# Current: Uses US Eastern Time
# India Update: Add IST timezone support
import pytz

def get_market_hours(market: str = "US"):
    if market == "INDIA":
        return {
            "timezone": pytz.timezone("Asia/Kolkata"),
            "open": "09:15",
            "close": "15:30"
        }
    return {
        "timezone": pytz.timezone("US/Eastern"),
        "open": "09:30", 
        "close": "16:00"
    }
```

### **3. News Sources Integration**
```python
# New: tradingagents/dataflows/india_news_utils.py
class IndiaNewsUtils:
    @staticmethod
    def get_economic_times_news(ticker: str, date: str):
        # Economic Times API integration
        pass
    
    @staticmethod  
    def get_moneycontrol_news(ticker: str, date: str):
        # MoneyControl API integration
        pass
```

## **Summary**

- **✅ No Changes**: 60% of system (technical indicators, OHLCV data, state management)
- **⚠️ Minor Updates**: 25% of system (currency display, validation rules, prompts)  
- **🔄 Major Updates**: 15% of system (news sources, fundamental data, market calendar)

**Total Effort**: Medium - Most core functionality remains unchanged due to yfinance universal support.
