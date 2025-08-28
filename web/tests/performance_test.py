#!/usr/bin/env python3
"""
Performance Test - Quick load testing for TradingAgents Web App
"""

import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any

async def test_api_performance(concurrent_requests: int = 20) -> Dict[str, Any]:
    """Test API performance with concurrent requests"""
    print(f"🔥 Testing API Performance ({concurrent_requests} concurrent requests)...")
    
    async def make_request(session: aiohttp.ClientSession, url: str) -> float:
        start_time = time.time()
        try:
            async with session.get(url) as response:
                await response.text()
                return time.time() - start_time
        except Exception:
            return -1
    
    urls = [
        "http://localhost:8003/health",
        "http://localhost:8003/api/config/analysts",
        "http://localhost:8003/api/config/llm-providers",
    ]
    
    results = {}
    
    async with aiohttp.ClientSession() as session:
        for url in urls:
            print(f"   Testing {url}...")
            tasks = [make_request(session, url) for _ in range(concurrent_requests)]
            response_times = await asyncio.gather(*tasks)
            
            # Filter out failed requests
            successful_times = [t for t in response_times if t > 0]
            failed_count = len([t for t in response_times if t < 0])
            
            if successful_times:
                results[url] = {
                    'total_requests': concurrent_requests,
                    'successful_requests': len(successful_times),
                    'failed_requests': failed_count,
                    'avg_response_time': statistics.mean(successful_times),
                    'min_response_time': min(successful_times),
                    'max_response_time': max(successful_times),
                    'success_rate': len(successful_times) / concurrent_requests * 100
                }
            else:
                results[url] = {
                    'total_requests': concurrent_requests,
                    'successful_requests': 0,
                    'failed_requests': failed_count,
                    'success_rate': 0
                }
    
    return results

async def test_websocket_performance(concurrent_connections: int = 10) -> Dict[str, Any]:
    """Test WebSocket performance with concurrent connections"""
    print(f"🔌 Testing WebSocket Performance ({concurrent_connections} concurrent connections)...")
    
    async def websocket_client(client_id: int) -> Dict[str, Any]:
        import websockets
        session_id = f"perf-test-{client_id}-{int(time.time())}"
        ws_url = f"ws://localhost:8003/ws/{session_id}"
        
        result = {
            'client_id': client_id,
            'connected': False,
            'messages_received': 0,
            'connection_time': 0,
            'error': None
        }
        
        start_time = time.time()
        try:
            async with websockets.connect(ws_url) as websocket:
                result['connected'] = True
                result['connection_time'] = time.time() - start_time
                
                # Listen for 3 seconds
                end_time = start_time + 3
                while time.time() < end_time:
                    try:
                        await asyncio.wait_for(websocket.recv(), timeout=0.5)
                        result['messages_received'] += 1
                    except asyncio.TimeoutError:
                        continue
                        
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    tasks = [websocket_client(i) for i in range(concurrent_connections)]
    connection_results = await asyncio.gather(*tasks)
    
    successful_connections = [r for r in connection_results if r['connected']]
    
    return {
        'total_connections': concurrent_connections,
        'successful_connections': len(successful_connections),
        'failed_connections': concurrent_connections - len(successful_connections),
        'success_rate': len(successful_connections) / concurrent_connections * 100,
        'avg_connection_time': statistics.mean([r['connection_time'] for r in successful_connections]) if successful_connections else 0,
        'total_messages': sum(r['messages_received'] for r in successful_connections)
    }

def print_performance_results(api_results: Dict[str, Any], ws_results: Dict[str, Any]):
    """Print performance test results"""
    print("\n" + "="*70)
    print("🔥 PERFORMANCE TEST RESULTS")
    print("="*70)
    
    print("📊 API Performance:")
    for url, result in api_results.items():
        endpoint = url.split('/')[-1] or url.split('/')[-2]
        print(f"   {endpoint}:")
        print(f"      Success Rate: {result['success_rate']:.1f}%")
        if result['successful_requests'] > 0:
            print(f"      Avg Response: {result['avg_response_time']*1000:.1f}ms")
            print(f"      Min/Max: {result['min_response_time']*1000:.1f}ms / {result['max_response_time']*1000:.1f}ms")
    
    print(f"\n🔌 WebSocket Performance:")
    print(f"   Success Rate: {ws_results['success_rate']:.1f}%")
    print(f"   Avg Connection Time: {ws_results['avg_connection_time']*1000:.1f}ms")
    print(f"   Total Messages: {ws_results['total_messages']}")
    
    # Overall assessment
    api_success = all(r['success_rate'] > 90 for r in api_results.values())
    ws_success = ws_results['success_rate'] > 90
    overall_success = api_success and ws_success
    
    print(f"\n🎯 Performance Grade: {'✅ EXCELLENT' if overall_success else '⚠️ NEEDS ATTENTION'}")
    print("="*70)
    
    return overall_success

async def main():
    """Main performance test execution"""
    print("🚀 Starting Performance Tests...")
    print("="*50)
    
    # Test API performance
    api_results = await test_api_performance(concurrent_requests=20)
    
    # Test WebSocket performance  
    ws_results = await test_websocket_performance(concurrent_connections=10)
    
    # Print results
    success = print_performance_results(api_results, ws_results)
    
    # Save results
    results = {
        'api_performance': api_results,
        'websocket_performance': ws_results,
        'overall_success': success,
        'timestamp': time.time()
    }
    
    import json
    with open('performance_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
