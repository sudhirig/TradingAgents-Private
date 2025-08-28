#!/usr/bin/env python3
"""
Quick validation test for TradingAgents Web Application
Tests all critical functionality without hanging
"""

import asyncio
import json
import time
import requests
import websockets
from typing import Dict, Any

class QuickValidator:
    """Quick validation of all web app functionality"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8003"
        self.frontend_url = "http://localhost:5175"
        self.ws_url = "ws://localhost:8003"
        self.results = {}
        
    def test_backend_health(self) -> Dict[str, Any]:
        """Test backend health and basic endpoints"""
        print("🔍 Testing Backend Health...")
        results = {}
        
        try:
            # Health check
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            results['health'] = {
                'status': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            results['health'] = {'status': False, 'error': str(e)}
            
        try:
            # API docs
            response = requests.get(f"{self.backend_url}/docs", timeout=5)
            results['docs'] = {'status': response.status_code == 200}
        except Exception as e:
            results['docs'] = {'status': False, 'error': str(e)}
            
        return results
        
    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test all API endpoints"""
        print("🔌 Testing API Endpoints...")
        results = {}
        
        endpoints = [
            '/api/config/analysts',
            '/api/config/llm-providers',
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                results[endpoint] = {
                    'status': response.status_code == 200,
                    'data_length': len(response.json()) if response.status_code == 200 else 0
                }
            except Exception as e:
                results[endpoint] = {'status': False, 'error': str(e)}
                
        return results
        
    async def test_websocket(self) -> Dict[str, Any]:
        """Test WebSocket connection"""
        print("🔄 Testing WebSocket Connection...")
        results = {
            'connection': False,
            'messages_received': 0,
            'demo_messages': False,
            'error': None
        }
        
        try:
            session_id = f"test-{int(time.time())}"
            ws_url = f"{self.ws_url}/ws/{session_id}"
            
            async with websockets.connect(ws_url) as websocket:
                results['connection'] = True
                
                # Listen for demo messages for 5 seconds
                start_time = time.time()
                while time.time() - start_time < 5:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(message)
                        results['messages_received'] += 1
                        
                        if data.get('type') in ['agent_status_update', 'message_update']:
                            results['demo_messages'] = True
                            
                    except asyncio.TimeoutError:
                        continue
                        
        except Exception as e:
            results['error'] = str(e)
            
        return results
        
    def test_frontend(self) -> Dict[str, Any]:
        """Test frontend accessibility"""
        print("🌐 Testing Frontend...")
        results = {}
        
        try:
            response = requests.get(self.frontend_url, timeout=5)
            results['accessibility'] = {
                'status': response.status_code == 200,
                'has_react': 'react' in response.text.lower(),
                'has_root_div': 'id="root"' in response.text
            }
        except Exception as e:
            results['accessibility'] = {'status': False, 'error': str(e)}
            
        return results
        
    async def run_validation(self) -> Dict[str, Any]:
        """Run complete validation"""
        print("🚀 Starting Quick Validation...")
        print("="*50)
        
        start_time = time.time()
        
        # Test backend
        self.results['backend'] = self.test_backend_health()
        self.results['api_endpoints'] = self.test_api_endpoints()
        
        # Test WebSocket
        self.results['websocket'] = await self.test_websocket()
        
        # Test frontend
        self.results['frontend'] = self.test_frontend()
        
        # Calculate overall status
        self.results['duration'] = time.time() - start_time
        self.results['timestamp'] = time.time()
        
        # Determine success
        backend_ok = self.results['backend']['health']['status']
        api_ok = all(ep['status'] for ep in self.results['api_endpoints'].values())
        ws_ok = self.results['websocket']['connection']
        frontend_ok = self.results['frontend']['accessibility']['status']
        
        self.results['overall_success'] = all([backend_ok, api_ok, ws_ok, frontend_ok])
        
        return self.results
        
    def print_results(self):
        """Print validation results"""
        print("\n" + "="*60)
        print("🧪 QUICK VALIDATION RESULTS")
        print("="*60)
        
        # Backend Health
        health = self.results['backend']['health']
        print(f"📡 Backend Health: {'✅' if health['status'] else '❌'}")
        if health['status'] and health.get('response'):
            print(f"   Service: {health['response'].get('service', 'Unknown')}")
            print(f"   Version: {health['response'].get('version', 'Unknown')}")
            
        # API Endpoints
        print(f"\n🔌 API Endpoints:")
        for endpoint, result in self.results['api_endpoints'].items():
            status = '✅' if result['status'] else '❌'
            data_info = f" ({result.get('data_length', 0)} items)" if result['status'] else ""
            print(f"   {endpoint}: {status}{data_info}")
            
        # WebSocket
        ws = self.results['websocket']
        print(f"\n🔄 WebSocket:")
        print(f"   Connection: {'✅' if ws['connection'] else '❌'}")
        print(f"   Messages Received: {ws['messages_received']}")
        print(f"   Demo Messages: {'✅' if ws['demo_messages'] else '❌'}")
        
        # Frontend
        frontend = self.results['frontend']['accessibility']
        print(f"\n🌐 Frontend:")
        print(f"   Accessibility: {'✅' if frontend['status'] else '❌'}")
        if frontend['status']:
            print(f"   React Detected: {'✅' if frontend.get('has_react') else '❌'}")
            print(f"   Root Element: {'✅' if frontend.get('has_root_div') else '❌'}")
            
        # Overall Result
        overall = '✅ SUCCESS' if self.results['overall_success'] else '❌ FAILURE'
        print(f"\n🎯 Overall Status: {overall}")
        print(f"⏱️  Duration: {self.results['duration']:.2f}s")
        print("="*60)

async def main():
    """Main validation execution"""
    validator = QuickValidator()
    results = await validator.run_validation()
    validator.print_results()
    
    # Save results
    with open('quick_validation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
        
    return results['overall_success']

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
