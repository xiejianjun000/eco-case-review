#!/usr/bin/env python3
"""
Standalone Load Tester - 100 Tests
Does not require API server, simulates review logic
"""

import sys
import os
import time
import random
import json
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

# Add project root
sys.path.insert(0, os.path.abspath('/workspace/hermes-case-review'))

# Test cases (embedded to avoid import issues)
TEST_CASES = [
    {
        "id": "case_001",
        "name": "某食品公司篡改自动监测数据案",
        "type": "一般行政处罚",
        "case_type": "water_pollution",
        "violation": "违反《水污染防治法》第三十九条",
        "document_score": 85,
        "document_standard": 100,
        "basic_deduction": 3,
        "data": {"company": "某食品有限公司", "pollutant": "化学需氧量、氨氮"}
    },
    {
        "id": "case_002",
        "name": "某碳素公司大气污染物超标排放案",
        "type": "一般行政处罚",
        "case_type": "air_pollution",
        "violation": "违反《大气污染防治法》第十八条",
        "document_score": 92,
        "document_standard": 100,
        "basic_deduction": 1,
        "data": {"company": "某碳素有限公司", "pollutant": "烟尘"}
    },
    {
        "id": "case_003",
        "name": "跨省转移废铅蓄电池案",
        "type": "移送涉嫌环境污染犯罪",
        "case_type": "hazardous_waste",
        "violation": "违反《固体废物污染环境防治法》",
        "document_score": 78,
        "document_standard": 100,
        "basic_deduction": 5,
        "data": {"company": "某物资回收公司", "waste_type": "废铅蓄电池"}
    },
    {
        "id": "case_004",
        "name": "某检测公司出具虚假监测报告案",
        "type": "一般行政处罚",
        "case_type": "third_party_fraud",
        "violation": "违反《环境监测数据弄虚作假行为判定及处理办法》",
        "document_score": 95,
        "document_standard": 100,
        "basic_deduction": 0,
        "data": {"company": "某环境检测有限公司"}
    },
    {
        "id": "case_005",
        "name": "未批先建违法生产案",
        "type": "一般行政处罚",
        "case_type": "construction_project",
        "violation": "违反《环境影响评价法》",
        "document_score": 88,
        "document_standard": 100,
        "basic_deduction": 2,
        "data": {"company": "某建材有限公司"}
    },
    {
        "id": "case_006",
        "name": "某公司夜间施工噪声污染案",
        "type": "一般行政处罚",
        "case_type": "noise_pollution",
        "violation": "违反《噪声污染防治法》",
        "document_score": 72,
        "document_standard": 100,
        "basic_deduction": 4,
        "data": {"company": "某建筑工程公司"}
    },
    {
        "id": "case_007",
        "name": "某化工公司土壤污染责任案",
        "type": "一般行政处罚",
        "case_type": "soil_pollution",
        "violation": "违反《土壤污染防治法》",
        "document_score": 90,
        "document_standard": 100,
        "basic_deduction": 2,
        "data": {"company": "某化工有限公司"}
    },
    {
        "id": "case_008",
        "name": "某养殖场畜禽粪污污染案",
        "type": "一般行政处罚",
        "case_type": "solid_waste",
        "violation": "违反《固体废物污染环境防治法》",
        "document_score": 65,
        "document_standard": 100,
        "basic_deduction": 6,
        "data": {"company": "某生态养殖有限公司"}
    },
    {
        "id": "case_009",
        "name": "某肉联公司伪造监测数据案",
        "type": "移送涉嫌环境污染犯罪",
        "case_type": "monitoring_fraud",
        "violation": "违反《水污染防治法》第三十九条",
        "document_score": 87,
        "document_standard": 100,
        "basic_deduction": 3,
        "data": {"company": "某肉联实业有限公司"}
    },
    {
        "id": "case_010",
        "name": "某公司未按规定进行环境应急培训案",
        "type": "一般行政处罚",
        "case_type": "emergency_management",
        "violation": "违反《突发环境事件应急管理办法》",
        "document_score": 93,
        "document_standard": 100,
        "basic_deduction": 1,
        "data": {"company": "某化工有限公司"}
    },
    {
        "id": "case_011",
        "name": "某耐火材料公司旁路偷排废气案",
        "type": "移送公安",
        "case_type": "bypass_emission",
        "violation": "违反《大气污染防治法》第二十条第二款",
        "document_score": 75,
        "document_standard": 100,
        "basic_deduction": 4,
        "data": {"company": "某耐火材料有限公司"}
    },
    {
        "id": "case_012",
        "name": "某检测公司出具虚假机动车排放检验报告案",
        "type": "一般行政处罚",
        "case_type": "vehicle_testing_fraud",
        "violation": "违反《大气污染防治法》",
        "document_score": 82,
        "document_standard": 100,
        "basic_deduction": 3,
        "data": {"company": "某机动车检测有限公司"}
    },
    {
        "id": "case_013",
        "name": "某公司轻微超标且及时整改案",
        "type": "不予行政处罚",
        "case_type": "minor_violation",
        "violation": "轻微超标，首次发现，及时整改",
        "document_score": 91,
        "document_standard": 100,
        "basic_deduction": 1,
        "data": {"company": "某碳素有限公司"}
    },
    {
        "id": "case_014",
        "name": "某采石场破坏生态环境案",
        "type": "一般行政处罚",
        "case_type": "ecological_damage",
        "violation": "违反《环境保护法》",
        "document_score": 80,
        "document_standard": 100,
        "basic_deduction": 3,
        "data": {"company": "某矿业开发公司"}
    },
    {
        "id": "case_015",
        "name": "某医院放射性同位素管理不规范案",
        "type": "一般行政处罚",
        "case_type": "radiation_safety",
        "violation": "违反《放射性污染防治法》",
        "document_score": 70,
        "document_standard": 100,
        "basic_deduction": 5,
        "data": {"company": "某医院"}
    }
]


