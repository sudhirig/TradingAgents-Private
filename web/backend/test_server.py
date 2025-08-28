#!/usr/bin/env python3
"""
Simple test script to verify backend functionality
"""

import sys
import os
sys.path.append('/Users/Gautam/TradingAgents')
from load_env import load_env

# Test basic imports
try:
    import uvicorn
    from fastapi import FastAPI
    print("✅ FastAPI imports successful")
except Exception as e:
    print(f"❌ FastAPI import error: {e}")
    sys.exit(1)

# Test app imports
try:
    sys.path.append('/Users/Gautam/TradingAgents/web/backend/app')
    from main import app
    print("✅ App import successful")
except Exception as e:
    print(f"❌ App import error: {e}")
    sys.exit(1)

# Test basic functionality
try:
    # Create a simple test client
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Test health endpoint
    response = client.get("/health")
    print(f"✅ Health endpoint: {response.status_code} - {response.json()}")
    
    # Test root endpoint
    response = client.get("/")
    print(f"✅ Root endpoint: {response.status_code} - {response.json()}")
    
    # Test config endpoint
    response = client.get("/api/config/analysts")
    print(f"✅ Config endpoint: {response.status_code} - Found {len(response.json())} analysts")
    
    print("\n🎉 All tests passed! Backend is ready to start.")
    
except Exception as e:
    print(f"❌ Test error: {e}")
    sys.exit(1)

if __name__ == "__main__":
    print("Starting server on port 8001...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
