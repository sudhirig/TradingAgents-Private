#!/usr/bin/env python3
"""
UI Validation Test - Tests frontend components and user interface
"""

import requests
import json
import time
from typing import Dict, Any

def test_frontend_ui() -> Dict[str, Any]:
    """Test frontend UI components and functionality"""
    print("🌐 Testing Frontend UI Components...")
    
    results = {
        'page_load': False,
        'react_app': False,
        'components_loaded': False,
        'styling_present': False,
        'javascript_active': False,
        'error': None
    }
    
    try:
        # Test main page load
        response = requests.get("http://localhost:5175", timeout=10)
        results['page_load'] = response.status_code == 200
        
        if results['page_load']:
            content = response.text.lower()
            
            # Check for React
            results['react_app'] = any(indicator in content for indicator in [
                'react', 'id="root"', 'react-dom', '__react'
            ])
            
            # Check for key components
            component_indicators = [
                'dashboard', 'analysis', 'websocket', 'config',
                'tradingagents', 'agent', 'message'
            ]
            results['components_loaded'] = any(indicator in content for indicator in component_indicators)
            
            # Check for styling (Tailwind CSS)
            styling_indicators = [
                'tailwind', 'css', 'style', 'class='
            ]
            results['styling_present'] = any(indicator in content for indicator in styling_indicators)
            
            # Check for JavaScript activity
            js_indicators = [
                'script', 'javascript', 'js', 'module'
            ]
            results['javascript_active'] = any(indicator in content for indicator in js_indicators)
            
    except Exception as e:
        results['error'] = str(e)
        
    return results

def test_api_integration() -> Dict[str, Any]:
    """Test frontend-backend API integration"""
    print("🔗 Testing API Integration...")
    
    results = {
        'backend_reachable': False,
        'cors_configured': False,
        'endpoints_accessible': {},
        'error': None
    }
    
    try:
        # Test backend health from frontend perspective
        headers = {
            'Origin': 'http://localhost:5175',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        # Test CORS preflight
        response = requests.options("http://localhost:8003/health", headers=headers, timeout=5)
        results['cors_configured'] = 'access-control-allow-origin' in response.headers
        
        # Test key endpoints
        endpoints = [
            '/health',
            '/api/config/analysts',
            '/api/config/llm-providers'
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"http://localhost:8003{endpoint}", timeout=5)
                results['endpoints_accessible'][endpoint] = {
                    'status': response.status_code == 200,
                    'response_time': response.elapsed.total_seconds()
                }
            except Exception as e:
                results['endpoints_accessible'][endpoint] = {
                    'status': False,
                    'error': str(e)
                }
                
        results['backend_reachable'] = all(
            ep['status'] for ep in results['endpoints_accessible'].values()
        )
        
    except Exception as e:
        results['error'] = str(e)
        
    return results

def test_security_features() -> Dict[str, Any]:
    """Test security features"""
    print("🔒 Testing Security Features...")
    
    results = {
        'cors_headers': False,
        'security_headers': {},
        'rate_limiting': False,
        'input_validation': False
    }
    
    try:
        # Test security headers
        response = requests.get("http://localhost:8003/health", timeout=5)
        
        security_headers = [
            'x-content-type-options',
            'x-frame-options', 
            'x-xss-protection',
            'referrer-policy'
        ]
        
        for header in security_headers:
            results['security_headers'][header] = header in response.headers
            
        results['cors_headers'] = 'access-control-allow-origin' in response.headers
        
        # Test rate limiting (make rapid requests)
        rapid_requests = []
        for _ in range(10):
            try:
                resp = requests.get("http://localhost:8003/health", timeout=1)
                rapid_requests.append(resp.status_code)
            except:
                rapid_requests.append(0)
                
        # If we get rate limited, some requests should fail
        results['rate_limiting'] = any(code == 429 for code in rapid_requests)
        
    except Exception as e:
        results['error'] = str(e)
        
    return results

def print_ui_results(ui_results: Dict[str, Any], api_results: Dict[str, Any], security_results: Dict[str, Any]):
    """Print UI validation results"""
    print("\n" + "="*70)
    print("🌐 UI VALIDATION RESULTS")
    print("="*70)
    
    # Frontend UI
    print("🎨 Frontend UI:")
    print(f"   Page Load: {'✅' if ui_results['page_load'] else '❌'}")
    print(f"   React App: {'✅' if ui_results['react_app'] else '❌'}")
    print(f"   Components: {'✅' if ui_results['components_loaded'] else '❌'}")
    print(f"   Styling: {'✅' if ui_results['styling_present'] else '❌'}")
    print(f"   JavaScript: {'✅' if ui_results['javascript_active'] else '❌'}")
    
    # API Integration
    print(f"\n🔗 API Integration:")
    print(f"   Backend Reachable: {'✅' if api_results['backend_reachable'] else '❌'}")
    print(f"   CORS Configured: {'✅' if api_results['cors_configured'] else '❌'}")
    
    if api_results['endpoints_accessible']:
        print("   Endpoints:")
        for endpoint, result in api_results['endpoints_accessible'].items():
            status = '✅' if result['status'] else '❌'
            time_info = f" ({result.get('response_time', 0)*1000:.1f}ms)" if result['status'] else ""
            print(f"      {endpoint}: {status}{time_info}")
    
    # Security
    print(f"\n🔒 Security Features:")
    print(f"   CORS Headers: {'✅' if security_results['cors_headers'] else '❌'}")
    
    if security_results['security_headers']:
        security_count = sum(1 for present in security_results['security_headers'].values() if present)
        total_headers = len(security_results['security_headers'])
        print(f"   Security Headers: {security_count}/{total_headers} present")
        
    # Overall assessment
    ui_ok = all([
        ui_results['page_load'],
        ui_results['react_app'],
        ui_results['components_loaded']
    ])
    
    api_ok = api_results['backend_reachable'] and api_results['cors_configured']
    
    overall_success = ui_ok and api_ok
    
    print(f"\n🎯 UI Validation: {'✅ SUCCESS' if overall_success else '❌ FAILURE'}")
    print("="*70)
    
    return overall_success

def main():
    """Main UI validation execution"""
    print("🚀 Starting UI Validation...")
    print("="*50)
    
    # Run tests
    ui_results = test_frontend_ui()
    api_results = test_api_integration()
    security_results = test_security_features()
    
    # Print results
    success = print_ui_results(ui_results, api_results, security_results)
    
    # Save results
    results = {
        'ui_validation': ui_results,
        'api_integration': api_results,
        'security_features': security_results,
        'overall_success': success,
        'timestamp': time.time()
    }
    
    with open('ui_validation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
        
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
