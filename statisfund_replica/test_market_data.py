#!/usr/bin/env python3
"""
Test market data connectivity directly
"""
import yfinance as yf
import requests
from datetime import datetime, timedelta
import time

def test_yahoo_finance():
    """Test Yahoo Finance API directly"""
    print("\n=== Testing Yahoo Finance ===")
    symbols = ['SPY', 'AAPL', 'MSFT', 'TSLA']
    
    for symbol in symbols:
        try:
            print(f"\nTesting {symbol}...")
            ticker = yf.Ticker(symbol)
            
            # Test history method
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            data = ticker.history(start=start_date, end=end_date)
            
            if not data.empty:
                print(f"✅ {symbol}: Retrieved {len(data)} days of data")
                print(f"   Latest close: ${data['Close'].iloc[-1]:.2f}")
                print(f"   Date range: {data.index[0].date()} to {data.index[-1].date()}")
            else:
                print(f"❌ {symbol}: No data received")
                
        except Exception as e:
            print(f"❌ {symbol}: Error - {str(e)}")
            
def test_alpha_vantage():
    """Test Alpha Vantage API directly"""
    print("\n=== Testing Alpha Vantage ===")
    
    api_key = "3XRPPKB5I0HZ6OM1"  # Hardcoded key from backend
    symbol = "SPY"
    
    try:
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'Time Series (Daily)' in data:
            days = list(data['Time Series (Daily)'].keys())
            print(f"✅ Alpha Vantage: Retrieved {len(days)} days for {symbol}")
            latest_day = days[0]
            latest_close = data['Time Series (Daily)'][latest_day]['4. close']
            print(f"   Latest close: ${latest_close}")
            print(f"   Latest date: {latest_day}")
        elif 'Note' in data:
            print(f"⚠️  Alpha Vantage: API limit reached - {data['Note']}")
        elif 'Error Message' in data:
            print(f"❌ Alpha Vantage: {data['Error Message']}")
        else:
            print(f"❌ Alpha Vantage: Unexpected response")
            print(f"   Response: {str(data)[:200]}")
            
    except Exception as e:
        print(f"❌ Alpha Vantage Error: {str(e)}")

def test_backend_data_endpoint():
    """Test backend's ability to fetch data"""
    print("\n=== Testing Backend Data Fetching ===")
    
    # Test through indicator analysis endpoint
    try:
        response = requests.post(
            "http://localhost:8000/api/indicator-analysis",
            json={
                "symbol": "SPY",
                "indicators": ["SMA", "RSI"],
                "start_date": "2024-01-01",
                "end_date": "2024-12-01"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Backend can fetch market data")
            else:
                print(f"❌ Backend data fetch failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Backend returned status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Backend test failed: {str(e)}")

def test_direct_download():
    """Test yfinance download function directly"""
    print("\n=== Testing Direct yfinance Download ===")
    
    try:
        data = yf.download('SPY', start='2024-01-01', end='2024-02-01', progress=False)
        
        if not data.empty:
            print(f"✅ Direct download successful")
            print(f"   Retrieved {len(data)} days of data")
            print(f"   Columns: {list(data.columns)}")
        else:
            print("❌ Direct download returned empty data")
            
    except Exception as e:
        print(f"❌ Direct download failed: {str(e)}")

def check_network():
    """Check basic network connectivity"""
    print("\n=== Testing Network Connectivity ===")
    
    sites = [
        ("Google", "https://www.google.com"),
        ("Yahoo Finance", "https://finance.yahoo.com"),
        ("Alpha Vantage", "https://www.alphavantage.co"),
    ]
    
    for name, url in sites:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {name}: Reachable (Status {response.status_code})")
        except Exception as e:
            print(f"❌ {name}: Not reachable - {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("MARKET DATA CONNECTIVITY TEST")
    print("=" * 60)
    
    check_network()
    test_yahoo_finance()
    test_direct_download()
    test_alpha_vantage()
    test_backend_data_endpoint()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
