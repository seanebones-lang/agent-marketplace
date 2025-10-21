"""
Chaos Engineering Tests with Locust
Load testing and failure simulation for resilience validation
"""

import random
import time
from locust import HttpUser, task, between, events
from locust.exception import RescheduleTask
import logging

logger = logging.getLogger(__name__)


class AgentMarketplaceUser(HttpUser):
    """
    Simulates a user interacting with the Agent Marketplace Platform
    """
    
    # Wait time between tasks (1-5 seconds)
    wait_time = between(1, 5)
    
    # User credentials (would be loaded from config in production)
    api_key = "test-api-key-12345"
    
    def on_start(self):
        """Called when a user starts"""
        self.client.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        logger.info(f"User {self.user_id} started")
    
    def on_stop(self):
        """Called when a user stops"""
        logger.info(f"User {self.user_id} stopped")
    
    @task(5)
    def list_packages(self):
        """List available agent packages (high frequency)"""
        with self.client.get(
            "/api/v1/packages",
            catch_response=True,
            name="List Packages"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                # Rate limited - expected behavior
                response.success()
                logger.info("Rate limit hit - backing off")
                time.sleep(5)
            else:
                response.failure(f"Unexpected status: {response.status_code}")
    
    @task(3)
    def execute_agent(self):
        """Execute an agent package (medium frequency)"""
        packages = [
            "ticket-resolver",
            "knowledge-base",
            "data-processor",
            "report-generator"
        ]
        
        package_id = random.choice(packages)
        
        payload = {
            "task": f"Test task {random.randint(1, 1000)}",
            "config": {
                "timeout": 30,
                "priority": random.choice(["low", "medium", "high"])
            }
        }
        
        with self.client.post(
            f"/api/v1/packages/{package_id}/execute",
            json=payload,
            catch_response=True,
            name="Execute Agent",
            timeout=60
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                response.success()
                logger.info("Rate limit hit on execution")
                time.sleep(10)
            elif response.status_code == 503:
                # Service unavailable - circuit breaker open
                response.success()
                logger.warning("Circuit breaker open")
                time.sleep(5)
            else:
                response.failure(f"Execution failed: {response.status_code}")
    
    @task(2)
    def get_analytics(self):
        """Get analytics data (low frequency)"""
        with self.client.get(
            "/api/v1/analytics/overview",
            catch_response=True,
            name="Get Analytics"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                response.success()
            else:
                response.failure(f"Analytics failed: {response.status_code}")
    
    @task(2)
    def get_execution_history(self):
        """Get execution history"""
        with self.client.get(
            "/api/v1/history/executions?limit=10",
            catch_response=True,
            name="Get History"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"History failed: {response.status_code}")
    
    @task(1)
    def simulate_failure(self):
        """Simulate random failures for chaos testing"""
        failure_type = random.choice([
            "network_timeout",
            "invalid_request",
            "concurrent_limit"
        ])
        
        if failure_type == "network_timeout":
            # Simulate network timeout
            try:
                with self.client.get(
                    "/api/v1/packages",
                    timeout=0.001,  # Very short timeout
                    catch_response=True,
                    name="Simulated Timeout"
                ) as response:
                    response.failure("Simulated timeout")
            except Exception as e:
                logger.info(f"Expected timeout: {e}")
        
        elif failure_type == "invalid_request":
            # Send invalid request
            with self.client.post(
                "/api/v1/packages/invalid-package/execute",
                json={"invalid": "data"},
                catch_response=True,
                name="Simulated Invalid Request"
            ) as response:
                if response.status_code == 404:
                    response.success()  # Expected 404
                else:
                    response.failure(f"Unexpected status: {response.status_code}")
        
        elif failure_type == "concurrent_limit":
            # Try to exceed concurrent execution limit
            for _ in range(10):
                self.client.post(
                    "/api/v1/packages/ticket-resolver/execute",
                    json={"task": "concurrent test"},
                    name="Concurrent Execution Test"
                )


class HighLoadUser(HttpUser):
    """
    Simulates high-load scenarios
    """
    
    wait_time = between(0.1, 0.5)  # Very short wait time
    
    @task
    def rapid_fire_requests(self):
        """Rapid fire requests to test rate limiting"""
        for _ in range(20):
            self.client.get("/api/v1/packages", name="Rapid Fire")
            time.sleep(0.05)


class SpikeLoadUser(HttpUser):
    """
    Simulates traffic spikes
    """
    
    wait_time = between(0, 1)
    
    @task
    def spike_traffic(self):
        """Generate traffic spike"""
        burst_size = random.randint(10, 50)
        for _ in range(burst_size):
            self.client.get("/api/v1/health", name="Health Check Spike")


# Event listeners for custom metrics
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Track custom metrics"""
    if exception:
        logger.error(f"Request failed: {name} - {exception}")
    
    if response_time > 5000:  # 5 seconds
        logger.warning(f"Slow request: {name} took {response_time}ms")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts"""
    logger.info("=" * 80)
    logger.info("CHAOS ENGINEERING TEST STARTED")
    logger.info("=" * 80)
    logger.info(f"Target host: {environment.host}")
    logger.info(f"Users: {environment.runner.user_count if hasattr(environment.runner, 'user_count') else 'N/A'}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops"""
    logger.info("=" * 80)
    logger.info("CHAOS ENGINEERING TEST COMPLETED")
    logger.info("=" * 80)
    
    # Print statistics
    stats = environment.stats
    logger.info(f"Total requests: {stats.total.num_requests}")
    logger.info(f"Total failures: {stats.total.num_failures}")
    logger.info(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    logger.info(f"Max response time: {stats.total.max_response_time:.2f}ms")
    logger.info(f"Requests per second: {stats.total.total_rps:.2f}")
    
    # Calculate success rate
    if stats.total.num_requests > 0:
        success_rate = ((stats.total.num_requests - stats.total.num_failures) / 
                       stats.total.num_requests * 100)
        logger.info(f"Success rate: {success_rate:.2f}%")


# Custom load shapes for different test scenarios
from locust import LoadTestShape

class StepLoadShape(LoadTestShape):
    """
    Step load pattern: gradually increase load
    """
    step_time = 60  # 60 seconds per step
    step_load = 10  # Add 10 users per step
    spawn_rate = 5
    time_limit = 600  # 10 minutes total
    
    def tick(self):
        run_time = self.get_run_time()
        
        if run_time > self.time_limit:
            return None
        
        current_step = run_time // self.step_time
        user_count = (current_step + 1) * self.step_load
        
        return (user_count, self.spawn_rate)


class SpikeLoadShape(LoadTestShape):
    """
    Spike load pattern: sudden traffic spikes
    """
    time_limit = 300  # 5 minutes
    spawn_rate = 10
    
    def tick(self):
        run_time = self.get_run_time()
        
        if run_time > self.time_limit:
            return None
        
        # Create spikes every 60 seconds
        if run_time % 60 < 10:  # 10 second spike
            return (100, self.spawn_rate)
        else:
            return (10, self.spawn_rate)


# Run instructions
"""
To run chaos tests:

1. Basic load test:
   locust -f backend/tests/chaos_test.py --host=http://localhost:8000

2. Headless mode with specific users:
   locust -f backend/tests/chaos_test.py --host=http://localhost:8000 \\
          --users 100 --spawn-rate 10 --run-time 5m --headless

3. With step load shape:
   locust -f backend/tests/chaos_test.py --host=http://localhost:8000 \\
          --headless --users 100 --spawn-rate 5

4. High load test:
   locust -f backend/tests/chaos_test.py --host=http://localhost:8000 \\
          --users 500 --spawn-rate 50 --run-time 10m --headless

5. Spike test:
   locust -f backend/tests/chaos_test.py --host=http://localhost:8000 \\
          --users 200 --spawn-rate 100 --run-time 5m --headless

6. With web UI (default):
   locust -f backend/tests/chaos_test.py --host=http://localhost:8000
   # Then open http://localhost:8089
"""

