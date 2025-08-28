#!/bin/bash
"""
Master Test Runner for TradingAgents Web Application
Executes comprehensive testing suite with proper environment setup
"""

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 TradingAgents Comprehensive Test Suite${NC}"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "comprehensive_test_suite.py" ]; then
    echo -e "${RED}❌ Error: Must run from web/tests directory${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}🔧 Setting up environment...${NC}"
cd ../../
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
else
    echo -e "${RED}❌ Virtual environment not found${NC}"
    exit 1
fi

# Return to tests directory
cd web/tests

# Check if backend is running
echo -e "${YELLOW}🔍 Checking backend server...${NC}"
if curl -s http://localhost:8001/health > /dev/null; then
    echo -e "${GREEN}✅ Backend server is running${NC}"
else
    echo -e "${YELLOW}⚠️  Backend server not detected, starting minimal server...${NC}"
    cd ../backend
    python3 minimal_server.py &
    BACKEND_PID=$!
    sleep 3
    cd ../tests
    
    if curl -s http://localhost:8001/health > /dev/null; then
        echo -e "${GREEN}✅ Minimal backend server started${NC}"
    else
        echo -e "${RED}❌ Failed to start backend server${NC}"
        exit 1
    fi
fi

# Check if frontend is running
echo -e "${YELLOW}🔍 Checking frontend server...${NC}"
if curl -s http://localhost:5173 > /dev/null; then
    echo -e "${GREEN}✅ Frontend server is running${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend server not detected, starting...${NC}"
    cd ../frontend
    npm run dev &
    FRONTEND_PID=$!
    sleep 5
    cd ../tests
    
    if curl -s http://localhost:5173 > /dev/null; then
        echo -e "${GREEN}✅ Frontend server started${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend server may not be ready${NC}"
    fi
fi

# Install test dependencies if needed
echo -e "${YELLOW}📦 Installing test dependencies...${NC}"
pip install -q requests selenium websocket-client 2>/dev/null || true

# Run tests in sequence
echo -e "\n${BLUE}🚀 Starting Test Execution${NC}"
echo "=================================="

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 1. Backend API Tests
echo -e "\n${BLUE}1️⃣  Backend API Tests${NC}"
echo "------------------------"
if python3 backend_api_tests.py; then
    echo -e "${GREEN}✅ Backend API tests passed${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ Backend API tests failed${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# 2. Frontend UI Tests
echo -e "\n${BLUE}2️⃣  Frontend UI Tests${NC}"
echo "----------------------"
if python3 frontend_ui_tests.py; then
    echo -e "${GREEN}✅ Frontend UI tests passed${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ Frontend UI tests failed${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# 3. Comprehensive Integration Tests
echo -e "\n${BLUE}3️⃣  Integration Tests${NC}"
echo "----------------------"
if python3 comprehensive_test_suite.py; then
    echo -e "${GREEN}✅ Integration tests passed${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ Integration tests failed${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# 4. Manual Frontend Verification
echo -e "\n${BLUE}4️⃣  Manual Frontend Verification${NC}"
echo "-----------------------------------"
echo -e "${YELLOW}🔍 Performing human-like UI verification...${NC}"

