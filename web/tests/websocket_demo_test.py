#!/usr/bin/env python3
"""
WebSocket Demo Message Test - Validates the demo streaming functionality
"""

import asyncio
import json
import time
import websockets
from typing import Dict, Any, List

async def test_websocket_demo_messages():
    """Test WebSocket demo message streaming"""
    print("🔄 Testing WebSocket Demo Messages...")
    
    session_id = f"demo-test-{int(time.time())}"
    ws_url = f"ws://localhost:8003/ws/{session_id}"
    
    results = {
        'connection_established': False,
        'messages_received': [],
        'agent_status_updates': 0,
        'message_updates': 0,
        'unique_agents': set(),
        'message_types': set(),
        'duration': 0
    }
    
    start_time = time.time()
    
    try:
        async with websockets.connect(ws_url) as websocket:
            results['connection_established'] = True
            print(f"✅ Connected to {ws_url}")
            
            # Listen for messages for 10 seconds to capture demo cycle
            end_time = start_time + 10
            while time.time() < end_time:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    results['messages_received'].append(data)
                    
                    msg_type = data.get('type', 'unknown')
                    results['message_types'].add(msg_type)
                    
                    if msg_type == 'agent_status_update':
                        results['agent_status_updates'] += 1
                        if 'data' in data and 'agent' in data['data']:
                            results['unique_agents'].add(data['data']['agent'])
                            
                    elif msg_type == 'message_update':
                        results['message_updates'] += 1
                        
                    print(f"📨 Received {msg_type}: {data.get('data', {}).get('agent', 'N/A')} - {data.get('data', {}).get('status', data.get('data', {}).get('message_type', 'N/A'))}")
                    
                except asyncio.TimeoutError:
                    continue
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON decode error: {e}")
                    
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        results['error'] = str(e)
        
    results['duration'] = time.time() - start_time
    results['unique_agents'] = list(results['unique_agents'])
    results['message_types'] = list(results['message_types'])
    
    return results

def print_websocket_results(results: Dict[str, Any]):
    """Print WebSocket test results"""
    print("\n" + "="*60)
    print("🔄 WEBSOCKET DEMO TEST RESULTS")
    print("="*60)
    
    print(f"🔌 Connection: {'✅' if results['connection_established'] else '❌'}")
    print(f"📨 Total Messages: {len(results['messages_received'])}")
    print(f"👥 Agent Status Updates: {results['agent_status_updates']}")
    print(f"💬 Message Updates: {results['message_updates']}")
    print(f"⏱️ Duration: {results['duration']:.1f}s")
    
    if results['unique_agents']:
        print(f"\n🤖 Agents Seen:")
        for agent in results['unique_agents']:
            print(f"   • {agent}")
            
    if results['message_types']:
        print(f"\n📋 Message Types:")
        for msg_type in results['message_types']:
            print(f"   • {msg_type}")
            
    # Show sample messages
    if results['messages_received']:
        print(f"\n📄 Sample Messages (first 3):")
        for i, msg in enumerate(results['messages_received'][:3]):
            print(f"   {i+1}. {msg.get('type', 'unknown')}: {json.dumps(msg.get('data', {}), indent=6)}")
            
    success = (results['connection_established'] and 
              len(results['messages_received']) > 0 and
              results['agent_status_updates'] > 0)
              
    print(f"\n🎯 Demo Test: {'✅ SUCCESS' if success else '❌ FAILURE'}")
    print("="*60)
    
    return success

async def main():
    """Main test execution"""
    results = await test_websocket_demo_messages()
    success = print_websocket_results(results)
    
    # Save results
    with open('websocket_demo_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
        
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
