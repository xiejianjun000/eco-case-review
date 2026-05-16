#!/usr/bin/env python3
"""
HERMES Case Review System - Load Testing Script
==============================================

Comprehensive load testing for the HERMES Case Review System API.
Tests various endpoints under different load conditions.

Usage:
    # Light load test (10 users, 1 minute)
    python load_test_runner.py --users 10 --spawn-rate 5 --duration 60 --name light

    # Medium load test (50 users, 1 minute)
    python load_test_runner.py --users 50 --spawn-rate 10 --duration 60 --name medium

    # Heavy load test (100 users, 1 minute)
    python load_test_runner.py --users 100 --spawn-rate 20 --duration 60 --name heavy

    # Custom test
    python load_test_runner.py --users 200 --spawn-rate 50 --duration 120 --name custom
"""

import os
import sys
import time
import json
import random
import subprocess
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from typing import Dict, List, Optional

# API Configuration
API_HOST = os.getenv("API_HOST", "http://localhost:8000")
TEST_OUTPUT_DIR = "./load_test_results"

# Case types supported by the system
CASE_TYPES = [
    "一般行政处罚",
    "不予行政处罚",
    "按日连续处罚",
    "查封扣押",
    "移送拘留",
    "移送涉嫌环境污染犯罪"
]

# Sample case data templates
SAMPLE_CASE_DATA = [
    {"document_score": 85, "document_standard": 100, "basic_deduction": 3},
    {"document_score": 92, "document_standard": 100, "basic_deduction": 1},
    {"document_score": 78, "document_standard": 100, "basic_deduction": 5},
    {"document_score": 95, "document_standard": 100, "basic_deduction": 0},
    {"document_score": 88, "document_standard": 100, "basic_deduction": 2},
    {"document_score": 72, "document_standard": 100, "basic_deduction": 4},
]


