#!/usr/bin/env python3
"""Quick verification that no mock data is being used"""

import requests
import json

print("🔍 Verifying No Mock Data in Application\n")
print("="*50)

# Test 1: Check backend health
try:
    r = requests.get("http://localhost:8000/health")
    print(f"✅ Backend running on port 8000")
except:
    print(f"❌ Backend not accessible on port 8000")

# Test 2: Check frontend
try:
    r = requests.get("http://localhost:3000")
    if r.status_code == 200:
        print(f"✅ Frontend running on port 3000")
    else:
        print(f"⚠️  Frontend returned status {r.status_code}")
except:
    print(f"❌ Frontend not accessible on port 3000")

# Test 3: Check API responses for mock data
print("\n📊 Testing API Endpoints (No Mock Data):")
print("-"*40)

# Test strategy generation
try:
    r = requests.post("http://localhost:8000/api/generate-strategy", 
                      json={"prompt": "Create a simple strategy"})
    if r.status_code == 200:
        data = r.json()
        has_mock = "mock" in str(data).lower() or "getMockStrategy" in str(data)
        if not has_mock:
            print("✅ Strategy generation: No mock data detected")
        else:
            print("❌ Strategy generation: Mock data found!")
    else:
        print(f"⚠️  Strategy generation returned {r.status_code}")
except Exception as e:
    print(f"❌ Strategy generation failed: {e}")

# Test usage stats
try:
    r = requests.get("http://localhost:8000/api/user/ideas")
    if r.status_code == 200:
        data = r.json()
        # Check if returning default mock values (10 ideas, etc)
        if data.get('ideas_remaining') == 10 and 'error' not in data:
            print("⚠️  Usage stats: Might be using defaults")
        elif 'error' in data:
            print("✅ Usage stats: Returns error (no mock fallback)")
        else:
            print(f"✅ Usage stats: {data.get('ideas_remaining', 0)} ideas remaining")
except Exception as e:
    print(f"❌ Usage stats failed: {e}")

# Test indicators
try:
    r = requests.get("http://localhost:8000/api/indicators")
    if r.status_code == 200:
        data = r.json()
        indicators = data.get('indicators', [])
        print(f"✅ Indicators: {len(indicators)} available")
except Exception as e:
    print(f"❌ Indicators failed: {e}")

print("\n" + "="*50)
print("✨ Verification Complete\n")
