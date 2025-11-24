"""
Load Testing Script
Simulates realistic user traffic and measures system performance.
"""

import asyncio
import time
from typing import Dict, List
import statistics


class LoadTester:
    """
    Load testing utility for API endpoints.
    
    Features:
    - Concurrent user simulation
    - Request rate control
    - Performance metrics collection
    - Report generation
    """

    def __init__(self, target_url: str, auth_header: str = None):
        """
        Initialize load tester.
        
        Args:
            target_url: Base URL to test
            auth_header: Optional authentication header
        """
        self.target_url = target_url
        self.auth_header = auth_header
        self.results: List[Dict] = []

    async def make_request(self, endpoint: str = "/") -> Dict:
        """
        Make a single HTTP request and measure performance.
        
        Args:
            endpoint: API endpoint to test
            
        Returns:
            Request result dictionary
        """
        import aiohttp
        
        start_time = time.time()
        
        try:
            headers = {}
            if self.auth_header:
                headers["Authorization"] = self.auth_header
            
            url = f"{self.target_url}{endpoint}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    status = response.status
                    await response.text()
                    
                    duration = (time.time() - start_time) * 1000  # ms
                    
                    return {
                        "endpoint": endpoint,
                        "status": status,
                        "duration_ms": duration,
                        "success": status < 400,
                        "timestamp": time.time()
                    }
        except asyncio.TimeoutError:
            return {
                "endpoint": endpoint,
                "status": 0,
                "duration_ms": 30000,
                "success": False,
                "error": "timeout",
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "endpoint": endpoint,
                "status": 0,
                "duration_ms": (time.time() - start_time) * 1000,
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }

    async def simulate_user(self, user_id: int, requests_per_user: int, delay: float = 1.0):
        """
        Simulate a single user making multiple requests.
        
        Args:
            user_id: User identifier
            requests_per_user: Number of requests to make
            delay: Delay between requests in seconds
        """
        for i in range(requests_per_user):
            result = await self.make_request()
            result["user_id"] = user_id
            result["request_num"] = i + 1
            self.results.append(result)
            
            if i < requests_per_user - 1:
                await asyncio.sleep(delay)

    async def run_load_test(
        self,
        concurrent_users: int = 10,
        requests_per_user: int = 10,
        ramp_up_seconds: int = 0
    ) -> Dict:
        """
        Run load test with multiple concurrent users.
        
        Args:
            concurrent_users: Number of concurrent users
            requests_per_user: Requests per user
            ramp_up_seconds: Time to ramp up to full load
            
        Returns:
            Test results summary
        """
        print(f"\n🚀 Starting load test:")
        print(f"   Users: {concurrent_users}")
        print(f"   Requests per user: {requests_per_user}")
        print(f"   Total requests: {concurrent_users * requests_per_user}")
        print(f"   Ramp-up: {ramp_up_seconds}s\n")
        
        self.results.clear()
        start_time = time.time()
        
        # Create user simulation tasks
        tasks = []
        for user_id in range(concurrent_users):
            # Stagger user start times during ramp-up
            if ramp_up_seconds > 0:
                delay = (ramp_up_seconds / concurrent_users) * user_id
                await asyncio.sleep(delay)
            
            task = asyncio.create_task(
                self.simulate_user(user_id, requests_per_user, delay=1.0)
            )
            tasks.append(task)
        
        # Wait for all users to complete
        await asyncio.gather(*tasks)
        
        total_duration = time.time() - start_time
        
        # Calculate metrics
        return self.calculate_metrics(total_duration)

    def calculate_metrics(self, total_duration: float) -> Dict:
        """
        Calculate performance metrics from test results.
        
        Args:
            total_duration: Total test duration in seconds
            
        Returns:
            Metrics dictionary
        """
        if not self.results:
            return {"error": "No results to analyze"}
        
        successful = [r for r in self.results if r["success"]]
        failed = [r for r in self.results if not r["success"]]
        
        durations = [r["duration_ms"] for r in successful]
        
        metrics = {
            "test_summary": {
                "total_requests": len(self.results),
                "successful": len(successful),
                "failed": len(failed),
                "success_rate": len(successful) / len(self.results),
                "total_duration_seconds": total_duration,
            },
            "performance": {
                "min_response_ms": min(durations) if durations else 0,
                "max_response_ms": max(durations) if durations else 0,
                "avg_response_ms": statistics.mean(durations) if durations else 0,
                "median_response_ms": statistics.median(durations) if durations else 0,
                "p95_response_ms": self._percentile(durations, 0.95) if durations else 0,
                "p99_response_ms": self._percentile(durations, 0.99) if durations else 0,
            },
            "throughput": {
                "requests_per_second": len(self.results) / total_duration,
                "successful_rps": len(successful) / total_duration,
            }
        }
        
        return metrics

    @staticmethod
    def _percentile(data: List[float], percentile: float) -> float:
        """Calculate percentile value."""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]

    def print_report(self, metrics: Dict):
        """
        Print formatted test report.
        
        Args:
            metrics: Metrics dictionary
        """
        print("\n" + "=" * 60)
        print("LOAD TEST RESULTS")
        print("=" * 60)
        
        summary = metrics["test_summary"]
        print(f"\n📊 Test Summary:")
        print(f"   Total Requests:    {summary['total_requests']}")
        print(f"   Successful:        {summary['successful']} ({summary['success_rate']:.1%})")
        print(f"   Failed:            {summary['failed']}")
        print(f"   Duration:          {summary['total_duration_seconds']:.2f}s")
        
        perf = metrics["performance"]
        print(f"\n⚡ Performance Metrics:")
        print(f"   Min Response:      {perf['min_response_ms']:.2f}ms")
        print(f"   Max Response:      {perf['max_response_ms']:.2f}ms")
        print(f"   Avg Response:      {perf['avg_response_ms']:.2f}ms")
        print(f"   Median Response:   {perf['median_response_ms']:.2f}ms")
        print(f"   95th Percentile:   {perf['p95_response_ms']:.2f}ms")
        print(f"   99th Percentile:   {perf['p99_response_ms']:.2f}ms")
        
        throughput = metrics["throughput"]
        print(f"\n🔥 Throughput:")
        print(f"   Total RPS:         {throughput['requests_per_second']:.2f}")
        print(f"   Successful RPS:    {throughput['successful_rps']:.2f}")
        
        print("\n" + "=" * 60 + "\n")


# Example usage and test scenarios
async def main():
    """Run example load tests."""
    import os
    
    # Test Telegram Bot API
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if bot_token and not bot_token.startswith("PASTE_"):
        print("\n" + "=" * 60)
        print("TELEGRAM BOT LOAD TEST")
        print("=" * 60)
        
        tester = LoadTester(f"https://api.telegram.org/bot{bot_token}")
        
        # Light load test
        print("\n📌 Scenario 1: Light Load")
        metrics = await tester.run_load_test(
            concurrent_users=5,
            requests_per_user=5,
            ramp_up_seconds=2
        )
        tester.print_report(metrics)
        
        # Wait between tests
        await asyncio.sleep(5)
        
        # Normal load test
        print("\n📌 Scenario 2: Normal Load")
        metrics = await tester.run_load_test(
            concurrent_users=10,
            requests_per_user=10,
            ramp_up_seconds=5
        )
        tester.print_report(metrics)
    else:
        print("⚠️  TELEGRAM_BOT_TOKEN not configured, skipping load test")
        print("   Set environment variable to run load tests")


if __name__ == "__main__":
    print("\n🔥 Load Testing Tool for Top-TieR-Global-HUB-AI\n")
    asyncio.run(main())