class LoadTestRunner:
    """Load test runner for HERMES Case Review System"""

    def __init__(self, host: str, output_dir: str):
        self.host = host
        self.output_dir = output_dir
        self.results = []
        os.makedirs(output_dir, exist_ok=True)

    def test_endpoint(self, name: str, method: str = "GET",
                      path: str = "/", data: Optional[Dict] = None) -> Dict:
        """Test a single endpoint"""
        url = f"{self.host}{path}"
        start_time = time.time()

        try:
            if method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            elapsed = (time.time() - start_time) * 1000  # ms

            return {
                "name": name,
                "endpoint": path,
                "method": method,
                "status_code": response.status_code,
                "response_time_ms": elapsed,
                "success": response.status_code == 200,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            return {
                "name": name,
                "endpoint": path,
                "method": method,
                "status_code": 0,
                "response_time_ms": elapsed,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def run_load_test(self, users: int, spawn_rate: int,
                     duration_seconds: int, test_name: str) -> Dict:
        """Run load test with specified parameters"""
        print(f"\n{'='*60}")
        print(f"Starting Load Test: {test_name}")
        print(f"Users: {users}, Spawn Rate: {spawn_rate}/s, Duration: {duration_seconds}s")
        print(f"{'='*60}\n")

        results = []
        start_time = time.time()
        request_count = 0
        error_count = 0

        # Calculate spawn interval
        spawn_interval = 1.0 / spawn_rate if spawn_rate > 0 else 0

        with ThreadPoolExecutor(max_workers=users) as executor:
            futures = []

            while time.time() - start_time < duration_seconds:
                # Submit review requests
                for _ in range(min(spawn_rate, users)):
                    if time.time() - start_time < duration_seconds:
                        future = executor.submit(
                            self._perform_review_request,
                            f"review_{request_count}"
                        )
                        futures.append(future)
                        request_count += 1

                # Small delay between spawns
                time.sleep(spawn_interval)

                # Check completed futures
                completed = [f for f in futures if f.done()]
                for f in completed:
                    try:
                        result = f.result()
                        results.append(result)
                        if not result["success"]:
                            error_count += 1
                    except Exception as e:
                        error_count += 1
                        results.append({
                            "success": False,
                            "error": str(e),
                            "timestamp": datetime.now().isoformat()
                        })

                futures = [f for f in futures if not f.done()]

            # Wait for remaining futures
            for future in futures:
                try:
                    result = future.result()
                    results.append(result)
                    if not result["success"]:
                        error_count += 1
                except Exception as e:
                    error_count += 1
                    results.append({
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })

        # Calculate statistics
        total_time = time.time() - start_time
        success_count = sum(1 for r in results if r["success"])
        response_times = [r["response_time_ms"] for r in results if r["success"]]

        stats = {
            "test_name": test_name,
            "start_time": datetime.fromtimestamp(start_time).isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": total_time,
            "total_requests": request_count,
            "successful_requests": success_count,
            "failed_requests": error_count,
            "success_rate": (success_count / request_count * 100) if request_count > 0 else 0,
            "requests_per_second": request_count / total_time if total_time > 0 else 0,
            "response_times": {
                "min_ms": min(response_times) if response_times else 0,
                "max_ms": max(response_times) if response_times else 0,
                "avg_ms": sum(response_times) / len(response_times) if response_times else 0,
                "median_ms": sorted(response_times)[len(response_times)//2] if response_times else 0,
                "p95_ms": sorted(response_times)[int(len(response_times)*0.95)] if response_times else 0,
                "p99_ms": sorted(response_times)[int(len(response_times)*0.99)] if response_times else 0,
            },
            "results": results
        }

        # Save results
        output_file = f"{self.output_dir}/{test_name}_results.json"
        with open(output_file, "w") as f:
            json.dump(stats, f, indent=2)

        # Print summary
        self._print_summary(stats)

        return stats

    def _perform_review_request(self, name: str) -> Dict:
        """Perform a single review request"""
        payload = {
            "case_id": f"load_test_{name}_{random.randint(1000, 9999)}",
            "case_data": random.choice(SAMPLE_CASE_DATA),
            "case_type": random.choice(CASE_TYPES)
        }
        return self.test_endpoint(name, "POST", "/api/v1/review", payload)

    def _print_summary(self, stats: Dict):
        """Print test summary"""
        print(f"\n{'='*60}")
        print(f"Load Test Summary: {stats['test_name']}")
        print(f"{'='*60}")
        print(f"Duration:           {stats['duration_seconds']:.2f}s")
        print(f"Total Requests:     {stats['total_requests']}")
        print(f"Successful:         {stats['successful_requests']}")
        print(f"Failed:             {stats['failed_requests']}")
        print(f"Success Rate:       {stats['success_rate']:.2f}%")
        print(f"Requests/sec:       {stats['requests_per_second']:.2f}")
        print(f"\nResponse Times:")
        print(f"  Min:              {stats['response_times']['min_ms']:.2f}ms")
        print(f"  Max:              {stats['response_times']['max_ms']:.2f}ms")
        print(f"  Average:          {stats['response_times']['avg_ms']:.2f}ms")
        print(f"  Median:           {stats['response_times']['median_ms']:.2f}ms")
        print(f"  95th Percentile:  {stats['response_times']['p95_ms']:.2f}ms")
        print(f"  99th Percentile:  {stats['response_times']['p99_ms']:.2f}ms")
        print(f"{'='*60}\n")

    def test_all_endpoints(self) -> Dict:
        """Test all API endpoints"""
        print(f"\n{'='*60}")
        print("Testing All API Endpoints")
        print(f"{'='*60}\n")

        endpoints = [
            ("root", "GET", "/"),
            ("health", "GET", "/health"),
            ("legality_standards", "GET", "/api/v1/standards/legality"),
            ("normative_standards", "GET", "/api/v1/standards/normative"),
            ("calculate", "GET", "/api/v1/calculate?legality_score=50&document_score=85"),
            ("review", "POST", "/api/v1/review", {
                "case_id": "endpoint_test",
                "case_data": {"document_score": 85, "document_standard": 100, "basic_deduction": 3},
                "case_type": "一般行政处罚"
            })
        ]

        results = []
        for name, method, path, *data in endpoints:
            result = self.test_endpoint(
                name, method, path, data[0] if data else None
            )
            results.append(result)
            status = "✓" if result["success"] else "✗"
            print(f"{status} {method} {path} - {result['response_time_ms']:.2f}ms")

        print(f"\n{'='*60}")
        print(f"Endpoints tested: {len(results)}")
        print(f"Successful: {sum(1 for r in results if r['success'])}")
        print(f"{'='*60}\n")

        return {"endpoints": results}


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="HERMES Case Review System - Load Testing Tool"
    )
    parser.add_argument(
        "--host", default=API_HOST,
        help="API host URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--users", type=int, default=10,
        help="Number of concurrent users (default: 10)"
    )
    parser.add_argument(
        "--spawn-rate", type=int, default=5,
        help="User spawn rate per second (default: 5)"
    )
    parser.add_argument(
        "--duration", type=int, default=60,
        help="Test duration in seconds (default: 60)"
    )
    parser.add_argument(
        "--name", default="test",
        help="Test name for output files (default: test)"
    )
    parser.add_argument(
        "--test-endpoints-only", action="store_true",
        help="Only test endpoints without load test"
    )
    parser.add_argument(
        "--output-dir", default=TEST_OUTPUT_DIR,
        help="Output directory for test results"
    )

    args = parser.parse_args()

    runner = LoadTestRunner(args.host, args.output_dir)

    # Test all endpoints first
    runner.test_all_endpoints()

    if not args.test_endpoints_only:
        # Run load test
        stats = runner.run_load_test(
            users=args.users,
            spawn_rate=args.spawn_rate,
            duration_seconds=args.duration,
            test_name=args.name
        )

        # Generate HTML report
        generate_html_report(runner.output_dir, args.name)

        print(f"\nResults saved to: {runner.output_dir}")
        print(f"HTML report: {runner.output_dir}/{args.name}_report.html")


def generate_html_report(output_dir: str, test_name: str):
    """Generate HTML report from test results"""
    results_file = f"{output_dir}/{test_name}_results.json"

    if not os.path.exists(results_file):
        print("No results file found, skipping HTML report generation")
        return

    with open(results_file, "r") as f:
        data = json.load(f)

    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HERMES Case Review System - Load Test Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }}
        .metric-label {{
            color: #7f8c8d;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        .success {{
            color: #27ae60;
        }}
        .error {{
            color: #e74c3c;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏛️ HERMES Case Review System - Load Test Report</h1>
        <p class="timestamp">Test Name: {data['test_name']}</p>
        <p class="timestamp">Start Time: {data['start_time']}</p>
        <p class="timestamp">End Time: {data['end_time']}</p>

        <h2>📊 Test Summary</h2>
        <div class="summary">
            <div class="metric">
                <div class="metric-value">{data['total_requests']}</div>
                <div class="metric-label">Total Requests</div>
            </div>
            <div class="metric">
                <div class="metric-value">{data['successful_requests']}</div>
                <div class="metric-label">Successful</div>
            </div>
            <div class="metric">
                <div class="metric-value">{data['failed_requests']}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric">
                <div class="metric-value">{data['success_rate']:.1f}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
            <div class="metric">
                <div class="metric-value">{data['requests_per_second']:.2f}</div>
                <div class="metric-label">Requests/sec</div>
            </div>
            <div class="metric">
                <div class="metric-value">{data['duration_seconds']:.1f}s</div>
                <div class="metric-label">Duration</div>
            </div>
        </div>

        <h2>⏱️ Response Times</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value (ms)</th>
            </tr>
            <tr>
                <td>Minimum</td>
                <td>{data['response_times']['min_ms']:.2f}</td>
            </tr>
            <tr>
                <td>Maximum</td>
                <td>{data['response_times']['max_ms']:.2f}</td>
            </tr>
            <tr>
                <td>Average</td>
                <td>{data['response_times']['avg_ms']:.2f}</td>
            </tr>
            <tr>
                <td>Median</td>
                <td>{data['response_times']['median_ms']:.2f}</td>
            </tr>
            <tr>
                <td>95th Percentile</td>
                <td>{data['response_times']['p95_ms']:.2f}</td>
            </tr>
            <tr>
                <td>99th Percentile</td>
                <td>{data['response_times']['p99_ms']:.2f}</td>
            </tr>
        </table>

        <h2>📝 Sample Results</h2>
        <table>
            <tr>
                <th>Name</th>
                <th>Endpoint</th>
                <th>Status</th>
                <th>Response Time</th>
            </tr>
"""

    for result in data['results'][:50]:  # Show first 50 results
        status_class = "success" if result['success'] else "error"
        status_text = "✓" if result['success'] else "✗"
        html += f"""
            <tr>
                <td>{result['name']}</td>
                <td>{result['endpoint']}</td>
                <td class="{status_class}">{status_text} {result.get('status_code', 'N/A')}</td>
                <td>{result['response_time_ms']:.2f}ms</td>
            </tr>
"""

    html += """
        </table>

        <footer style="margin-top: 40px; text-align: center; color: #7f8c8d;">
            <p>Generated by HERMES Case Review System Load Testing Tool</p>
        </footer>
    </div>
</body>
</html>
"""

    report_file = f"{output_dir}/{test_name}_report.html"
    with open(report_file, "w") as f:
        f.write(html)

    print(f"HTML report generated: {report_file}")


if __name__ == "__main__":
    main()
