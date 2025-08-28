#!/usr/bin/env python3
"""
Simple backend test without analysis functionality
"""

import sys
import os
sys.path.append('/Users/Gautam/TradingAgents')
from load_env import load_env

# Test basic imports only
try:
    sys.path.append('/Users/Gautam/TradingAgents/web/backend/app')
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    # Test health endpoint
    response = client.get("/health")
    print(f"Health: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Health: {response.json()}")
    else:
        print(f"❌ Health error: {response.text}")
    
    # Test root endpoint
    response = client.get("/")
    print(f"Root: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Root: {response.json()}")
    else:
        print(f"❌ Root error: {response.text}")
    
    # Test config endpoints
    response = client.get("/api/config/analysts")
    print(f"Analysts: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Analysts: Found {len(response.json())} analysts")
    else:
        print(f"❌ Analysts error: {response.text}")
    
    response = client.get("/api/config/llm-providers")
    print(f"LLM Providers: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ LLM Providers: Found {len(response.json())} providers")
    else:
        print(f"❌ LLM Providers error: {response.text}")
    
    response = client.get("/api/config/")
    print(f"Full Config: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Full Config: OK")
    else:
        print(f"❌ Full Config error: {response.text}")
    
    print("\n🎉 Backend API endpoints working correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
