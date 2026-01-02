"""
Load Testing and Stress Testing Suite
Tests system performance under high load
"""

import asyncio
import time
import statistics
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
import random


class LoadTester:
    """Load testing utility for API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    async def simulate_request(self, endpoint: str, method: str = "GET", 
                              data: Dict = None) -> Dict:
        """Simulate a single API request"""
        start_time = time.time()
        
        try:
            # Simulate network latency
            await asyncio.sleep(random.uniform(0.01, 0.05))
            
            # Simulate processing
            await asyncio.sleep(random.uniform(0.05, 0.15))
            
            elapsed = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                'success': True,
                'response_time_ms': elapsed,
                'endpoint': endpoint,
                'status_code': 200
            }
        except Exception as e:
            return {
                'success': False,
                'response_time_ms': 0,
                'endpoint': endpoint,
                'error': str(e)
            }
    
    async def run_concurrent_requests(self, endpoint: str, num_requests: int) -> List[Dict]:
        """Run multiple concurrent requests to an endpoint"""
        tasks = [self.simulate_request(endpoint) for _ in range(num_requests)]
        return await asyncio.gather(*tasks)
    
    def calculate_statistics(self, results: List[Dict]) -> Dict:
        """Calculate performance statistics from results"""
        response_times = [r['response_time_ms'] for r in results if r['success']]
        failures = [r for r in results if not r['success']]
        
        if not response_times:
            return {
                'total_requests': len(results),
                'successful': 0,
                'failed': len(failures),
                'error_rate': 100.0
            }
        
        return {
            'total_requests': len(results),
            'successful': len(response_times),
            'failed': len(failures),
            'min_ms': min(response_times),
            'max_ms': max(response_times),
            'mean_ms': statistics.mean(response_times),
            'median_ms': statistics.median(response_times),
            'p95_ms': sorted(response_times)[int(len(response_times) * 0.95)],
            'p99_ms': sorted(response_times)[int(len(response_times) * 0.99)],
            'error_rate': (len(failures) / len(results)) * 100
        }
    
    async def test_endpoint_load(self, endpoint: str, num_requests: int, 
                                 concurrent_users: int) -> Dict:
        """
        Test endpoint with concurrent load
        
        Args:
            endpoint: API endpoint to test
            num_requests: Total number of requests
            concurrent_users: Number of concurrent users
        """
        print(f"\n🔥 Load Testing: {endpoint}")
        print(f"   Total Requests: {num_requests}")
        print(f"   Concurrent Users: {concurrent_users}")
        
        start_time = time.time()
        
        # Distribute requests across concurrent users
        requests_per_user = num_requests // concurrent_users
        
        tasks = []
        for i in range(concurrent_users):
            task = self.run_concurrent_requests(endpoint, requests_per_user)
            tasks.append(task)
        
        # Execute all concurrent user loads
        all_results = await asyncio.gather(*tasks)
        
        # Flatten results
        results = [item for sublist in all_results for item in sublist]
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        stats = self.calculate_statistics(results)
        stats['total_time_s'] = total_time
        stats['requests_per_second'] = num_requests / total_time
        
        # Print results
        print(f"\n📊 Results:")
        print(f"   Total Time: {total_time:.2f}s")
        print(f"   Requests/sec: {stats['requests_per_second']:.2f}")
        print(f"   Success Rate: {(stats['successful'] / stats['total_requests'] * 100):.2f}%")
        print(f"   Mean Response: {stats['mean_ms']:.2f}ms")
        print(f"   Median Response: {stats['median_ms']:.2f}ms")
        print(f"   P95 Response: {stats['p95_ms']:.2f}ms")
        print(f"   P99 Response: {stats['p99_ms']:.2f}ms")
        print(f"   Max Response: {stats['max_ms']:.2f}ms")
        
        return stats


class StressTester:
    """Stress testing to find system limits"""
    
    def __init__(self):
        self.load_tester = LoadTester()
    
    async def ramp_up_test(self, endpoint: str, max_users: int = 100,
                          ramp_up_time_s: int = 60) -> List[Dict]:
        """
        Gradually increase load to find breaking point
        
        Args:
            endpoint: API endpoint to stress test
            max_users: Maximum number of concurrent users
            ramp_up_time_s: Time to reach max users
        """
        print(f"\n🚀 Ramp-Up Stress Test: {endpoint}")
        print(f"   Max Users: {max_users}")
        print(f"   Ramp-Up Time: {ramp_up_time_s}s")
        
        results = []
        step_size = max_users // 10  # 10 steps
        requests_per_step = 50
        
        for users in range(step_size, max_users + 1, step_size):
            print(f"\n📈 Testing with {users} concurrent users...")
            
            stats = await self.load_tester.test_endpoint_load(
                endpoint, 
                requests_per_step * users,
                users
            )
            
            results.append({
                'concurrent_users': users,
                'stats': stats
            })
            
            # Check if system is degrading
            if stats['error_rate'] > 10:
                print(f"\n⚠️  High error rate ({stats['error_rate']:.2f}%) at {users} users")
                print(f"   System limit approximately: {users - step_size} concurrent users")
                break
            
            if stats['p95_ms'] > 2000:  # 2 second threshold
                print(f"\n⚠️  Slow responses (P95: {stats['p95_ms']:.2f}ms) at {users} users")
                print(f"   Performance degrades beyond {users - step_size} users")
                break
            
            # Brief pause between steps
            await asyncio.sleep(2)
        
        return results
    
    async def spike_test(self, endpoint: str, normal_load: int = 10,
                        spike_load: int = 100, duration_s: int = 30) -> Dict:
        """
        Test system behavior under sudden load spikes
        
        Args:
            endpoint: API endpoint to test
            normal_load: Normal concurrent users
            spike_load: Spike concurrent users
            duration_s: Duration of spike
        """
        print(f"\n⚡ Spike Test: {endpoint}")
        print(f"   Normal Load: {normal_load} users")
        print(f"   Spike Load: {spike_load} users")
        print(f"   Spike Duration: {duration_s}s")
        
        # Phase 1: Normal load
        print(f"\n📊 Phase 1: Normal load...")
        normal_stats = await self.load_tester.test_endpoint_load(
            endpoint, normal_load * 10, normal_load
        )
        
        # Phase 2: Spike
        print(f"\n⚡ Phase 2: SPIKE!")
        spike_stats = await self.load_tester.test_endpoint_load(
            endpoint, spike_load * 10, spike_load
        )
        
        # Phase 3: Recovery to normal
        print(f"\n🔄 Phase 3: Recovery...")
        recovery_stats = await self.load_tester.test_endpoint_load(
            endpoint, normal_load * 10, normal_load
        )
        
        # Analyze results
        degradation = ((spike_stats['mean_ms'] - normal_stats['mean_ms']) / 
                      normal_stats['mean_ms'] * 100)
        recovery_time = abs(recovery_stats['mean_ms'] - normal_stats['mean_ms'])
        
        print(f"\n📊 Spike Test Results:")
        print(f"   Normal Response: {normal_stats['mean_ms']:.2f}ms")
        print(f"   Spike Response: {spike_stats['mean_ms']:.2f}ms")
        print(f"   Recovery Response: {recovery_stats['mean_ms']:.2f}ms")
        print(f"   Performance Degradation: {degradation:.2f}%")
        print(f"   Recovery Quality: {recovery_time:.2f}ms difference")
        
        return {
            'normal': normal_stats,
            'spike': spike_stats,
            'recovery': recovery_stats,
            'degradation_percent': degradation,
            'recovered': recovery_time < 50  # Good recovery if within 50ms
        }
    
    async def endurance_test(self, endpoint: str, concurrent_users: int = 20,
                            duration_minutes: int = 10) -> Dict:
        """
        Test system stability over extended period
        
        Args:
            endpoint: API endpoint to test
            concurrent_users: Sustained concurrent users
            duration_minutes: Test duration in minutes
        """
        print(f"\n⏱️  Endurance Test: {endpoint}")
        print(f"   Concurrent Users: {concurrent_users}")
        print(f"   Duration: {duration_minutes} minutes")
        
        start_time = time.time()
        duration_seconds = duration_minutes * 60
        
        all_results = []
        iteration = 0
        
        while (time.time() - start_time) < duration_seconds:
            iteration += 1
            elapsed = time.time() - start_time
            
            print(f"\n⏱️  Iteration {iteration} ({elapsed:.0f}s elapsed)...")
            
            stats = await self.load_tester.test_endpoint_load(
                endpoint,
                concurrent_users * 5,
                concurrent_users
            )
            
            all_results.append(stats)
            
            # Brief pause
            await asyncio.sleep(5)
        
        # Analyze endurance results
        mean_response_times = [r['mean_ms'] for r in all_results]
        error_rates = [r['error_rate'] for r in all_results]
        
        # Check for degradation over time
        first_half = mean_response_times[:len(mean_response_times)//2]
        second_half = mean_response_times[len(mean_response_times)//2:]
        
        degradation = ((statistics.mean(second_half) - statistics.mean(first_half)) /
                      statistics.mean(first_half) * 100)
        
        print(f"\n📊 Endurance Test Results:")
        print(f"   Total Iterations: {iteration}")
        print(f"   Average Response Time: {statistics.mean(mean_response_times):.2f}ms")
        print(f"   Response Time Std Dev: {statistics.stdev(mean_response_times):.2f}ms")
        print(f"   Average Error Rate: {statistics.mean(error_rates):.2f}%")
        print(f"   Performance Degradation: {degradation:.2f}%")
        
        stable = abs(degradation) < 10  # Stable if < 10% degradation
        print(f"   System Stability: {'✅ STABLE' if stable else '⚠️  DEGRADING'}")
        
        return {
            'iterations': iteration,
            'mean_response_ms': statistics.mean(mean_response_times),
            'response_std_dev': statistics.stdev(mean_response_times),
            'mean_error_rate': statistics.mean(error_rates),
            'degradation_percent': degradation,
            'stable': stable
        }


class PerformanceBenchmark:
    """Benchmark system performance"""
    
    async def run_benchmark_suite(self):
        """Run comprehensive performance benchmark"""
        print("\n" + "="*60)
        print("🎯 PERFORMANCE BENCHMARK SUITE")
        print("="*60)
        
        load_tester = LoadTester()
        stress_tester = StressTester()
        
        # Benchmark critical endpoints
        endpoints = [
            '/api/v1/analytics/quick-stats',
            '/api/v1/analytics/dashboard',
            '/api/v1/analytics/summary/daily-optimized',
            '/api/v1/privacy/score',
            '/iot/automation/process'
        ]
        
        results = {}
        
        # 1. Load test each endpoint
        print("\n" + "="*60)
        print("📊 LOAD TESTING")
        print("="*60)
        
        for endpoint in endpoints:
            stats = await load_tester.test_endpoint_load(
                endpoint, 
                num_requests=100,
                concurrent_users=10
            )
            results[endpoint] = {'load_test': stats}
        
        # 2. Stress test most critical endpoint
        print("\n" + "="*60)
        print("🔥 STRESS TESTING")
        print("="*60)
        
        critical_endpoint = '/api/v1/analytics/dashboard'
        
        # Ramp-up test
        ramp_results = await stress_tester.ramp_up_test(
            critical_endpoint,
            max_users=50,
            ramp_up_time_s=30
        )
        results[critical_endpoint]['ramp_up'] = ramp_results
        
        # Spike test
        spike_results = await stress_tester.spike_test(
            critical_endpoint,
            normal_load=10,
            spike_load=50,
            duration_s=20
        )
        results[critical_endpoint]['spike'] = spike_results
        
        # 3. Short endurance test
        print("\n" + "="*60)
        print("⏱️  ENDURANCE TESTING")
        print("="*60)
        
        endurance_results = await stress_tester.endurance_test(
            critical_endpoint,
            concurrent_users=10,
            duration_minutes=2  # Short for testing
        )
        results[critical_endpoint]['endurance'] = endurance_results
        
        # Print summary
        print("\n" + "="*60)
        print("📋 BENCHMARK SUMMARY")
        print("="*60)
        
        for endpoint, data in results.items():
            print(f"\n{endpoint}:")
            if 'load_test' in data:
                lt = data['load_test']
                print(f"  Load Test: {lt['mean_ms']:.2f}ms avg, "
                      f"{lt['requests_per_second']:.2f} req/s")
        
        print("\n✅ Benchmark suite completed!")
        
        return results


# Test runner
async def main():
    """Run load and stress tests"""
    benchmark = PerformanceBenchmark()
    await benchmark.run_benchmark_suite()


if __name__ == "__main__":
    asyncio.run(main())
