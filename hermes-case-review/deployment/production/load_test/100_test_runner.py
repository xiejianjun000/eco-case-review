#!/usr/bin/env python3
"""
HERMES Case Review System - Comprehensive Load Test
Performs 100 test runs with diverse case scenarios
"""

import sys
import os
import time
import random
import json
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.abspath('/workspace/hermes-case-review'))

try:
    from fastapi.testclient import TestClient
    from src.api.routes import app
    USING_TEST_CLIENT = True
    print("📦 Using FastAPI TestClient")
except ImportError:
    try:
        import requests
        USING_TEST_CLIENT = False
        BASE_URL = "http://localhost:8000"
        print("🌐 Using requests library")
    except ImportError:
        print("❌ Neither FastAPI TestClient nor requests library available")
        sys.exit(1)

# Import test cases
sys.path.insert(0, os.path.abspath('/workspace/hermes-case-review/test_data'))

try:
    from test_cases import TEST_CASES, CASE_TYPES
    print(f"✅ Loaded {len(TEST_CASES)} test cases")
except ImportError:
    # Fallback test cases if import fails
    TEST_CASES = [
        {
            "id": f"case_{i:03d}",
            "name": f"测试案例 {i}",
            "type": random.choice(["一般行政处罚", "不予行政处罚"]),
            "document_score": random.randint(60, 100),
            "document_standard": 100,
            "basic_deduction": random.randint(0, 6)
        } for i in range(15)
    ]
    print(f"⚠️ Created {len(TEST_CASES)} fallback test cases")


class LoadTestResults:
    """Collect and manage load test results"""
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
        
    def start(self):
        self.start_time = time.time()
        
    def stop(self):
        self.end_time = time.time()
        
    def add_result(self, result: Dict[str, Any]):
        self.results.append(result)
        
    def get_summary(self) -> Dict[str, Any]:
        if not self.results:
            return {}
            
        response_times = [r.get('response_time_ms', 0) for r in self.results if r.get('success')]
        scores = [r.get('score', 0) for r in self.results if r.get('success')]
        
        return {
            'total_tests': len(self.results),
            'successful_tests': sum(1 for r in self.results if r.get('success')),
            'failed_tests': sum(1 for r in self.results if not r.get('success')),
            'total_duration_seconds': (self.end_time - self.start_time) if (self.start_time and self.end_time) else 0,
            'average_response_time_ms': statistics.mean(response_times) if response_times else 0,
            'median_response_time_ms': statistics.median(response_times) if response_times else 0,
            'min_response_time_ms': min(response_times) if response_times else 0,
            'max_response_time_ms': max(response_times) if response_times else 0,
            'p95_response_time_ms': self.percentile(response_times, 95) if response_times else 0,
            'p99_response_time_ms': self.percentile(response_times, 99) if response_times else 0,
            'average_score': statistics.mean(scores) if scores else 0,
            'requests_per_second': len(self.results) / ((self.end_time - self.start_time) if (self.start_time and self.end_time) else 1)
        }
        
    @staticmethod
    def percentile(data: List[float], p: int) -> float:
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * (p / 100.0)
        f = int(k)
        c = k - f
        
        if f + 1 < len(sorted_data):
            return sorted_data[f] * (1 - c) + sorted_data[f + 1] * c
        return sorted_data[f]


def run_single_test(test_case: Dict[str, Any], test_id: int) -> Dict[str, Any]:
    """Run a single test case"""
    start_time = time.time()
    
    try:
        test_payload = {
            "case_id": test_case.get('id', f'case_{test_id:03d}'),
            "case_data": {
                "document_score": test_case.get('document_score', 85),
                "document_standard": test_case.get('document_standard', 100),
                "basic_deduction": test_case.get('basic_deduction', 2)
            },
            "case_type": test_case.get('type', "一般行政处罚")
        }
        
        if USING_TEST_CLIENT:
            client = TestClient(app)
            response = client.post("/api/v1/review", json=test_payload)
        else:
            response = requests.post(f"{BASE_URL}/api/v1/review", json=test_payload)
            
        response_time_ms = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            response_data = response.json()
            success = response_data.get('success', True)
            return {
                'test_id': test_id,
                'case_id': test_payload['case_id'],
                'case_name': test_case.get('name', 'Unknown'),
                'case_type': test_case.get('case_type', 'unknown'),
                'success': success,
                'status_code': response.status_code,
                'response_time_ms': response_time_ms,
                'score': response_data.get('comprehensive_score'),
                'grade': response_data.get('comprehensive_grade'),
                'passed': response_data.get('is_pass'),
                'details': response_data
            }
        else:
            return {
                'test_id': test_id,
                'case_id': test_payload['case_id'],
                'case_name': test_case.get('name', 'Unknown'),
                'case_type': test_case.get('case_type', 'unknown'),
                'success': False,
                'status_code': response.status_code,
                'response_time_ms': response_time_ms,
                'error': response.text
            }
            
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        return {
            'test_id': test_id,
            'case_id': test_case.get('id', f'case_{test_id:03d}'),
            'case_name': test_case.get('name', 'Unknown'),
            'success': False,
            'response_time_ms': response_time_ms,
            'error': str(e)
        }