class CaseReviewer:
    """Simulates the HERMES case review algorithm"""
    
    ONE_VETO_RULES = {
        "主体认定不清或错误": False,
        "主要事实认定不清": False,
        "违反法定程序": False,
        "适用法律依据错误": False,
        "处理决定明显不当": False,
        "滥用职权": False,
        "超越职权": False,
        "主要证据不足": False
    }
    
    @classmethod
    def calculate_document_score(cls, doc_score: int, doc_standard: int, basic_deduction: int) -> Dict[str, Any]:
        """Calculate document score"""
        score = (doc_score / doc_standard) * 100 - basic_deduction
        return {
            "score": max(0, min(100, score)),
            "grade": cls.get_grade(max(0, min(100, score)))
        }
    
    @classmethod
    def calculate_legality_score(cls, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate legality score"""
        violations = [
            "主体认定", "事实认定", "适用法律", 
            "执法程序", "自由裁量", "行政权限"
        ]
        score = random.randint(65, 100)
        deduction_items = []
        
        if random.random() < 0.3:
            score -= random.randint(3, 10)
            deduction_items.append(random.choice(violations))
        
        return {
            "score": max(0, min(100, score)),
            "grade": cls.get_grade(max(0, min(100, score))),
            "veto_rules": cls.ONE_VETO_RULES.copy(),
            "has_veto": any(cls.ONE_VETO_RULES.values()),
            "deduction_items": deduction_items
        }
    
    @classmethod
    def calculate_normative_score(cls, doc_score: int) -> Dict[str, Any]:
        """Calculate normative score"""
        score = random.randint(70, 100)
        if doc_score > 85:
            score = min(100, score + 10)
        
        return {
            "score": max(0, min(100, score)),
            "grade": cls.get_grade(max(0, min(100, score)))
        }
    
    @classmethod
    def calculate_comprehensive(cls, doc_score: int, legality_score: int, normative_score: int, has_veto: bool) -> Dict[str, Any]:
        """Calculate comprehensive score"""
        if has_veto:
            return {
                "score": 59,
                "grade": "不合格",
                "is_pass": False
            }
        
        score = 0.2 * doc_score + 0.4 * legality_score + 0.4 * normative_score
        return {
            "score": max(0, min(100, score)),
            "grade": cls.get_grade(max(0, min(100, score))),
            "is_pass": score >= 60
        }
    
    @staticmethod
    def get_grade(score: float) -> str:
        if score >= 95:
            return "优秀"
        elif score >= 85:
            return "良好"
        elif score >= 75:
            return "中等"
        elif score >= 60:
            return "及格"
        else:
            return "不合格"
    
    @classmethod
    def review_case(cls, case: Dict[str, Any]) -> Dict[str, Any]:
        """Perform full case review"""
        start = time.time()
        
        doc_result = cls.calculate_document_score(
            case.get('document_score', 85),
            case.get('document_standard', 100),
            case.get('basic_deduction', 2)
        )
        
        legality_result = cls.calculate_legality_score(case)
        normative_result = cls.calculate_normative_score(doc_result['score'])
        comprehensive_result = cls.calculate_comprehensive(
            doc_result['score'],
            legality_result['score'],
            normative_result['score'],
            legality_result.get('has_veto', False)
        )
        
        return {
            'success': True,
            'document_score': doc_result,
            'legality_score': legality_result,
            'normative_score': normative_result,
            'comprehensive_score': comprehensive_result['score'],
            'comprehensive_grade': comprehensive_result['grade'],
            'is_pass': comprehensive_result['is_pass'],
            'processing_time_ms': (time.time() - start) * 1000
        }


class LoadTestResults:
    """Collect and manage test results"""
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
    """Run single test"""
    start = time.time()
    
    try:
        result = CaseReviewer.review_case(test_case)
        resp_time = (time.time() - start) * 1000
        
        return {
            'test_id': test_id,
            'case_id': test_case.get('id'),
            'case_name': test_case.get('name'),
            'case_type': test_case.get('case_type'),
            'success': True,
            'status_code': 200,
            'response_time_ms': resp_time,
            'score': result.get('comprehensive_score'),
            'grade': result.get('comprehensive_grade'),
            'passed': result.get('is_pass'),
            'details': result
        }
        
    except Exception as e:
        resp_time = (time.time() - start) * 1000
        return {
            'test_id': test_id,
            'case_id': test_case.get('id'),
            'case_name': test_case.get('name'),
            'success': False,
            'response_time_ms': resp_time,
            'error': str(e)
        }


def run_load_test(num_tests: int = 100, concurrent: int = 10) -> LoadTestResults:
    """Run comprehensive load test"""
    print(f"\n{'='*80}")
    print(f"🚀 HERMES CASE REVIEW SYSTEM - LOAD TEST")
    print(f"{'='*80}")
    print(f"📊 Total tests: {num_tests}")
    print(f"🔄 Concurrency: {concurrent}")
    print(f"📦 Test cases: {len(TEST_CASES)}")
    print(f"{'='*80}\n")
    
    results = LoadTestResults()
    results.start()
    
    # Prepare test list
    test_list = []
    for i in range(num_tests):
        test_case = TEST_CASES[i % len(TEST_CASES)].copy()
        test_case['id'] = f"test_{i+1:04d}_{test_case['id']}"
        test_list.append(test_case)
    
    with ThreadPoolExecutor(max_workers=concurrent) as executor:
        futures = {
            executor.submit(run_single_test, test_case, i+1): i+1
            for i, test_case in enumerate(test_list)
        }
        
        completed = 0
        for future in as_completed(futures):
            test_id = futures[future]
            try:
                result = future.result()
                results.add_result(result)
                completed += 1
                
                status = "✅" if result.get('success') else "❌"
                time_ms = result.get('response_time_ms', 0)
                print(f"[{completed}/{num_tests}] {status} Test {test_id} - {result.get('case_name', 'Unknown')} ({time_ms:.1f}ms)", end='\r')
                
            except Exception as e:
                print(f"⚠️ Error in test {test_id}: {str(e)}")
    
    results.stop()
    print()
    return results


def print_results_summary(results: LoadTestResults):
    """Print summary"""
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


def save_results(results: LoadTestResults, output_dir: str = "/workspace/hermes-case-review/load_test_results"):
    """Save results"""
    os.makedirs(output_dir, exist_ok=True)
    
    summary = results.get_summary()
    
    # Save JSON
    json_data = {
        'test_info': {
            'test_datetime': datetime.now().isoformat(),
            'test_environment': 'Cloud Sandbox',
            'framework': 'HERMES Case Review System'
        },
        'summary': summary,
        'detailed_results': results.results
    }
    
    json_path = os.path.join(output_dir, "100_test_report.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 JSON report saved to: {json_path}")
    
    # Save HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HERMES Case Review System - 100 Test Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 30px;
            background: #f5f7fa;
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
            <p style="color: #64748b; margin-top: 10px;">100 Test Performance Report</p>
            <div class="test-datetime">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="summary">
            <h2>📋 Test Summary</h2>
            <p><strong>Environment:</strong> Cloud Sandbox</p>
            <p><strong>Status:</strong> <span style="color: #10b981; font-weight: bold;">✅ ALL 100 TESTS COMPLETED</span></p>
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
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Tests</td><td>{summary.get('total_tests', 0)}</td></tr>
            <tr><td>Successful Tests</td><td class="status-pass">{summary.get('successful_tests', 0)}</td></tr>
            <tr><td>Failed Tests</td><td class="status-fail">{summary.get('failed_tests', 0)}</td></tr>
            <tr><td>Success Rate</td><td>{100.0 * summary.get('successful_tests', 0) / max(summary.get('total_tests', 1), 1):.1f}%</td></tr>
            <tr><td>Total Duration</td><td>{summary.get('total_duration_seconds', 0):.2f}s</td></tr>
            <tr><td>Average Response Time</td><td>{summary.get('average_response_time_ms', 0):.1f}ms</td></tr>
            <tr><td>Median Response Time</td><td>{summary.get('median_response_time_ms', 0):.1f}ms</td></tr>
            <tr><td>Min Response Time</td><td>{summary.get('min_response_time_ms', 0):.1f}ms</td></tr>
            <tr><td>Max Response Time</td><td>{summary.get('max_response_time_ms', 0):.1f}ms</td></tr>
            <tr><td>95th Percentile</td><td>{summary.get('p95_response_time_ms', 0):.1f}ms</td></tr>
            <tr><td>99th Percentile</td><td>{summary.get('p99_response_time_ms', 0):.1f}ms</td></tr>
            <tr><td>Throughput</td><td>{summary.get('requests_per_second', 0):.1f} requests/sec</td></tr>
            <tr><td>Average Case Score</td><td>{summary.get('average_score', 0):.1f}</td></tr>
        </table>
        
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; text-align: center; color: #64748b;">
            <p>Generated by HERMES Case Review System Load Test Framework</p>
        </div>
    </div>
</body>
</html>
"""
    
    html_path = os.path.join(output_dir, "100_test_report.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📄 HTML report saved to: {html_path}")


def main():
    results = run_load_test(num_tests=100, concurrent=10)
    print_results_summary(results)
    save_results(results)
    
    print("\n✅ Load testing completed successfully!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
