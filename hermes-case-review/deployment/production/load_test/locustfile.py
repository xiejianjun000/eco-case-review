"""
HERMES Case Review System - Load Testing Script
==============================================

This script performs comprehensive load testing on the HERMES Case Review System API.
It simulates realistic user behavior with various endpoints and workloads.

Usage:
    # Basic load test
    locust -f locustfile.py --host=http://localhost:8000

    # Distributed load test
    locust -f locustfile.py --host=http://localhost:8000 --master
    locust -f locustfile.py --host=http://localhost:8000 --worker --master-host=<master-ip>

    # Headless mode (for CI/CD)
    locust -f locustfile.py --host=http://localhost:8000 \
           --users 1000 --spawn-rate 10 --run-time 5m --headless \
           --html report.html --csv report
"""

import os
import random
import json
from datetime import datetime
from typing import Optional
from locust import (
    HttpUser,
    task,
    between,
    events,
    stats as locust_stats
)
from locust.runners import MasterRunner

# Configuration
API_HOST = os.getenv("LOCUST_HOST", "http://localhost:8000")
TEST_DURATION_MINUTES = int(os.getenv("TEST_DURATION", "5"))

# Case types supported by the system
CASE_TYPES = [
    "一般行政处罚",
    "不予行政处罚",
    "按日连续处罚",
    "查封扣押",
    "移送拘留",
    "移送涉嫌环境污染犯罪"
]

# Sample case data templates for realistic testing
SAMPLE_CASE_DATA = [
    {"document_score": 85, "document_standard": 100, "basic_deduction": 3},
    {"document_score": 92, "document_standard": 100, "basic_deduction": 1},
    {"document_score": 78, "document_standard": 100, "basic_deduction": 5},
    {"document_score": 95, "document_standard": 100, "basic_deduction": 0},
    {"document_score": 88, "document_standard": 100, "basic_deduction": 2},
    {"document_score": 72, "document_standard": 100, "basic_deduction": 4},
    {"document_score": 90, "document_standard": 100, "basic_deduction": 2},
    {"document_score": 65, "document_standard": 100, "basic_deduction": 6},
]

# Veto items simulation (mostly False for realistic testing)
VETO_SCENARIOS = [
    {},  # No veto
    {"veto_14": True},  # Procedural rights not informed
    {"veto_20": True},  # Exceeded statute oflimitations
    {"veto_1": True, "veto_14": True},  # Multiple vetoes
]


