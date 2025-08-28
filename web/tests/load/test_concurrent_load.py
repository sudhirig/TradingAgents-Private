"""
Load testing for concurrent WebSocket connections and API requests
"""

import asyncio
import aiohttp
import websockets
import json
import time
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import threading

class LoadTester:
    """Load testing for TradingAgents web application"""
    
    def __init__(self, backend_url: str = "http://localhost:8003"):
        self.backend_url = backend_url
        self.ws_base_url = backend_url.replace('http', 'ws')
        self.results = {
            'api_tests': [],
            'websocket_tests': [],
            'concurrent_tests': [],
            'performance_metrics': {}
        }
        
    async def test_api_load(self, concurrent_requests: int = 50, 
                           requests_per_client: int = 10) -> Dict[str, Any]:
        """Test API endpoint load"""
        print(f"🔥 Testing API load: {concurrent_requests} concurrent clients, {requests_per_client} requests each")
        
        async def make_requests(session: aiohttp.ClientSession, client_id: int) -> List[float]:
            """Make multiple requests for a single client"""
            response_times = []
            
            for i in range(requests_per_client):
                start_time = time.time()
                try:
                    async with session.get(f"{self.backend_url}/api/config/analysts") as response:
                        await response.text()
                        response_times.append(time.time() - start_time)
                except Exception as e:
                    print(f"Request failed for client {client_id}: {e}")
                    response_times.append(-1)  # Mark as failed
                    
            return response_times
            
        # Create concurrent clients
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                make_requests(session, client_id) 
                for client_id in range(concurrent_requests)
            ]
            
            all_response_times = await asyncio.gather(*tasks)
            
        total_time = time.time() - start_time
        
        # Flatten response times and filter out failures
        flat_times = [t for times in all_response_times for t in times if t > 0]
        failed_requests = sum(1 for times in all_response_times for t in times if t < 0)
        
        results = {
            'concurrent_clients': concurrent_requests,
            'requests_per_client': requests_per_client,
            'total_requests': concurrent_requests * requests_per_client,
            'successful_requests': len(flat_times),
            'failed_requests': failed_requests,
            'total_time': total_time,
            'requests_per_second': len(flat_times) / total_time if total_time > 0 else 0,
            'avg_response_time': statistics.mean(flat_times) if flat_times else 0,
            'min_response_time': min(flat_times) if flat_times else 0,
            'max_response_time': max(flat_times) if flat_times else 0,
            'p95_response_time': statistics.quantiles(flat_times, n=20)[18] if len(flat_times) > 20 else 0,
            'success_rate': len(flat_times) / (concurrent_requests * requests_per_client) * 100
        }
        
        return results
        
    async def test_websocket_load(self, concurrent_connections: int = 20,
                                 connection_duration: int = 30) -> Dict[str, Any]:
        """Test WebSocket connection load"""
        print(f"🔌 Testing WebSocket load: {concurrent_connections} concurrent connections for {connection_duration}s")
        
        connection_results = []
        
        async def websocket_client(client_id: int) -> Dict[str, Any]:
            """Single WebSocket client"""
            session_id = f"load-test-{client_id}-{int(time.time())}"
            ws_url = f"{self.ws_base_url}/ws/{session_id}"
            
            result = {
                'client_id': client_id,
                'connected': False,
                'messages_received': 0,
                'connection_time': 0,
                'total_time': 0,
                'error': None
            }
            
            start_time = time.time()
            
            try:
                async with websockets.connect(ws_url) as websocket:
                    result['connected'] = True
                    result['connection_time'] = time.time() - start_time
                    
                    # Listen for messages
                    end_time = start_time + connection_duration
                    while time.time() < end_time:
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                            result['messages_received'] += 1
                        except asyncio.TimeoutError:
                            continue
                        except Exception as e:
                            result['error'] = str(e)
                            break
                            
                    result['total_time'] = time.time() - start_time
                    
            except Exception as e:
                result['error'] = str(e)
                result['total_time'] = time.time() - start_time
                
            return result
            
        # Create concurrent WebSocket connections
        tasks = [websocket_client(i) for i in range(concurrent_connections)]
        connection_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_connections = [r for r in connection_results if isinstance(r, dict) and r['connected']]
        failed_connections = len(connection_results) - len(successful_connections)
        
        total_messages = sum(r['messages_received'] for r in successful_connections)
        avg_connection_time = statistics.mean([r['connection_time'] for r in successful_connections]) if successful_connections else 0
        
        results = {
            'concurrent_connections': concurrent_connections,
            'connection_duration': connection_duration,
            'successful_connections': len(successful_connections),
            'failed_connections': failed_connections,
            'success_rate': len(successful_connections) / concurrent_connections * 100,
            'total_messages_received': total_messages,
            'avg_messages_per_connection': total_messages / len(successful_connections) if successful_connections else 0,
            'avg_connection_time': avg_connection_time,
            'messages_per_second': total_messages / connection_duration if connection_duration > 0 else 0
        }
        
        return results
        
    async def test_mixed_load(self, api_clients: int = 25, ws_clients: int = 15,
                             test_duration: int = 60) -> Dict[str, Any]:
        """Test mixed API and WebSocket load"""
        print(f"🔄 Testing mixed load: {api_clients} API clients + {ws_clients} WS clients for {test_duration}s")
        
        start_time = time.time()
        
        # Start API load test
        api_task = asyncio.create_task(
            self.test_api_load(concurrent_requests=api_clients, requests_per_client=10)
        )
        
        # Start WebSocket load test
        ws_task = asyncio.create_task(
            self.test_websocket_load(concurrent_connections=ws_clients, connection_duration=test_duration)
        )
        
        # Wait for both to complete
        api_results, ws_results = await asyncio.gather(api_task, ws_task)
        
        total_time = time.time() - start_time
        
        results = {
            'test_duration': total_time,
            'api_results': api_results,
            'websocket_results': ws_results,
            'combined_metrics': {
                'total_api_requests': api_results['total_requests'],
                'total_ws_connections': ws_results['concurrent_connections'],
                'overall_success_rate': (
                    api_results['success_rate'] + ws_results['success_rate']
                ) / 2
            }
        }
        
        return results
        
    async def test_performance_metrics_endpoint(self, requests: int = 100) -> Dict[str, Any]:
        """Test performance metrics endpoint under load"""
        print(f"📊 Testing metrics endpoint: {requests} requests")
        
        response_times = []
        failed_requests = 0
        
        async with aiohttp.ClientSession() as session:
            for i in range(requests):
                start_time = time.time()
                try:
                    async with session.get(f"{self.backend_url}/api/metrics/performance") as response:
                        await response.json()
                        response_times.append(time.time() - start_time)
                except Exception:
                    failed_requests += 1
                    
        results = {
            'total_requests': requests,
            'successful_requests': len(response_times),
            'failed_requests': failed_requests,
            'success_rate': len(response_times) / requests * 100,
            'avg_response_time': statistics.mean(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0
        }
        
        return results
        
    async def run_comprehensive_load_test(self) -> Dict[str, Any]:
        """Run comprehensive load testing suite"""
        print("🚀 Starting Comprehensive Load Test...")
        
        results = {
            'timestamp': time.time(),
            'test_phases': {}
        }
        
        # Phase 1: Light API load
        print("\n📈 Phase 1: Light API Load")
        results['test_phases']['light_api_load'] = await self.test_api_load(
            concurrent_requests=10, requests_per_client=5
        )
        
        # Phase 2: Heavy API load
        print("\n📈 Phase 2: Heavy API Load")
        results['test_phases']['heavy_api_load'] = await self.test_api_load(
            concurrent_requests=50, requests_per_client=20
        )
        
        # Phase 3: WebSocket load
        print("\n🔌 Phase 3: WebSocket Load")
        results['test_phases']['websocket_load'] = await self.test_websocket_load(
            concurrent_connections=25, connection_duration=30
        )
        
        # Phase 4: Mixed load
        print("\n🔄 Phase 4: Mixed Load")
        results['test_phases']['mixed_load'] = await self.test_mixed_load(
            api_clients=20, ws_clients=10, test_duration=45
        )
        
        # Phase 5: Metrics endpoint load
        print("\n📊 Phase 5: Metrics Endpoint Load")
        results['test_phases']['metrics_load'] = await self.test_performance_metrics_endpoint(
            requests=200
        )
        
        # Calculate overall metrics
        results['overall_metrics'] = self.calculate_overall_metrics(results['test_phases'])
        
        return results
        
    def calculate_overall_metrics(self, test_phases: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall performance metrics"""
        overall = {
            'total_api_requests': 0,
            'total_ws_connections': 0,
            'avg_success_rate': 0,
            'peak_requests_per_second': 0,
            'avg_response_time': 0
        }
        
        success_rates = []
        response_times = []
        rps_values = []
        
        for phase_name, phase_results in test_phases.items():
            if 'success_rate' in phase_results:
                success_rates.append(phase_results['success_rate'])
                
            if 'avg_response_time' in phase_results:
                response_times.append(phase_results['avg_response_time'])
                
            if 'requests_per_second' in phase_results:
                rps_values.append(phase_results['requests_per_second'])
                
            if 'total_requests' in phase_results:
                overall['total_api_requests'] += phase_results['total_requests']
                
            if 'concurrent_connections' in phase_results:
                overall['total_ws_connections'] += phase_results['concurrent_connections']
                
        overall['avg_success_rate'] = statistics.mean(success_rates) if success_rates else 0
        overall['avg_response_time'] = statistics.mean(response_times) if response_times else 0
        overall['peak_requests_per_second'] = max(rps_values) if rps_values else 0
        
        return overall
        
    def print_results(self, results: Dict[str, Any]):
        """Print formatted load test results"""
        print("\n" + "="*80)
        print("🔥 COMPREHENSIVE LOAD TEST RESULTS")
        print("="*80)
        
        for phase_name, phase_results in results['test_phases'].items():
            print(f"\n📊 {phase_name.upper().replace('_', ' ')}")
            print("-" * 40)
            
            if 'total_requests' in phase_results:
                print(f"   Total Requests: {phase_results['total_requests']}")
                print(f"   Success Rate: {phase_results['success_rate']:.1f}%")
                print(f"   Requests/sec: {phase_results['requests_per_second']:.1f}")
                print(f"   Avg Response Time: {phase_results['avg_response_time']*1000:.1f}ms")
                
            if 'concurrent_connections' in phase_results:
                print(f"   Concurrent Connections: {phase_results['concurrent_connections']}")
                print(f"   Success Rate: {phase_results['success_rate']:.1f}%")
                print(f"   Messages Received: {phase_results['total_messages_received']}")
                print(f"   Messages/sec: {phase_results['messages_per_second']:.1f}")
                
        # Overall metrics
        overall = results['overall_metrics']
        print(f"\n🎯 OVERALL PERFORMANCE")
        print("-" * 40)
        print(f"   Total API Requests: {overall['total_api_requests']}")
        print(f"   Total WS Connections: {overall['total_ws_connections']}")
        print(f"   Average Success Rate: {overall['avg_success_rate']:.1f}%")
        print(f"   Peak Requests/sec: {overall['peak_requests_per_second']:.1f}")
        print(f"   Average Response Time: {overall['avg_response_time']*1000:.1f}ms")
        
        # Performance assessment
        success_threshold = 95.0
        response_time_threshold = 0.5  # 500ms
        
        performance_grade = "🟢 EXCELLENT"
        if overall['avg_success_rate'] < success_threshold:
            performance_grade = "🟡 NEEDS IMPROVEMENT"
        if overall['avg_response_time'] > response_time_threshold:
            performance_grade = "🔴 POOR PERFORMANCE"
            
        print(f"\n🏆 Performance Grade: {performance_grade}")
        print("="*80)

async def main():
    """Main load test execution"""
    tester = LoadTester()
    results = await tester.run_comprehensive_load_test()
    tester.print_results(results)
    
    # Save results to file
    with open('load_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
        
    # Return success based on performance
    overall = results['overall_metrics']
    success = (overall['avg_success_rate'] >= 90.0 and 
              overall['avg_response_time'] <= 1.0)
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