# Check if frontend is accessible
if curl -s http://localhost:5173 | grep -q "TradingAgents"; then
    echo -e "${GREEN}✅ Frontend page loads with correct title${NC}"
    
    # Check for configuration elements
    FRONTEND_HTML=$(curl -s http://localhost:5173)
    
    CONFIG_ELEMENTS=(
        "Ticker Symbol"
        "Analysis Date"
        "Select Analysts"
        "Research Depth"
        "LLM Provider"
        "Start.*Analysis"
    )
    
    FOUND_ELEMENTS=0
    for element in "${CONFIG_ELEMENTS[@]}"; do
        if echo "$FRONTEND_HTML" | grep -q "$element"; then
            echo -e "${GREEN}  ✓ Found: $element${NC}"
            FOUND_ELEMENTS=$((FOUND_ELEMENTS + 1))
        else
            echo -e "${RED}  ✗ Missing: $element${NC}"
        fi
    done
    
    if [ $FOUND_ELEMENTS -eq ${#CONFIG_ELEMENTS[@]} ]; then
        echo -e "${GREEN}✅ All UI elements present${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ Missing UI elements ($FOUND_ELEMENTS/${#CONFIG_ELEMENTS[@]} found)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
else
    echo -e "${RED}❌ Frontend not accessible or missing content${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# 5. Business Logic Validation
echo -e "\n${BLUE}5️⃣  Business Logic Validation${NC}"
echo "-------------------------------"
echo -e "${YELLOW}🧠 Testing business logic and common sense scenarios...${NC}"

# Test API validation
echo -e "${YELLOW}Testing API validation...${NC}"
VALIDATION_TESTS=0
VALIDATION_PASSED=0

# Test empty ticker
if curl -s -X POST http://localhost:8001/api/analysis/start \
   -H "Content-Type: application/json" \
   -d '{"ticker":"","analysis_date":"2025-08-28"}' | grep -q "422"; then
    echo -e "${GREEN}  ✓ Empty ticker correctly rejected${NC}"
    VALIDATION_PASSED=$((VALIDATION_PASSED + 1))
else
    echo -e "${RED}  ✗ Empty ticker not properly validated${NC}"
fi
VALIDATION_TESTS=$((VALIDATION_TESTS + 1))

# Test invalid analyst
if curl -s -X POST http://localhost:8001/api/analysis/start \
   -H "Content-Type: application/json" \
   -d '{"ticker":"AAPL","analysts":["Invalid Analyst"]}' | grep -q "422"; then
    echo -e "${GREEN}  ✓ Invalid analyst correctly rejected${NC}"
    VALIDATION_PASSED=$((VALIDATION_PASSED + 1))
else
    echo -e "${RED}  ✗ Invalid analyst not properly validated${NC}"
fi
VALIDATION_TESTS=$((VALIDATION_TESTS + 1))

# Test valid request
if curl -s -X POST http://localhost:8001/api/analysis/start \
   -H "Content-Type: application/json" \
   -d '{"ticker":"AAPL","analysis_date":"2025-08-28","analysts":["Market Analyst"]}' | grep -q "session_id"; then
    echo -e "${GREEN}  ✓ Valid request accepted${NC}"
    VALIDATION_PASSED=$((VALIDATION_PASSED + 1))
else
    echo -e "${RED}  ✗ Valid request rejected${NC}"
fi
VALIDATION_TESTS=$((VALIDATION_TESTS + 1))

if [ $VALIDATION_PASSED -eq $VALIDATION_TESTS ]; then
    echo -e "${GREEN}✅ Business logic validation passed${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ Business logic validation failed ($VALIDATION_PASSED/$VALIDATION_TESTS)${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Generate final report
echo -e "\n${BLUE}📊 FINAL TEST REPORT${NC}"
echo "=================================="
echo -e "Total Test Suites: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS ✅${NC}"
echo -e "${RED}Failed: $FAILED_TESTS ❌${NC}"

SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
echo -e "Success Rate: ${SUCCESS_RATE}%"

# Create detailed report
REPORT_FILE="test_execution_report.json"
cat > $REPORT_FILE << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "total_suites": $TOTAL_TESTS,
  "passed": $PASSED_TESTS,
  "failed": $FAILED_TESTS,
  "success_rate": $SUCCESS_RATE,
  "environment": {
    "backend_url": "http://localhost:8001",
    "frontend_url": "http://localhost:5173",
    "python_version": "$(python3 --version)",
    "platform": "$(uname -s)"
  },
  "test_suites": [
    {"name": "Backend API Tests", "status": "$([ $PASSED_TESTS -ge 1 ] && echo 'PASS' || echo 'FAIL')"},
    {"name": "Frontend UI Tests", "status": "$([ $PASSED_TESTS -ge 2 ] && echo 'PASS' || echo 'FAIL')"},
    {"name": "Integration Tests", "status": "$([ $PASSED_TESTS -ge 3 ] && echo 'PASS' || echo 'FAIL')"},
    {"name": "Manual Verification", "status": "$([ $PASSED_TESTS -ge 4 ] && echo 'PASS' || echo 'FAIL')"},
    {"name": "Business Logic", "status": "$([ $PASSED_TESTS -ge 5 ] && echo 'PASS' || echo 'FAIL')"}
  ]
}
EOF

echo -e "\n📄 Detailed report saved to: ${REPORT_FILE}"

# Cleanup background processes if we started them
if [ ! -z "$BACKEND_PID" ]; then
    kill $BACKEND_PID 2>/dev/null || true
    echo -e "${YELLOW}🧹 Stopped backend server${NC}"
fi

if [ ! -z "$FRONTEND_PID" ]; then
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${YELLOW}🧹 Stopped frontend server${NC}"
fi

# Exit with appropriate code
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED! Ready for deployment.${NC}"
    exit 0
else
    echo -e "\n${RED}💥 SOME TESTS FAILED! Review issues before deployment.${NC}"
    exit 1
fi