def run_load_test(num_tests: int = 100, concurrent: int = 10) -> LoadTestResults:
    """
    Run comprehensive load test
    
    Args:
        num_tests: Total number of tests to run
        concurrent: Number of concurrent threads
    """
    print(f"\n{'='*80}")
    print(f"🚀 HERMES CASE REVIEW SYSTEM - LOAD TEST")
    print(f"{'='*80}")
    print(f"📊 Total tests: {num_tests}")
    print(f"🔄 Concurrency: {concurrent}")
    print(f"📦 Test cases: {len(TEST_CASES)}")
    print(f"{'='*80}\n")
    
    results = LoadTestResults()
    results.start()
    
    # Create test list with repeated test cases
    test_list = []
    for i in range(num_tests):
        test_case = TEST_CASES[i % len(TEST_CASES)].copy()
        test_case['id'] = f"test_{i+1:04d}_{test_case['id']}"
        test_list.append(test_case)
    
    with ThreadPoolExecutor(max_workers=concurrent) as executor:
        futures = {
            executor.submit(run_single_test, test_case, i+1): (test_case, i+1)
            for i, test_case in enumerate(test_list)
        }
        
        completed = 0
        for future in as_completed(futures):
            test_case, test_id = futures[future]
            try:
                result = future.result()
                results.add_result(result)
                completed += 1
                
                # Progress indicator
                status = "✅" if result.get('success') else "❌"
                time_ms = result.get('response_time_ms', 0)
                print(f"[{completed}/{num_tests}] {status} Test {test_id} - {result.get('case_name', 'Unknown')} ({time_ms:.1f}ms)", end='\r')
                
            except Exception as e:
                print(f"⚠️ Error in test {test_id}: {str(e)}")
    
    results.stop()
    
    print()  # New line after progress indicator
    
    return results


def print_results_summary(results: LoadTestResults):
    """Print results summary"""
    summary = results.get_summary()
    
    print(f"\n{'='*80}")
    print(f"📊 LOAD TEST RESULTS SUMMARY")
    print(f"{'='*80}")
    
    print(f"\n📈 Performance Metrics:")
    print(f"   Total Tests:     {summary.get('total_tests', 0)}")
    print(f"   Successful:      {summary.get('successful_tests', 0)} ✅")
    print(f"   Failed:          {summary.get('failed_tests', 0)} ❌")
    print(f"   Success Rate:    {100.0 * summary.get('successful_tests', 0) / max(summary.get('total_tests', 1), 1):.1f}%")
    
    print(f"\n⏱️ Response Times:")
    print(f"   Total Duration:  {summary.get('total_duration_seconds', 0):.2f}s")
    print(f"   Average:         {summary.get('average_response_time_ms', 0):.1f}ms")
    print(f"   Median:          {summary.get('median_response_time_ms', 0):.1f}ms")
    print(f"   Min:             {summary.get('min_response_time_ms', 0):.1f}ms")
    print(f"   Max:             {summary.get('max_response_time_ms', 0):.1f}ms")
    print(f"   95th Percentile: {summary.get('p95_response_time_ms', 0):.1f}ms")
    print(f"   99th Percentile: {summary.get('p99_response_time_ms', 0):.1f}ms")
    
    print(f"\n⚡ Throughput:")
    print(f"   Requests/sec:    {summary.get('requests_per_second', 0):.1f}")
    print(f"   Avg Score:       {summary.get('average_score', 0):.1f}")
    
    print(f"\n{'='*80}")
    
    success_rate = 100.0 * summary.get('successful_tests', 0) / max(summary.get('total_tests', 1), 1)
    if success_rate >= 95 and summary.get('p95_response_time_ms', 10000) < 1000:
        print(f"🎉 Overall Result: PASSED ✅")
    else:
        print(f"⚠️ Overall Result: Review Required")
    print(f"{'='*80}")


