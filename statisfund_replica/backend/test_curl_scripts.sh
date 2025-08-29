#!/bin/bash
# Comprehensive curl testing scripts for Statis Fund Replica API
# Tests all endpoints with real stock data and edge cases

BASE_URL="http://localhost:8000"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="curl_test_results_${TIMESTAMP}.log"

echo "🚀 Starting curl API tests at $(date)" | tee $LOG_FILE
echo "📍 Testing against: $BASE_URL" | tee -a $LOG_FILE
echo "=" | tee -a $LOG_FILE

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_endpoint() {
    local test_name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="$5"
    
    echo -e "\n🧪 Testing: ${YELLOW}$test_name${NC}" | tee -a $LOG_FILE
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BASE_URL$endpoint")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "✅ ${GREEN}PASS${NC} - HTTP $http_code" | tee -a $LOG_FILE
        echo "Response: $(echo "$body" | jq -c . 2>/dev/null || echo "$body" | head -c 100)..." | tee -a $LOG_FILE
    else
        echo -e "❌ ${RED}FAIL${NC} - Expected $expected_status, got $http_code" | tee -a $LOG_FILE
        echo "Response: $body" | tee -a $LOG_FILE
    fi
}

# Test 1: Health Check
test_endpoint "Health Check" "GET" "/health" "" "200"

# Test 2: CORS Preflight
echo -e "\n🌐 Testing CORS Preflight" | tee -a $LOG_FILE
curl -s -i -X OPTIONS "$BASE_URL/api/generate-strategy" \
    -H "Origin: http://localhost:3000" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Content-Type" | tee -a $LOG_FILE

# Test 3: Strategy Generation
test_endpoint "Strategy Generation - AAPL" "POST" "/api/generate-strategy" '{
    "description": "Simple moving average crossover strategy for AAPL with RSI filter",
    "symbols": ["AAPL"],
    "start_date": "2023-01-01",
    "end_date": "2023-12-31"
}' "200"

test_endpoint "Strategy Generation - TSLA" "POST" "/api/generate-strategy" '{
    "description": "Momentum strategy using MACD and Bollinger Bands for TSLA",
    "symbols": ["TSLA"],
    "start_date": "2023-01-01", 
    "end_date": "2023-12-31"
}' "200"

test_endpoint "Strategy Generation - MSFT" "POST" "/api/generate-strategy" '{
    "description": "Mean reversion strategy with volume analysis for MSFT",
    "symbols": ["MSFT"],
    "start_date": "2023-01-01",
    "end_date": "2023-12-31"
}' "200"

# Test 4: Basic Backtest with sample strategy
SAMPLE_STRATEGY='import backtrader as bt

class TestStrategy(bt.Strategy):
    params = (("period", 20),)
    
    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.params.period)
        self.crossover = bt.indicators.CrossOver(self.data.close, self.sma)
    
    def next(self):
        if not self.position and self.crossover > 0:
            self.buy(size=100)
        elif self.position and self.crossover < 0:
            self.sell(size=self.position.size)'

test_endpoint "Basic Backtest - AAPL" "POST" "/api/backtest" "{
    \"code\": \"$SAMPLE_STRATEGY\",
    \"symbol\": \"AAPL\",
    \"start_date\": \"2023-01-01\",
    \"end_date\": \"2023-06-30\",
    \"initial_cash\": 10000.0
}" "200"

test_endpoint "Basic Backtest - TSLA" "POST" "/api/backtest" "{
    \"code\": \"$SAMPLE_STRATEGY\",
    \"symbol\": \"TSLA\", 
    \"start_date\": \"2023-01-01\",
    \"end_date\": \"2023-06-30\",
    \"initial_cash\": 10000.0
}" "200"

# Test 5: Advanced Backtest
test_endpoint "Advanced Backtest - AAPL" "POST" "/api/advanced-backtest" "{
    \"code\": \"$SAMPLE_STRATEGY\",
    \"symbol\": \"AAPL\",
    \"start_date\": \"2023-01-01\",
    \"end_date\": \"2023-06-30\",
    \"initial_cash\": 10000,
    \"commission\": 0.001,
    \"order_type\": \"market\",
    \"position_sizer\": \"percent\",
    \"position_size\": 100
}" "200"

# Test 6: Fenced Code Handling
FENCED_STRATEGY='```python
import backtrader as bt

class FencedStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=15)
    
    def next(self):
        if not self.position and self.data.close[0] > self.sma[0]:
            self.buy(size=50)
        elif self.position and self.data.close[0] < self.sma[0]:
            self.sell(size=self.position.size)
```'

test_endpoint "Fenced Code - Basic Backtest" "POST" "/api/backtest" "{
    \"code\": \"$FENCED_STRATEGY\",
    \"symbol\": \"AAPL\",
    \"start_date\": \"2023-01-01\",
    \"end_date\": \"2023-03-31\",
    \"initial_cash\": 10000.0
}" "200"

test_endpoint "Fenced Code - Advanced Backtest" "POST" "/api/advanced-backtest" "{
    \"code\": \"$FENCED_STRATEGY\",
    \"symbol\": \"AAPL\",
    \"start_date\": \"2023-01-01\",
    \"end_date\": \"2023-03-31\",
    \"initial_cash\": 10000,
    \"commission\": 0.001
}" "200"

# Test 7: Error Cases
test_endpoint "Error - Invalid Symbol" "POST" "/api/backtest" "{
    \"code\": \"$SAMPLE_STRATEGY\",
    \"symbol\": \"INVALID_XYZ\",
    \"start_date\": \"2023-01-01\",
    \"end_date\": \"2023-02-01\",
    \"initial_cash\": 10000
}" "200"

test_endpoint "Error - Malformed Code" "POST" "/api/backtest" '{
    "code": "this is not valid python code!!!",
    "symbol": "AAPL",
    "start_date": "2023-01-01", 
    "end_date": "2023-02-01",
    "initial_cash": 10000
}' "200"

test_endpoint "Error - Missing Description" "POST" "/api/generate-strategy" '{
    "symbols": ["AAPL"]
}' "422"

# Test 8: Supporting Endpoints
test_endpoint "Indicators List" "GET" "/api/indicators" "" "200"
test_endpoint "Advanced Indicators" "GET" "/api/indicators/advanced" "" "200"
test_endpoint "Market Data" "GET" "/api/market-data" "" "200"
test_endpoint "Order Types" "GET" "/api/orders/types" "" "200"
test_endpoint "Supported Assets" "GET" "/api/assets/supported" "" "200"
test_endpoint "Trading Brokers" "GET" "/api/trading/brokers" "" "200"

# Test 9: Indicator Analysis
test_endpoint "Indicator Analysis - AAPL" "POST" "/api/indicator-analysis" '{
    "symbol": "AAPL",
    "start_date": "2023-01-01",
    "end_date": "2023-03-31"
}' "200"

echo -e "\n🏁 curl tests completed at $(date)" | tee -a $LOG_FILE
echo "📄 Results saved to: $LOG_FILE" | tee -a $LOG_FILE