class ReviewUser(HttpUser):
    """
    Simulates a typical user performing case reviews.
    User behavior: Check health -> Review case -> Get standards occasionally
    """
    # Wait 0.1-0.5 seconds between tasks for realistic pacing
    wait_time = between(0.1, 0.5)

    def on_start(self):
        """Called when a simulated user starts. Initialize user session."""
        self.case_count = 0
        self.session_id = f"session_{random.randint(100000, 999999)}"
        
        # Warm up the API with a health check
        self.client.get("/health", name="/health [warmup]")

    @task(5)
    def review_case_standard(self):
        """
        Main task: Submit a case for review with standard case data.
        This is the most common operation.
        """
        self.case_count += 1
        case_id = f"case_{self.session_id}_{self.case_count}"
        
        payload = {
            "case_id": case_id,
            "case_data": random.choice(SAMPLE_CASE_DATA),
            "case_type": random.choice(CASE_TYPES)
        }
        
        with self.client.post(
            "/api/v1/review",
            json=payload,
            catch_response=True,
            name="/api/v1/review [standard]"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure(f"Review failed: {data}")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(2)
    def review_case_with_veto(self):
        """
        Task: Submit a case with potential veto conditions.
        Tests the system's ability to handle edge cases.
        """
        self.case_count += 1
        case_id = f"case_veto_{self.session_id}_{self.case_count}"
        
        # Create case data with potential veto
        base_data = random.choice(SAMPLE_CASE_DATA)
        veto_data = random.choice(VETO_SCENARIOS)
        case_data = {**base_data, **veto_data}
        
        payload = {
            "case_id": case_id,
            "case_data": case_data,
            "case_type": "一般行政处罚"
        }
        
        with self.client.post(
            "/api/v1/review",
            json=payload,
            catch_response=True,
            name="/api/v1/review [with_veto]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(3)
    def review_case_batch(self):
        """
        Task: Simulate batch case review (multiple rapid submissions).
        Tests system throughput under burst load.
        """
        batch_size = random.randint(3, 8)
        
        for i in range(batch_size):
            self.case_count += 1
            case_id = f"batch_{self.session_id}_{self.case_count}_{i}"
            
            payload = {
                "case_id": case_id,
                "case_data": random.choice(SAMPLE_CASE_DATA),
                "case_type": random.choice(CASE_TYPES)
            }
            
            self.client.post(
                "/api/v1/review",
                json=payload,
                name="/api/v1/review [batch]"
            )

    @task(2)
    def health_check(self):
        """
        Task: Check API health status.
        Lightweight operation for load testing infrastructure.
        """
        with self.client.get("/health", name="/health") as response:
            if response.status_code == 200:
                # Verify health response
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    response.failure(f"Unhealthy status: {data}")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(1)
    def get_legality_standards(self):
        """
        Task: Fetch legality review standards.
        Occasional operation to test metadata endpoints.
        """
        with self.client.get(
            "/api/v1/standards/legality",
            name="/api/v1/standards/legality"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(1)
    def get_normative_standards(self):
        """
        Task: Fetch normative scoring standards.
        Occasional operation to test metadata endpoints.
        """
        with self.client.get(
            "/api/v1/standards/normative",
            name="/api/v1/standards/normative"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(2)
    def calculate_score(self):
        """
        Task: Calculate score with given parameters.
        Tests the scoring calculation endpoint.
        """
        params = {
            "legality_score": random.choice([0, 50]),
            "document_score": random.randint(60, 100),
            "document_standard": 100,
            "basic_deduction": random.randint(0, 6)
        }
        
        with self.client.get(
            "/api/v1/calculate",
            params=params,
            name="/api/v1/calculate"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(1)
    def root_endpoint(self):
        """
        Task: Access root endpoint.
        Tests basic connectivity.
        """
        with self.client.get("/", name="/") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    def on_stop(self):
        """Called when a simulated user stops. Log session summary."""
        print(f"User {self.session_id} completed {self.case_count} case reviews")


class HeavyLoadUser(HttpUser):
    """
    Simulates power users who submit cases rapidly.
    Used to stress test the system under heavy load.
    """
    wait_time = between(0.01, 0.1)  # Very short wait for stress testing

    @task
    def rapid_review_submission(self):
        """Submit case reviews as fast as possible."""
        case_id = f"stress_{random.randint(1000000, 9999999)}"
        
        payload = {
            "case_id": case_id,
            "case_data": {
                "document_score": random.randint(60, 100),
                "document_standard": 100,
                "basic_deduction": random.randint(0, 6)
            },
            "case_type": "一般行政处罚"
        }
        
        self.client.post("/api/v1/review", json=payload, name="/api/v1/review [stress]")


class ApiInfoUser(HttpUser):
    """
    Simulates users browsing API documentation.
    Lightweight operations to test informational endpoints.
    """
    wait_time = between(0.5, 1.5)

    @task
    def get_all_standards(self):
        """Fetch all standards endpoints."""
        endpoints = [
            "/api/v1/standards/legality",
            "/api/v1/standards/normative"
        ]
        
        for endpoint in endpoints:
            self.client.get(endpoint, name=endpoint)


# Event handlers for custom logging
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the load test starts."""
    print(f"""
    ============================================
    HERMES Case Review System - Load Test Started
    ============================================
    Host: {API_HOST}
    Duration: {TEST_DURATION_MINUTES} minutes
    ============================================
    """)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the load test stops. Generate summary report."""
    print("""
    ============================================
    HERMES Case Review System - Load Test Complete
    ============================================
    """)
    
    # Print summary statistics
    stats = environment.stats
    
    print(f"Total Requests: {stats.total.num_requests}")
    print(f"Total failures: {stats.total.num_failures}")
    print(f"Median Response Time: {stats.total.median_response_time}ms")
    print(f"95th Percentile: {stats.total.get_response_time_percentile(0.95)}ms")
    print(f"99th Percentile: {stats.total.get_response_time_percentile(0.99)}ms}")
    print(f"Requests/sec: {stats.total.total_rps:.2f}")
    print("""
    ============================================
    """)


# Custom stats writer for detailed CSV reports
def setup_csv_reporting():
    """
    Configure Locust to generate detailed CSV reports.
    """
    # Ensure CSV reports are written
    locust_stats.CSV_STATS_INTERVAL_SEC = 5
    locust_stats.STATS_NAME_WIDTH = 60


if __name__ == "__main__":
    # This allows running the file directly for testing
    import argparse
    
    parser = argparse.ArgumentParser(description="HERMES Case Review Load Test")
    parser.add_argument("--host", default=API_HOST, help="Target host URL")
    parser.add_argument("--users", type=int, default=100, help="Number of concurrent users")
    parser.add_argument("--spawn-rate", type=int, default=10, help="User spawn rate")
    parser.add_argument("--duration", type=int, default=TEST_DURATION_MINUTES, help="Test duration in minutes")
    
    args = parser.parse_args()
    
    print(f"Load test configuration:")
    print(f"  Host: {args.host}")
    print(f"  Users: {args.users}")
    print(f"  Spawn rate: {args.spawn_rate}")
    print(f"  Duration: {args.duration} minutes")
