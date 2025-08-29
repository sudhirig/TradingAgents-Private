#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Trading Platform Microservices...${NC}"

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}⚠️  Port $port is already in use${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Port $port is available${NC}"
        return 0
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local port=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}⏳ Waiting for $service_name to start on port $port...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:$port/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is ready on port $port${NC}"
            return 0
        fi
        echo -e "${YELLOW}⏳ Attempt $attempt/$max_attempts - $service_name not ready yet...${NC}"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ $service_name failed to start on port $port${NC}"
    return 1
}

# Install Python dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi

# Install Node.js dependencies for both frontends
echo -e "${BLUE}📦 Installing Node.js dependencies...${NC}"

# Statis Fund Frontend
if [ -d "statisfund_replica/frontend" ]; then
    echo -e "${BLUE}📦 Installing Statis Fund frontend dependencies...${NC}"
    cd statisfund_replica/frontend
    npm install
    cd ../..
else
    echo -e "${YELLOW}⚠️  Statis Fund frontend directory not found${NC}"
fi

# TradingAgents Frontend
if [ -d "web/frontend" ]; then
    echo -e "${BLUE}📦 Installing TradingAgents frontend dependencies...${NC}"
    cd web/frontend
    npm install
    cd ../..
else
    echo -e "${YELLOW}⚠️  TradingAgents frontend directory not found${NC}"
fi

# Check ports availability
# Note: In Replit, ports are managed by the platform, so we don't need to check availability
echo -e "${BLUE}📡 Replit will automatically map internal ports to external URLs${NC}"

# Create logs directory
mkdir -p logs

# Start services in background
echo -e "${BLUE}🚀 Starting backend services...${NC}"

# Start Statis Fund Backend (Port 8000 -> External 80)
if [ -f "statisfund_replica/backend/main.py" ]; then
    echo -e "${BLUE}🚀 Starting Statis Fund Backend on internal port 8000...${NC}"
    cd statisfund_replica/backend
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../../logs/statisfund_backend.log 2>&1 &
    STATISFUND_BACKEND_PID=$!
    cd ../..
    echo -e "${GREEN}✅ Statis Fund Backend started (PID: $STATISFUND_BACKEND_PID)${NC}"
else
    echo -e "${RED}❌ Statis Fund backend not found${NC}"
fi

# Start TradingAgents Backend (Port 8001 -> External 8001)
if [ -f "web/backend/main.py" ]; then
    echo -e "${BLUE}🚀 Starting TradingAgents Backend on internal port 8001...${NC}"
    cd web/backend
    python -m uvicorn main:app --host 0.0.0.0 --port 8001 > ../../logs/tradingagents_backend.log 2>&1 &
    TRADINGAGENTS_BACKEND_PID=$!
    cd ../..
    echo -e "${GREEN}✅ TradingAgents Backend started (PID: $TRADINGAGENTS_BACKEND_PID)${NC}"
else
    echo -e "${RED}❌ TradingAgents backend not found${NC}"
fi

# Wait for backends to be ready
sleep 5

# Start frontend services
echo -e "${BLUE}🚀 Starting frontend services...${NC}"

# Start Statis Fund Frontend (Port 3000 -> External 3000)
if [ -d "statisfund_replica/frontend" ]; then
    echo -e "${BLUE}🚀 Starting Statis Fund Frontend on internal port 3000...${NC}"
    cd statisfund_replica/frontend
    # Point to internal backend port, Replit will handle external mapping
    REACT_APP_API_URL=/api npm start -- --host 0.0.0.0 --port 3000 > ../../logs/statisfund_frontend.log 2>&1 &
    STATISFUND_FRONTEND_PID=$!
    cd ../..
    echo -e "${GREEN}✅ Statis Fund Frontend started (PID: $STATISFUND_FRONTEND_PID)${NC}"
else
    echo -e "${RED}❌ Statis Fund frontend not found${NC}"
fi

# Start TradingAgents Frontend (Port 3001 -> External 3001)
if [ -d "web/frontend" ]; then
    echo -e "${BLUE}🚀 Starting TradingAgents Frontend on internal port 3001...${NC}"
    cd web/frontend
    # Use relative path for API calls within Replit
    VITE_API_URL=/api npm run dev -- --host 0.0.0.0 --port 3001 > ../../logs/tradingagents_frontend.log 2>&1 &
    TRADINGAGENTS_FRONTEND_PID=$!
    cd ../..
    echo -e "${GREEN}✅ TradingAgents Frontend started (PID: $TRADINGAGENTS_FRONTEND_PID)${NC}"
else
    echo -e "${RED}❌ TradingAgents frontend not found${NC}"
fi

# Save PIDs for cleanup
echo "$STATISFUND_BACKEND_PID" > logs/statisfund_backend.pid
echo "$TRADINGAGENTS_BACKEND_PID" > logs/tradingagents_backend.pid
echo "$STATISFUND_FRONTEND_PID" > logs/statisfund_frontend.pid
echo "$TRADINGAGENTS_FRONTEND_PID" > logs/tradingagents_frontend.pid

# Display service status
echo -e "${GREEN}🎉 All services started successfully!${NC}"
echo -e "${BLUE}📊 Replit Service URLs (External Access):${NC}"
echo -e "${GREEN}  • Statis Fund Backend:    https://[repl-name]--[username].repl.co (port 80)${NC}"
echo -e "${GREEN}  • TradingAgents Backend:  https://[repl-name]--[username].repl.co:8001${NC}"
echo -e "${GREEN}  • Statis Fund Frontend:   https://[repl-name]--[username].repl.co:3000${NC}"
echo -e "${GREEN}  • TradingAgents Frontend: https://[repl-name]--[username].repl.co:3001${NC}"
echo -e "${BLUE}📚 API Documentation:${NC}"
echo -e "${GREEN}  • Statis Fund API:        https://[repl-name]--[username].repl.co/docs${NC}"
echo -e "${GREEN}  • TradingAgents API:      https://[repl-name]--[username].repl.co:8001/docs${NC}"
echo -e "${YELLOW}💡 Replace [repl-name] and [username] with your actual Replit details${NC}"

# Monitor services
echo -e "${BLUE}🔍 Monitoring services... (Press Ctrl+C to stop all services)${NC}"

# Trap Ctrl+C to cleanup
trap 'echo -e "${YELLOW}🛑 Stopping all services..."; kill $STATISFUND_BACKEND_PID $TRADINGAGENTS_BACKEND_PID $STATISFUND_FRONTEND_PID $TRADINGAGENTS_FRONTEND_PID 2>/dev/null; exit 0' INT

# Keep script running
while true; do
    sleep 1
done
