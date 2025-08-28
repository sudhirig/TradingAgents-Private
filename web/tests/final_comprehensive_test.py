#!/usr/bin/env python3
"""
Final Comprehensive Test Suite - Complete validation of TradingAgents Web Application
"""

import asyncio
import json
import time
import requests
import websockets
from typing import Dict, Any

class ComprehensiveValidator:
    """Complete validation of all web app functionality"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8003"
        self.frontend_url = "http://localhost:5175"
        self.results = {}
        
    def test_backend_functionality(self) -> Dict[str, Any]:
        """Test all backend functionality"""
        print("🔧 Testing Backend Functionality...")
        results = {}
        
        # Health check
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            results['health'] = {
                'status': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            results['health'] = {'status': False, 'error': str(e)}
            
        # API endpoints
        endpoints = {
            '/api/config/analysts': 'analysts_config',
            '/api/config/llm-providers': 'llm_providers',
            '/docs': 'api_documentation'
        }
        
        for endpoint, key in endpoints.items():
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                results[key] = {
                    'status': response.status_code == 200,
                    'response_time': response.elapsed.total_seconds()
                }
                if endpoint != '/docs' and response.status_code == 200:
                    results[key]['data_count'] = len(response.json())
            except Exception as e:
                results[key] = {'status': False, 'error': str(e)}
                
        return results
        
    def test_frontend_functionality(self) -> Dict[str, Any]:
        """Test frontend functionality"""
        print("🌐 Testing Frontend Functionality...")
        results = {}
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            results['page_load'] = {
                'status': response.status_code == 200,
                'response_time': response.elapsed.total_seconds()
            }
            
            if response.status_code == 200:
                content = response.text.lower()
                results['react_detected'] = 'react' in content or 'id="root"' in content
                results['vite_detected'] = 'vite' in content or '@vite' in content
                results['has_javascript'] = '<script' in content
                results['has_styling'] = 'style' in content or 'css' in content
                
        except Exception as e:
            results['page_load'] = {'status': False, 'error': str(e)}
            
        return results
        
    async def test_websocket_functionality(self) -> Dict[str, Any]:
        """Test WebSocket functionality"""
        print("🔄 Testing WebSocket Functionality...")
        results = {
            'connection': False,
            'demo_messages': False,
            'message_count': 0,
            'connection_time': 0,
            'agents_seen': [],
            'message_types': []
        }
        
        session_id = f"test-{int(time.time())}"
        ws_url = f"ws://localhost:8003/ws/{session_id}"
        
        start_time = time.time()
        try:
            async with websockets.connect(ws_url) as websocket:
                results['connection'] = True
                results['connection_time'] = time.time() - start_time
                
                # Listen for messages for 8 seconds
                end_time = start_time + 8
                while time.time() < end_time:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(message)
                        results['message_count'] += 1
                        
                        msg_type = data.get('type', 'unknown')
                        if msg_type not in results['message_types']:
                            results['message_types'].append(msg_type)
                            
                        # Check for agent information
                        if 'agent' in data:
                            agent = data['agent']
                            if agent not in results['agents_seen']:
                                results['agents_seen'].append(agent)
                        elif 'agent_name' in data:
                            agent = data['agent_name']
                            if agent not in results['agents_seen']:
                                results['agents_seen'].append(agent)
                                
                        results['demo_messages'] = True
                        
                    except asyncio.TimeoutError:
                        continue
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            results['error'] = str(e)
            
        return results
        
    def test_security_features(self) -> Dict[str, Any]:
        """Test security features"""
        print("🔒 Testing Security Features...")
        results = {}
        
        try:
            # Test CORS headers
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            results['cors_enabled'] = 'access-control-allow-origin' in response.headers
            
            # Test security headers
            security_headers = [
                'x-content-type-options',
                'x-frame-options',
                'x-xss-protection',
                'referrer-policy'
            ]
            
            results['security_headers'] = {}
            for header in security_headers:
                results['security_headers'][header] = header in response.headers
                
            results['security_score'] = sum(results['security_headers'].values())
            
        except Exception as e:
            results['error'] = str(e)
            
        return results
        
    async def test_performance(self) -> Dict[str, Any]:
        """Test basic performance"""
        print("⚡ Testing Performance...")
        results = {}
        
        # Test API response times
        endpoints = ['/health', '/api/config/analysts']
        response_times = []
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                response_time = time.time() - start_time
                if response.status_code == 200:
                    response_times.append(response_time)
            except:
                pass
                
        if response_times:
            results['avg_api_response'] = sum(response_times) / len(response_times)
            results['max_api_response'] = max(response_times)
            results['performance_grade'] = 'excellent' if results['avg_api_response'] < 0.1 else 'good'
        else:
            results['performance_grade'] = 'poor'
            
        return results
        
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run complete comprehensive test"""
        print("🚀 Starting Comprehensive Validation...")
        print("="*60)
        
        start_time = time.time()
        
        # Run all tests
        self.results['backend'] = self.test_backend_functionality()
        self.results['frontend'] = self.test_frontend_functionality()
        self.results['websocket'] = await self.test_websocket_functionality()
        self.results['security'] = self.test_security_features()
        self.results['performance'] = await self.test_performance()
        
        # Calculate overall status
        self.results['duration'] = time.time() - start_time
        self.results['timestamp'] = time.time()
        
        # Determine success criteria
        backend_ok = self.results['backend']['health']['status']
        frontend_ok = self.results['frontend']['page_load']['status']
        websocket_ok = self.results['websocket']['connection']
        security_ok = self.results['security'].get('cors_enabled', False)
        performance_ok = self.results['performance'].get('performance_grade') in ['excellent', 'good']
        
        self.results['overall_success'] = all([backend_ok, frontend_ok, websocket_ok, security_ok, performance_ok])
        
        return self.results
        
    def print_comprehensive_results(self):
        """Print comprehensive test results"""
        print("\n" + "="*80)
        print("🧪 COMPREHENSIVE VALIDATION RESULTS")
        print("="*80)
        
        # Backend
        backend = self.results['backend']
        print("🔧 Backend:")
        print(f"   Health Check: {'✅' if backend['health']['status'] else '❌'}")
        print(f"   API Documentation: {'✅' if backend.get('api_documentation', {}).get('status') else '❌'}")
        print(f"   Analysts Config: {'✅' if backend.get('analysts_config', {}).get('status') else '❌'} ({backend.get('analysts_config', {}).get('data_count', 0)} analysts)")
        print(f"   LLM Providers: {'✅' if backend.get('llm_providers', {}).get('status') else '❌'} ({backend.get('llm_providers', {}).get('data_count', 0)} providers)")
        
        # Frontend
        frontend = self.results['frontend']
        print(f"\n🌐 Frontend:")
        print(f"   Page Load: {'✅' if frontend['page_load']['status'] else '❌'}")
        print(f"   React Detected: {'✅' if frontend.get('react_detected') else '❌'}")
        print(f"   Vite Build: {'✅' if frontend.get('vite_detected') else '❌'}")
        print(f"   JavaScript Active: {'✅' if frontend.get('has_javascript') else '❌'}")
        
        # WebSocket
        websocket = self.results['websocket']
        print(f"\n🔄 WebSocket:")
        print(f"   Connection: {'✅' if websocket['connection'] else '❌'}")
        print(f"   Demo Messages: {'✅' if websocket['demo_messages'] else '❌'}")
        print(f"   Messages Received: {websocket['message_count']}")
        print(f"   Message Types: {', '.join(websocket['message_types'])}")
        if websocket['agents_seen']:
            print(f"   Agents Seen: {', '.join(websocket['agents_seen'])}")
            
        # Security
        security = self.results['security']
        print(f"\n🔒 Security:")
        print(f"   CORS Enabled: {'✅' if security.get('cors_enabled') else '❌'}")
        print(f"   Security Headers: {security.get('security_score', 0)}/4 present")
        
        # Performance
        performance = self.results['performance']
        print(f"\n⚡ Performance:")
        grade = performance.get('performance_grade', 'unknown')
        grade_emoji = {'excellent': '🚀', 'good': '✅', 'poor': '❌'}.get(grade, '❓')
        print(f"   Grade: {grade_emoji} {grade.upper()}")
        if 'avg_api_response' in performance:
            print(f"   Avg API Response: {performance['avg_api_response']*1000:.1f}ms")
            
        # Overall Result
        overall = '🎉 SUCCESS' if self.results['overall_success'] else '⚠️ ISSUES FOUND'
        print(f"\n🎯 Overall Status: {overall}")
        print(f"⏱️ Total Duration: {self.results['duration']:.2f}s")
        print("="*80)

async def main():
    """Main comprehensive test execution"""
    validator = ComprehensiveValidator()
    results = await validator.run_comprehensive_test()
    validator.print_comprehensive_results()
    
    # Save results
    with open('comprehensive_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
        
    return results['overall_success']

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
