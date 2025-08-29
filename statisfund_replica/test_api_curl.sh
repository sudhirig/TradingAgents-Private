#!/bin/bash

# API Testing with CURL Commands
# Tests all endpoints without mock data

echo "======================================"
echo "STATISFUND PHASE 2 - CURL API TESTING"
echo "======================================"
echo ""

BASE_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -n "Testing: $description... "
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" -X $method -H "Content-Type: application/json" -d "$data" "$BASE_URL$endpoint")
    fi
    
    if [ "$response" == "200" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $response)"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $response)"
        ((TESTS_FAILED++))
    fi
}

# Function to test for mock data
test_no_mock() {
    local endpoint=$1
    local method=$2
    local data=$3
    local description=$4
    
    echo -n "Mock Check: $description... "
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s "$BASE_URL$endpoint")
    else
        response=$(curl -s -X $method -H "Content-Type: application/json" -d "$data" "$BASE_URL$endpoint")
    fi
    
    if echo "$response" | grep -qi "mock\|fake\|test_data\|getMock"; then
        echo -e "${RED}✗ MOCK DATA DETECTED${NC}"
        ((TESTS_FAILED++))
    else
        echo -e "${GREEN}✓ NO MOCK DATA${NC}"
        ((TESTS_PASSED++))
    fi
}

echo "1. HEALTH & STATUS CHECKS"
echo "-------------------------"
test_endpoint "GET" "/health" "" "Backend health check"
test_endpoint "GET" "/api/indicators" "" "TA-Lib indicators list"
test_endpoint "GET" "/api/user/ideas" "" "User ideas/usage stats"

echo ""
echo "2. STRATEGY GENERATION (NO MOCK)"
echo "--------------------------------"
test_no_mock "/api/generate-strategy" "POST" '{"prompt":"Create a simple moving average strategy"}' "Strategy generation"

# Test with real trading scenarios
echo ""
echo "3. REAL TRADING SCENARIOS"
echo "-------------------------"
test_endpoint "POST" "/api/generate-strategy" '{"prompt":"Bollinger Bands mean reversion strategy for AAPL"}' "Bollinger Bands strategy"
test_endpoint "POST" "/api/generate-strategy" '{"prompt":"RSI momentum strategy with risk management"}' "RSI momentum strategy"
test_endpoint "POST" "/api/generate-strategy" '{"prompt":"MACD crossover with trailing stop loss"}' "MACD crossover strategy"

echo ""
echo "4. ADVANCED BACKTEST WITH CEREBRO"
echo "---------------------------------"

# Generate a simple strategy first
STRATEGY_CODE='import backtrader as bt\n\nclass SimpleMA(bt.Strategy):\n    params = ((\"period\", 20),)\n    \n    def __init__(self):\n        self.sma = bt.indicators.SMA(self.data, period=self.params.period)\n    \n    def next(self):\n        if self.data.close > self.sma:\n            if not self.position:\n                self.buy()\n        else:\n            if self.position:\n                self.sell()'

# Escape the strategy for JSON
ESCAPED_STRATEGY=$(echo "$STRATEGY_CODE" | sed 's/"/\\"/g' | tr '\n' ' ')

test_endpoint "POST" "/api/advanced-backtest" "{\"code\":\"$ESCAPED_STRATEGY\",\"symbol\":\"SPY\",\"start_date\":\"2023-01-01\",\"end_date\":\"2023-12-31\",\"initial_cash\":100000}" "Advanced backtest execution"

echo ""
echo "5. TECHNICAL INDICATOR ANALYSIS"
echo "-------------------------------"
test_endpoint "POST" "/api/indicator-analysis" '{"symbol":"AAPL","indicators":["SMA","RSI","MACD"],"period":20}' "Multi-indicator analysis"
test_endpoint "POST" "/api/indicator-analysis" '{"symbol":"TSLA","indicators":["BBANDS","STOCH","ADX"],"period":14}' "Advanced indicators"

echo ""
echo "6. VALIDATE BACKTEST RESULTS"
echo "----------------------------"
echo "Checking backtest return logic..."

# Run a backtest and check results
response=$(curl -s -X POST -H "Content-Type: application/json" \
    -d "{\"code\":\"$ESCAPED_STRATEGY\",\"symbol\":\"SPY\",\"start_date\":\"2023-06-01\",\"end_date\":\"2023-12-01\",\"initial_cash\":100000}" \
    "$BASE_URL/api/advanced-backtest")

if echo "$response" | grep -q "metrics"; then
    # Extract metrics
    total_return=$(echo "$response" | grep -o '"total_return":[^,}]*' | cut -d':' -f2)
    sharpe_ratio=$(echo "$response" | grep -o '"sharpe_ratio":[^,}]*' | cut -d':' -f2)
    max_drawdown=$(echo "$response" | grep -o '"max_drawdown":[^,}]*' | cut -d':' -f2)
    
    echo -e "  Total Return: $total_return%"
    echo -e "  Sharpe Ratio: $sharpe_ratio"
    echo -e "  Max Drawdown: $max_drawdown%"
    
    # Validate returns are logical
    if (( $(echo "$total_return > -100" | bc -l) )) && (( $(echo "$total_return < 500" | bc -l) )); then
        echo -e "  ${GREEN}✓ Returns are logical${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "  ${RED}✗ Returns seem unrealistic${NC}"
        ((TESTS_FAILED++))
    fi
else
    echo -e "  ${RED}✗ No metrics found in response${NC}"
    ((TESTS_FAILED++))
fi

echo ""
echo "7. WEBSOCKET CONNECTION TEST"
echo "----------------------------"
echo "Testing WebSocket at ws://localhost:8000/ws..."

# Use Python for WebSocket test
python3 -c "
import asyncio
import websockets
import json

async def test_ws():
    try:
        async with websockets.connect('ws://localhost:8000/ws') as websocket:
            # Send a test message
            await websocket.send(json.dumps({'type': 'ping'}))
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print('✓ WebSocket connection successful')
            return True
    except Exception as e:
        print(f'✗ WebSocket failed: {e}')
        return False

asyncio.run(test_ws())
" 2>/dev/null

if [ $? -eq 0 ]; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

echo ""
echo "8. FRONTEND ACCESSIBILITY"
echo "------------------------"
frontend_status=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
if [ "$frontend_status" == "200" ]; then
    echo -e "${GREEN}✓ Frontend accessible on port 3000${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Frontend not accessible${NC}"
    ((TESTS_FAILED++))
fi

echo ""
echo "======================================"
echo "TEST SUMMARY"
echo "======================================"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL API TESTS PASSED!${NC}"
    exit 0
else
    echo -e "\n${YELLOW}⚠️ Some tests failed. Review and fix before deployment.${NC}"
    exit 1
fi
