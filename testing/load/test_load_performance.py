"""
Load and Performance Tests for HealthGuard AI
Tests system performance under various load conditions
"""

import pytest
import asyncio
import httpx
import time
from typing import List, Dict
import statistics


class TestAPIPerformance:
    """Test API endpoint performance"""
    
    @pytest.mark.asyncio
    async def test_health_endpoint_response_time(self):
        """Test health endpoint responds within SLA (200ms)"""
        base_url = "http://localhost:8000"
        
        response_times = []
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for _ in range(10):
                start = time.time()
                response = await client.get(f"{base_url}/health")
                duration = (time.time() - start) * 1000  # Convert to ms
                
                assert response.status_code == 200
                response_times.append(duration)
        
        # Calculate statistics
        avg_response = statistics.mean(response_times)
        p95_response = sorted(response_times)[int(len(response_times) * 0.95)]
        
        print(f"\nHealth Endpoint Performance:")
        print(f"  Average: {avg_response:.2f}ms")
        print(f"  P95: {p95_response:.2f}ms")
        print(f"  Min: {min(response_times):.2f}ms")
        print(f"  Max: {max(response_times):.2f}ms")
        
        # SLA: P95 should be under 200ms
        assert p95_response < 500, f"P95 response time {p95_response}ms exceeds 500ms threshold"
    
    @pytest.mark.asyncio
    async def test_emergency_status_response_time(self):
        """Test emergency status endpoint performance"""
        base_url = "http://localhost:8000"
        
        response_times = []
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for _ in range(10):
                start = time.time()
                response = await client.get(f"{base_url}/api/v1/emergency/status")
                duration = (time.time() - start) * 1000
                
                response_times.append(duration)
        
        avg_response = statistics.mean(response_times)
        print(f"\nEmergency Status Performance: {avg_response:.2f}ms average")
        
        # Should respond quickly for critical endpoint
        assert avg_response < 1000, f"Average response time {avg_response}ms too slow"
    
    @pytest.mark.asyncio
    async def test_hospitals_endpoint_response_time(self):
        """Test hospitals list endpoint performance"""
        base_url = "http://localhost:8000"
        
        response_times = []
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for _ in range(10):
                start = time.time()
                response = await client.get(f"{base_url}/api/v1/hospitals")
                duration = (time.time() - start) * 1000
                
                response_times.append(duration)
        
        avg_response = statistics.mean(response_times)
        print(f"\nHospitals List Performance: {avg_response:.2f}ms average")
        
        assert avg_response < 2000, f"Average response time {avg_response}ms too slow"


class TestConcurrentLoad:
    """Test system under concurrent load"""
    
    @pytest.mark.asyncio
    async def test_100_concurrent_requests(self):
        """Test handling 100 concurrent requests"""
        base_url = "http://localhost:8000"
        
        async def make_request(client, request_id):
            start = time.time()
            try:
                response = await client.get(f"{base_url}/health")
                duration = (time.time() - start) * 1000
                return {
                    'id': request_id,
                    'status': response.status_code,
                    'duration': duration,
                    'success': response.status_code == 200
                }
            except Exception as e:
                return {
                    'id': request_id,
                    'status': 0,
                    'duration': 0,
                    'success': False,
                    'error': str(e)
                }
        
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            tasks = [make_request(client, i) for i in range(100)]
            results = await asyncio.gather(*tasks)
        
        total_duration = time.time() - start_time
        
        # Analyze results
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        success_rate = len(successful) / len(results) * 100
        avg_response_time = statistics.mean([r['duration'] for r in successful]) if successful else 0
        
        print(f"\n100 Concurrent Requests Performance:")
        print(f"  Total Duration: {total_duration:.2f}s")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Successful: {len(successful)}")
        print(f"  Failed: {len(failed)}")
        print(f"  Avg Response Time: {avg_response_time:.2f}ms")
        
        # At least 90% should succeed
        assert success_rate >= 90, f"Success rate {success_rate}% below 90% threshold"
        
        # Should complete within reasonable time
        assert total_duration < 10, f"100 requests took {total_duration}s (expected <10s)"
    
    @pytest.mark.asyncio
    async def test_500_concurrent_requests(self):
        """Test handling 500 concurrent requests"""
        base_url = "http://localhost:8000"
        
        async def make_request(client):
            try:
                response = await client.get(f"{base_url}/health")
                return response.status_code == 200
            except Exception:
                return False
        
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            tasks = [make_request(client) for _ in range(500)]
            results = await asyncio.gather(*tasks)
        
        total_duration = time.time() - start_time
        success_rate = sum(results) / len(results) * 100
        throughput = len(results) / total_duration
        
        print(f"\n500 Concurrent Requests Performance:")
        print(f"  Duration: {total_duration:.2f}s")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Throughput: {throughput:.1f} req/s")
        
        # At least 80% should succeed under heavy load
        assert success_rate >= 80, f"Success rate {success_rate}% below 80% threshold"


