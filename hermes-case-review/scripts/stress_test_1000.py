#!/usr/bin/env python3
"""
HERMES 1000次批量评查压力测试脚本
使用1000份生态环境行政处罚案例对系统进行压力测试
"""
import json
import time
import sys
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any

sys.path.insert(0, 'src')
from agent_learning.case_reviewer import CaseReviewer


class StressTestRunner:
    """压力测试运行器"""

    def __init__(self, cases_path: str, max_workers: int = 10):
        self.cases_path = cases_path
        self.max_workers = max_workers
        self.cases = []
        self.results = []
        self.start_time = None
        self.end_time = None

    def load_cases(self):
        """加载测试案例"""
        print(f"正在加载案例数据: {self.cases_path}")
        with open(self.cases_path, 'r', encoding='utf-8') as f:
            self.cases = json.load(f)
        print(f"成功加载 {len(self.cases)} 份案例")
        return len(self.cases)

    def case_to_content(self, case: Dict) -> str:
        """将案例转换为评查内容"""
        return f"""
案卷编号：{case['case_number']}
案卷名称：{case['case_name']}
被处罚单位：{case['respondent']}
执法机关：{case['organizing_unit']}
违法事实：{case['violation']}
处罚决定：{case['penalty_decision']}
罚款金额：{case['penalty_amount']}元
法律依据：{case['penalty_basis']}
裁量等级：{case['discretion_level']}

程序检查：立案审批={case['procedural_check']['立案审批']}, 法制审核={case['procedural_check']['法制审核']}, 集体讨论={case['procedural_check']['集体讨论']}
告知权利={case['procedural_check']['告知权利']}, 决定审批={case['procedural_check']['决定审批']}

证据材料：现场检查笔录={case['documents']['现场检查笔录']['status']}, 调查询问笔录={case['documents']['调查询问笔录']['status']}, 监测报告={case['documents']['监测报告']['status']}
"""

    def review_single_case(self, index: int, case: Dict) -> Dict:
        """评查单个案例"""
        start = time.time()
        reviewer = CaseReviewer()
        content = self.case_to_content(case)
        result = reviewer.analyze_case(content, case['case_name'])
        elapsed = time.time() - start

        return {
            "index": index + 1,
            "case_id": case['case_id'],
            "case_number": case['case_number'],
            "case_name": case['case_name'],
            "violation_type": case['violation_type'],
            "success": True,
            "elapsed_time": elapsed,
            "legality_pass": not result['legality_review']['has_veto_issues'],
            "has_veto": result['legality_review']['has_veto_issues'],
            "comprehensive_score": result['comprehensive_score'],
            "grade": result['conclusion']['grade'],
            "veto_issues": len(result['legality_review'].get('veto_issues', [])),
            "normative_score": result['normative_review']['final_score'],
            "normative_deduction": result['normative_review']['total_deduction']
        }

    def run_sequential(self, limit: int = None) -> List[Dict]:
        """顺序执行测试"""
        if limit:
            cases = self.cases[:limit]
        else:
            cases = self.cases

        total = len(cases)
        results = []
        completed = 0

        print(f"\n开始顺序执行 {total} 次评查测试...")
        print("-" * 60)

        self.start_time = time.time()

        for i, case in enumerate(cases):
            result = self.review_single_case(i, case)
            results.append(result)
            completed += 1

            if completed % 10 == 0 or completed == total:
                elapsed = time.time() - self.start_time
                avg_time = elapsed / completed
                remaining = (total - completed) * avg_time
                print(f"进度: {completed}/{total} ({completed*100//total}%) | "
                      f"已用时: {elapsed:.1f}s | "
                      f"预计剩余: {remaining:.1f}s | "
                      f"平均耗时: {avg_time:.3f}s/案例")

        self.end_time = time.time()
        self.results = results
        return results

    def run_parallel(self, limit: int = None, workers: int = None) -> List[Dict]:
        """并行执行测试"""
        if limit:
            cases = self.cases[:limit]
        else:
            cases = self.cases

        total = len(cases)
        if not workers:
            workers = self.max_workers

        results = []
        completed = 0

        print(f"\n开始并行执行 {total} 次评查测试 (workers={workers})...")
        print("-" * 60)

        self.start_time = time.time()

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(self.review_single_case, i, case): i
                for i, case in enumerate(cases)
            }

            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                completed += 1

                if completed % 50 == 0 or completed == total:
                    elapsed = time.time() - self.start_time
                    avg_time = elapsed / completed
                    remaining = (total - completed) * avg_time / workers
                    print(f"进度: {completed}/{total} ({completed*100//total}%) | "
                          f"已用时: {elapsed:.1f}s | "
                          f"预计剩余: {remaining:.1f}s | "
                          f"平均耗时: {avg_time:.3f}s/案例")

        self.end_time = time.time()
        self.results = results
        return results

    def generate_report(self) -> str:
        """生成测试报告"""
        if not self.results:
            return "无测试结果"

        total = len(self.results)
        total_time = self.end_time - self.start_time
        avg_time = total_time / total
        success_count = sum(1 for r in self.results if r['success'])
        failure_count = total - success_count

        scores = [r['comprehensive_score'] for r in self.results if r['success']]
        avg_score = sum(scores) / len(scores) if scores else 0

        veto_count = sum(1 for r in self.results if r['has_veto'])

        grade_counts = {}
        for r in self.results:
            grade = r['grade']
            grade_counts[grade] = grade_counts.get(grade, 0) + 1

        violation_type_counts = {}
        for r in self.results:
            vt = r['violation_type']
            violation_type_counts[vt] = violation_type_counts.get(vt, 0) + 1

        report = f"""
================================================================================
              HERMES 智能案卷评查系统 - 1000次压力测试报告
================================================================================

一、测试概述
--------------------------------------------------------------------------------
测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
测试案例数: {total}份
执行模式: {'并行测试' if self.max_workers > 1 else '顺序测试'}
并发数: {self.max_workers if self.max_workers > 1 else 1}
总耗时: {total_time:.2f}秒
平均耗时: {avg_time:.4f}秒/案例
吞吐量: {total/total_time:.2f}案例/秒

二、执行结果
--------------------------------------------------------------------------------
成功: {success_count} ({success_count*100//total}%)
失败: {failure_count} ({failure_count*100//total}%)
一票否决: {veto_count}份 ({veto_count*100//total}%)

三、评分统计
--------------------------------------------------------------------------------
平均综合得分: {avg_score:.2f}分
最高分: {max(scores):.1f}分
最低分: {min(scores):.1f}分
得分标准差: {self.calculate_std(scores):.2f}

四、评定等级分布
--------------------------------------------------------------------------------
"""
        for grade, count in sorted(grade_counts.items()):
            pct = count * 100 // total
            bar = '█' * (pct // 2)
            report += f"  {grade}: {count}份 ({pct:2d}%) {bar}\n"

        report += f"""
五、违法类型分布
--------------------------------------------------------------------------------
"""
        for vt, count in sorted(violation_type_counts.items(), key=lambda x: x[1], reverse=True):
            pct = count * 100 // total
            bar = '█' * (pct // 2)
            report += f"  {vt}: {count}份 ({pct:2d}%) {bar}\n"

        report += f"""
六、详细统计
--------------------------------------------------------------------------------
"""
        for vt in violation_type_counts:
            vt_results = [r for r in self.results if r['violation_type'] == vt]
            vt_scores = [r['comprehensive_score'] for r in vt_results]
            vt_avg = sum(vt_scores) / len(vt_scores) if vt_scores else 0
            vt_veto = sum(1 for r in vt_results if r['has_veto'])
            report += f"  {vt}:\n"
            report += f"    案例数: {len(vt_results)} | 平均分: {vt_avg:.1f} | 一票否决: {vt_veto}\n"

        report += f"""
七、结论与建议
--------------------------------------------------------------------------------
"""
        if avg_score >= 85:
            report += "  ✅ 系统表现优秀，评查质量高，平均得分达到优秀水平\n"
        elif avg_score >= 70:
            report += "  ⚠️ 系统表现良好，但仍有提升空间\n"
        else:
            report += "  ❌ 系统评查质量需要改进\n"

        if total_time < 300:
            report += "  ✅ 执行效率优秀，1000次评查在5分钟内完成\n"
        elif total_time < 600:
            report += "  ⚠️ 执行效率良好，可接受\n"
        else:
            report += "  ❌ 执行效率偏低，建议优化\n"

        if failure_count == 0:
            report += "  ✅ 所有案例评查成功，无失败\n"
        else:
            report += f"  ⚠️ 存在 {failure_count} 例失败，需要排查\n"

        report += f"""
================================================================================
                              测试报告生成完毕
================================================================================
"""
        return report

    @staticmethod
    def calculate_std(values: List[float]) -> float:
        """计算标准差"""
        if not values:
            return 0
        avg = sum(values) / len(values)
        variance = sum((x - avg) ** 2 for x in values) / len(values)
        return variance ** 0.5


def main():
    """主函数"""
    print("=" * 70)
    print("        HERMES 智能案卷评查系统 - 1000次压力测试")
    print("=" * 70)

    cases_path = "test_data/stress_test/eco_cases_1000.json"
    if not os.path.exists(cases_path):
        print(f"错误: 找不到案例文件 {cases_path}")
        print("请先运行 scripts/generate_test_cases.py 生成测试数据")
        return 1

    runner = StressTestRunner(cases_path, max_workers=1)
    runner.load_cases()

    mode = input("\n请选择测试模式:\n  1. 顺序执行 (慢速，完整测试)\n  2. 并行执行 (快速，高并发测试)\n请输入选择 [1/2]: ").strip()

    if mode == "2":
        workers = input("请输入并发数 [默认10]: ").strip()
        workers = int(workers) if workers else 10
        results = runner.run_parallel(workers=workers)
    else:
        results = runner.run_sequential()

    report = runner.generate_report()
    print("\n" + report)

    output_dir = "load_test_results"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(output_dir, f"1000_test_results_{timestamp}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "test_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "total_cases": len(results),
            "results": results
        }, f, ensure_ascii=False, indent=2)

    report_path = os.path.join(output_dir, f"1000_test_report_{timestamp}.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n测试结果已保存:")
    print(f"  JSON数据: {json_path}")
    print(f"  测试报告: {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
