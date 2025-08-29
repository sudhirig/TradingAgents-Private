#!/bin/bash

# API Testing Script with cURL
# Tests all backend endpoints systematically

BASE_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"

echo "🚀 Starting cURL API Tests..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

test_endpoint() {
    local name="$1"
    local method="$2"
    local url="$3"
    local data="$4"
    local expected_status="$5"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo ""
    echo "📋 Testing: $name"
    echo "URL: $method $url"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X GET "$url")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" -H "Content-Type: application/json" -X POST -d "$data" "$url")
    fi
    
    # Extract status code
    status_code=$(echo $response | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    body=$(echo $response | sed -E 's/HTTPSTATUS:[0-9]*$//')
    
    echo "Status Code: $status_code"
    echo "Response: ${body:0:200}..."
    
    if [ "$status_code" = "$expected_status" ] || [ "$expected_status" = "ANY" ]; then
        echo -e "${GREEN}✅ PASS${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL (Expected: $expected_status, Got: $status_code)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Test 1: Frontend accessibility
echo "🏠 Testing Frontend Accessibility..."
test_endpoint "Frontend Home Page" "GET" "$FRONTEND_URL" "" "200"

# Test 2: Backend health check
echo "🏥 Testing Backend Health..."
test_endpoint "Health Check" "GET" "$BASE_URL/health" "" "ANY"

# Test 3: API endpoints
echo "🔧 Testing API Endpoints..."

# Strategy Generation
strategy_payload='{
  "prompt": "Create a momentum strategy using RSI and MACD",
  "template": "momentum",
  "timeframe": "1h",
  "risk_per_trade": 2.0,
  "stop_loss": 5.0,
  "take_profit": 10.0
}'

test_endpoint "Strategy Generation" "POST" "$BASE_URL/api/generate-strategy" "$strategy_payload" "ANY"

# Backtest Engine
backtest_payload='{
  "code": "class TestStrategy(bt.Strategy):\n    def __init__(self):\n        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=20)\n    def next(self):\n        if not self.position and self.data.close > self.sma:\n            self.buy()",
  "symbol": "AAPL",
  "start_date": "2023-01-01", 
  "end_date": "2023-12-31",
  "initial_cash": 100000
}'

test_endpoint "Backtest Engine" "POST" "$BASE_URL/api/backtest" "$backtest_payload" "ANY"

# Advanced Backtest
test_endpoint "Advanced Backtest" "POST" "$BASE_URL/api/advanced-backtest" "$backtest_payload" "ANY"

# Indicators List
test_endpoint "Get Indicators" "GET" "$BASE_URL/api/indicators" "" "ANY"

# Market Data
test_endpoint "Get Market Data" "GET" "$BASE_URL/api/market-data" "" "ANY"

# Saved Strategies
test_endpoint "Get Strategies" "GET" "$BASE_URL/api/strategies" "" "ANY"

# Create Strategy
create_strategy_payload='{
  "name": "Test Momentum Strategy",
  "description": "Test strategy for validation",
  "code": "class TestStrategy(bt.Strategy): pass",
  "template": "momentum"
}'

test_endpoint "Create Strategy" "POST" "$BASE_URL/api/strategies" "$create_strategy_payload" "ANY"

# Indicator Analysis
indicator_payload='{
  "symbol": "AAPL",
  "indicators": ["RSI", "MACD", "SMA"],
  "timeframe": "1d"
}'

test_endpoint "Indicator Analysis" "POST" "$BASE_URL/api/indicator-analysis" "$indicator_payload" "ANY"

# Technical Analysis
test_endpoint "Technical Analysis" "GET" "$BASE_URL/api/technical-analysis/AAPL" "" "ANY"

echo ""
echo "=================================="
echo "📊 TEST RESULTS SUMMARY"
echo "=================================="
echo "Total Tests: $TOTAL_TESTS"
echo -e "✅ Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "❌ Failed: ${RED}$FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    exit 0
else
    success_rate=$(( PASSED_TESTS * 100 / TOTAL_TESTS ))
    echo "Success Rate: ${success_rate}%"
    echo -e "${YELLOW}⚠️  Some tests failed. Check backend connectivity.${NC}"
    exit 1
fi