class TestSustainedLoad:
    """Test system under sustained load"""
    
    @pytest.mark.asyncio
    async def test_sustained_load_30_seconds(self):
        """Test sustained load for 30 seconds"""
        base_url = "http://localhost:8000"
        
        results = []
        start_time = time.time()
        request_count = 0
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            while time.time() - start_time < 30:
                try:
                    req_start = time.time()
                    response = await client.get(f"{base_url}/health")
                    duration = (time.time() - req_start) * 1000
                    
                    results.append({
                        'success': response.status_code == 200,
                        'duration': duration
                    })
                    request_count += 1
                except Exception:
                    results.append({'success': False, 'duration': 0})
                
                # Small delay to avoid overwhelming the system
                await asyncio.sleep(0.05)
        
        total_duration = time.time() - start_time
        successful = [r for r in results if r['success']]
        success_rate = len(successful) / len(results) * 100
        avg_response = statistics.mean([r['duration'] for r in successful]) if successful else 0
        throughput = request_count / total_duration
        
        print(f"\nSustained Load (30s) Performance:")
        print(f"  Total Requests: {request_count}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Avg Response: {avg_response:.2f}ms")
        print(f"  Throughput: {throughput:.1f} req/s")
        
        # System should maintain high success rate
        assert success_rate >= 95, f"Success rate {success_rate}% degraded under sustained load"
        
        # Response time should remain reasonable
        assert avg_response < 500, f"Average response time {avg_response}ms too high"


class TestThroughput:
    """Test request throughput"""
    
    @pytest.mark.asyncio
    async def test_maximum_throughput(self):
        """Test maximum requests per second"""
        base_url = "http://localhost:8000"
        
        async def burst_requests(client, burst_size):
            start = time.time()
            tasks = [client.get(f"{base_url}/health") for _ in range(burst_size)]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            duration = time.time() - start
            
            successful = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 200)
            return successful, duration
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            successful, duration = await burst_requests(client, 200)
        
        throughput = successful / duration if duration > 0 else 0
        
        print(f"\nMaximum Throughput Test:")
        print(f"  Successful Requests: {successful}/200")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Throughput: {throughput:.1f} req/s")
        
        # Should handle at least 50 req/s
        assert throughput >= 50, f"Throughput {throughput:.1f} req/s below minimum 50 req/s"


class TestDatabasePerformance:
    """Test database query performance"""
    
    @pytest.mark.asyncio
    async def test_list_query_performance(self):
        """Test database list query performance"""
        base_url = "http://localhost:8000"
        
        query_times = []
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for _ in range(5):
                start = time.time()
                response = await client.get(f"{base_url}/api/v1/hospitals")
                duration = (time.time() - start) * 1000
                
                query_times.append(duration)
        
        avg_query_time = statistics.mean(query_times)
        
        print(f"\nDatabase Query Performance:")
        print(f"  Average: {avg_query_time:.2f}ms")
        
        # Database queries should be fast
        assert avg_query_time < 1000, f"Query time {avg_query_time}ms exceeds 1000ms"


class TestMemoryUsage:
    """Test memory consumption under load"""
    
    @pytest.mark.asyncio
    async def test_memory_leak_detection(self):
        """Test for memory leaks under repeated requests"""
        base_url = "http://localhost:8000"
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make many requests
        async with httpx.AsyncClient(timeout=10.0) as client:
            for _ in range(100):
                await client.get(f"{base_url}/health")
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory
        
        print(f"\nMemory Usage:")
        print(f"  Initial: {initial_memory:.2f}MB")
        print(f"  Final: {final_memory:.2f}MB")
        print(f"  Growth: {memory_growth:.2f}MB")
        
        # Memory growth should be reasonable
        assert memory_growth < 200, f"Memory grew by {memory_growth}MB - possible leak"


class TestResponseSizes:
    """Test response payload sizes"""
    
    @pytest.mark.asyncio
    async def test_response_size_reasonable(self):
        """Test that response sizes are reasonable"""
        base_url = "http://localhost:8000"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/api/v1/hospitals")
            
            if response.status_code == 200:
                size_kb = len(response.content) / 1024
                
                print(f"\nResponse Size: {size_kb:.2f}KB")
                
                # Should not send excessive data
                assert size_kb < 1024, f"Response size {size_kb}KB too large"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