def save_results_to_file(results: LoadTestResults, filename: str = "load_test_report.json"):
    """Save results to JSON file"""
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
    
    output_data = {
        'test_info': {
            'test_datetime': datetime.now().isoformat(),
            'test_environment': 'Cloud Sandbox',
            'framework': 'HERMES Case Review System'
        },
        'summary': results.get_summary(),
        'detailed_results': results.results
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Results saved to: {filename}")
    
    # Save HTML report
    save_html_report(results, filename.replace('.json', '.html'))


def save_html_report(results: LoadTestResults, filename: str):
    """Save results as HTML report"""
    summary = results.get_summary()
    
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HERMES Case Review System - Load Test Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 30px;
            background-color: #f5f7fa;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
            padding: 40px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 20px;
        }}
        .header h1 {{
            color: #1e293b;
            margin: 0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 24px;
            border-radius: 12px;
            text-align: center;
        }}
        .stat-card.green {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        .stat-card.orange {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        .stat-card.blue {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            border: 1px solid #e2e8f0;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #f1f5f9;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background-color: #f8fafc;
        }}
        .status-pass {{
            color: #10b981;
            font-weight: bold;
        }}
        .status-fail {{
            color: #ef4444;
            font-weight: bold;
        }}
        .summary {{
            background: #f0fdf4;
            border-left: 4px solid #10b981;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 8px;
        }}
        .test-datetime {{
            text-align: right;
            color: #64748b;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ HERMES Case Review System</h1>
            <p style="color: #64748b; margin-top: 10px;">Load Test Report - 100 Tests</p>
            <div class="test-datetime">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="summary">
            <h2>📋 Test Summary</h2>
            <p><strong>Environment:</strong> Cloud Sandbox</p>
            <p><strong>Status:</strong> <span style="color: #10b981; font-weight: bold;">✅ ALL TESTS COMPLETED</span></p>
        </div>
        
        <h2>📊 Performance Statistics</h2>
        <div class="stats-grid">
            <div class="stat-card green">
                <div class="stat-value">{summary.get('successful_tests', 0)}</div>
                <div class="stat-label">Success Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary.get('average_response_time_ms', 0):.0f}ms</div>
                <div class="stat-label">Avg Response Time</div>
            </div>
            <div class="stat-card blue">
                <div class="stat-value">{summary.get('requests_per_second', 0):.1f}/s</div>
                <div class="stat-label">Requests per Second</div>
            </div>
            <div class="stat-card orange">
                <div class="stat-value">{summary.get('p99_response_time_ms', 0):.0f}ms</div>
                <div class="stat-label">99th Percentile</div>
            </div>
        </div>
        
        <h2>📈 Detailed Metrics</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Total Tests</td>
                <td>{summary.get('total_tests', 0)}</td>
            </tr>
            <tr>
                <td>Successful Tests</td>
                <td class="status-pass">{summary.get('successful_tests', 0)}</td>
            </tr>
            <tr>
                <td>Failed Tests</td>
                <td class="status-fail">{summary.get('failed_tests', 0)}</td>
            </tr>
            <tr>
                <td>Success Rate</td>
                <td>{100.0 * summary.get('successful_tests', 0) / max(summary.get('total_tests', 1), 1):.1f}%</td>
            </tr>
            <tr>
                <td>Total Duration</td>
                <td>{summary.get('total_duration_seconds', 0):.2f}s</td>
            </tr>
            <tr>
                <td>Average Response Time</td>
                <td>{summary.get('average_response_time_ms', 0):.1f}ms</td>
            </tr>
            <tr>
                <td>Median Response Time</td>
                <td>{summary.get('median_response_time_ms', 0):.1f}ms</td>
            </tr>
            <tr>
                <td>Min Response Time</td>
                <td>{summary.get('min_response_time_ms', 0):.1f}ms</td>
            </tr>
            <tr>
                <td>Max Response Time</td>
                <td>{summary.get('max_response_time_ms', 0):.1f}ms</td>
            </tr>
            <tr>
                <td>95th Percentile</td>
                <td>{summary.get('p95_response_time_ms', 0):.1f}ms</td>
            </tr>
            <tr>
                <td>99th Percentile</td>
                <td>{summary.get('p99_response_time_ms', 0):.1f}ms</td>
            </tr>
            <tr>
                <td>Throughput (Requests/Second)</td>
                <td>{summary.get('requests_per_second', 0):.1f}</td>
            </tr>
            <tr>
                <td>Average Case Score</td>
                <td>{summary.get('average_score', 0):.1f}</td>
            </tr>
        </table>
        
        <h2>📊 Case Type Distribution</h2>
        <table>
            <tr>
                <th>Case Type</th>
                <th>Count</th>
            </tr>
"""
    # Count case types
    type_counts = {}
    for r in results.results:
        case_type = r.get('case_type', 'unknown')
        type_counts[case_type] = type_counts.get(case_type, 0) + 1
    
    for case_type, count in sorted(type_counts.items()):
        html_content += f"""
            <tr>
                <td>{case_type}</td>
                <td>{count}</td>
            </tr>
"""
    
    html_content += """
        </table>
        
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; text-align: center; color: #64748b;">
            <p>Generated by HERMES Case Review System Load Test Framework</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📄 HTML report saved to: {filename}")


def main():
    """Main function"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='HERMES Case Review Load Tester')
    parser.add_argument('--tests', type=int, default=100, help='Number of tests (default: 100)')
    parser.add_argument('--concurrent', type=int, default=10, help='Concurrent threads (default: 10)')
    parser.add_argument('--output', type=str, default='/workspace/hermes-case-review/load_test_results/100_test_report', help='Output file base name')
    
    args = parser.parse_args()
    
    # Run load test
    results = run_load_test(args.tests, args.concurrent)
    
    # Print summary
    print_results_summary(results)
    
    # Save results
    save_results_to_file(results, f"{args.output}.json")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
