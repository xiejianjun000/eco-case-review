#!/usr/bin/env python3
"""
HERMES智能案卷评查工具
输入案卷内容，自动进行评查并生成报告
"""
import json
from typing import Dict, List, Any
from datetime import datetime


class CaseReviewer:
    """案卷评查器"""
    
    # 25项评查标准
    REVIEW_STANDARDS = {
        "veto_rules": [
            {"id": 1, "name": "处罚对象认定错误或不清", "description": "被处罚主体不存在或与违法主体不符"},
            {"id": 2, "name": "主要事实认定不清", "description": "违法事实描述模糊，关键要素缺失"},
            {"id": 3, "name": "违反法定程序", "description": "未依法告知、听证、集体讨论等法定程序"},
            {"id": 4, "name": "适用法律依据错误", "description": "引用的法律条款与违法行为不匹配"},
            {"id": 5, "name": "超越职权", "description": "作出不属于本部门职权的处罚决定"},
            {"id": 6, "name": "滥用职权", "description": "处罚决定明显不合理或徇私舞弊"},
            {"id": 7, "name": "主要证据不足", "description": "关键证据缺失或相互矛盾"},
            {"id": 8, "name": "行政处罚明显不当", "description": "罚款金额畸高畸低或措施明显不当"}
        ],
        "deduction_rules": [
            {"id": 9, "name": "未告知程序性权利", "type": "程序", "score": 3},
            {"id": 10, "name": "未经集体讨论决定", "type": "程序", "score": 2},
            {"id": 11, "name": "应经法制审核未审核", "type": "程序", "score": 2},
            {"id": 12, "name": "应经集体讨论未讨论", "type": "程序", "score": 2},
            {"id": 13, "name": "罚款金额计算错误", "type": "实体", "score": 5},
            {"id": 14, "name": "法律引用不准确", "type": "实体", "score": 3},
            {"id": 15, "name": "文书格式不规范", "type": "规范", "score": 1},
            {"id": 16, "name": "签名盖章缺失", "type": "规范", "score": 2},
            {"id": 17, "name": "日期错误", "type": "规范", "score": 1},
            {"id": 18, "name": "证据链不完整", "type": "实体", "score": 3},
            {"id": 19, "name": "裁量理由不充分", "type": "实体", "score": 3},
            {"id": 20, "name": "救济途径告知不全", "type": "程序", "score": 2},
            {"id": 21, "name": "文书送达不规范", "type": "程序", "score": 1},
            {"id": 22, "name": "案卷装订不规范", "type": "规范", "score": 1},
            {"id": 23, "name": "目录编制不规范", "type": "规范", "score": 1},
            {"id": 24, "name": "副卷管理不规范", "type": "规范", "score": 1},
            {"id": 25, "name": "其他不规范问题", "type": "规范", "score": 1}
        ]
    }
    
    def __init__(self):
        self.review_results = []
        
    def analyze_case(self, case_content: str, case_name: str = "未命名案件") -> Dict[str, Any]:
        """
        分析案卷内容
        """
        # 基础信息提取
        basic_info = self._extract_basic_info(case_content)
        
        # 合法性审查
        legality_review = self._review_legality(case_content)
        
        # 规范性审查
        normative_review = self._review_normative(case_content)
        
        # 裁量审查
        discretion_review = self._review_discretion(case_content)
        
        # 综合评分
        comprehensive_score = self._calculate_score(legality_review, normative_review, discretion_review)
        
        # 生成结论
        conclusion = self._generate_conclusion(legality_review, comprehensive_score)
        
        result = {
            "case_name": case_name,
            "review_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "basic_info": basic_info,
            "legality_review": legality_review,
            "normative_review": normative_review,
            "discretion_review": discretion_review,
            "comprehensive_score": comprehensive_score,
            "conclusion": conclusion
        }
        
        self.review_results.append(result)
        return result
    
    def _extract_basic_info(self, content: str) -> Dict[str, str]:
        """提取基础信息"""
        return {
            "case_type": self._extract_field(content, ["案件类型", "处罚类型"]),
            "violation_type": self._extract_field(content, ["违法行为", "违法类型"]),
            "company_name": self._extract_field(content, ["当事人", "被处罚单位", "企业名称"]),
            "violation_date": self._extract_field(content, ["违法时间", "案发时间"]),
            "location": self._extract_field(content, ["违法地点", "案发地点"])
        }
    
    def _extract_field(self, content: str, keywords: List[str]) -> str:
        """提取字段"""
        import re
        for keyword in keywords:
            pattern = f"{keyword}[：:]([^\n]+)"
            match = re.search(pattern, content)
            if match:
                return match.group(1).strip()
        return "未明确"
    
    def _review_legality(self, content: str) -> Dict[str, Any]:
        """合法性审查"""
        issues = []
        passed = []
        
        # 检查一票否决项
        for rule in self.REVIEW_STANDARDS["veto_rules"]:
            if self._check_issue(content, rule):
                issues.append(rule)
            else:
                passed.append(rule["name"])
        
        return {
            "has_veto_issues": len(issues) > 0,
            "veto_issues": issues,
            "passed_items": passed,
            "has_evidence": self._check_evidence(content),
            "has_procedure": self._check_procedure(content),
            "has_authority": self._check_authority(content)
        }
    
    def _check_issue(self, content: str, rule: Dict) -> bool:
        """检查是否存在问题"""
        keywords = {
            1: ["主体错误", "认定不清", "被处罚主体"],
            2: ["事实不清", "认定不清", "关键要素缺失"],
            3: ["未告知", "未听证", "未经集体讨论", "程序违法"],
            4: ["适用错误", "法律依据错误", "引法错误"],
            5: ["超越职权", "越权", "无权"],
            6: ["滥用职权", "明显不当", "徇私"],
            7: ["证据不足", "主要证据缺失", "证据矛盾"],
            8: ["明显不当", "畸高畸低", "显失公正"]
        }
        
        rule_id = rule["id"]
        if rule_id in keywords:
            return any(kw in content for kw in keywords[rule_id])
        return False
    
    def _check_evidence(self, content: str) -> bool:
        """检查证据"""
        evidence_keywords = ["证据", "笔录", "监测报告", "鉴定"]
        return any(kw in content for kw in evidence_keywords)
    
    def _check_procedure(self, content: str) -> bool:
        """检查程序"""
        return "告知" in content or "听证" in content or "集体讨论" in content
    
    def _check_authority(self, content: str) -> bool:
        """检查职权"""
        return "职权" in content or "权限" in content
    
    def _review_normative(self, content: str) -> Dict[str, Any]:
        """规范性审查"""
        issues = []
        total_score = 25
        
        for rule in self.REVIEW_STANDARDS["deduction_rules"]:
            if self._check_normative_issue(content, rule):
                issues.append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "type": rule["type"],
                    "deduction": rule["score"]
                })
        
        deducted_score = sum(item["deduction"] for item in issues)
        final_score = max(0, total_score - deducted_score)
        
        return {
            "total_items": len(self.REVIEW_STANDARDS["deduction_rules"]),
            "issues": issues,
            "total_deduction": deducted_score,
            "final_score": final_score,
            "score_rate": f"{final_score}/{total_score}"
        }
    
    def _check_normative_issue(self, content: str, rule: Dict) -> bool:
        """检查规范性项"""
        keywords = {
            9: ["未告知", "未听取"],
            10: ["未经集体讨论"],
            11: ["未审核", "未法制审核"],
            12: ["未经集体讨论"],
            13: ["计算错误", "金额错误"],
            14: ["引用不准确", "法律错误"],
            15: ["格式不规范", "格式错误"],
            16: ["未签名", "未盖章", "签名缺失"],
            17: ["日期错误", "时间错误"],
            18: ["证据不完整", "证据链缺失"],
            19: ["裁量理由不充分", "理由不充分"],
            20: ["救济途径告知不全"],
            21: ["送达不规范", "未送达"],
            22: ["装订不规范"],
            23: ["目录不规范"],
            24: ["副卷管理不规范"]
        }
        
        rule_id = rule["id"]
        if rule_id in keywords:
            return any(kw in content for kw in keywords[rule_id])
        return False
    
    def _review_discretion(self, content: str) -> Dict[str, Any]:
        """裁量审查"""
        factors = []
        
        if "初次" in content:
            factors.append({"factor": "初次违法", "impact": "从轻"})
        if "及时整改" in content or "主动纠正" in content:
            factors.append({"factor": "及时整改", "impact": "从轻"})
        if "再次" in content or "屡次" in content:
            factors.append({"factor": "再次违法", "impact": "从重"})
        if "超标" in content:
            factors.append({"factor": "超标排放", "impact": "从重"})
        
        return {
            "factors": factors,
            "has_discretion": len(factors) > 0
        }
    
    def _calculate_score(self, legality: Dict, normative: Dict, discretion: Dict) -> float:
        """计算综合评分"""
        if legality["has_veto_issues"]:
            return 59.0
        
        base_score = 100
        deduction = normative["total_deduction"]
        
        if discretion["has_discretion"]:
            deduction += 2
        
        return max(0, base_score - deduction)
    
    def _generate_conclusion(self, legality: Dict, score: float) -> Dict[str, str]:
        """生成结论"""
        if legality["has_veto_issues"]:
            return {
                "grade": "不合格",
                "level": "一票否决",
                "summary": f"存在{len(legality['veto_issues'])}项一票否决问题",
                "suggestion": "建议发回整改后重新评查"
            }
        elif score >= 90:
            return {
                "grade": "优秀",
                "level": "A",
                "summary": "案卷质量优秀，符合规范要求",
                "suggestion": "建议评为优秀等次"
            }
        elif score >= 80:
            return {
                "grade": "良好",
                "level": "B",
                "summary": "案卷质量良好，存在少量不规范问题",
                "suggestion": "建议评为良好等次，注意完善细节"
            }
        elif score >= 60:
            return {
                "grade": "合格",
                "level": "C",
                "summary": "案卷基本合格，存在一定问题",
                "suggestion": "建议评为合格等次，需进行整改"
            }
        else:
            return {
                "grade": "不合格",
                "level": "D",
                "summary": "案卷存在较多问题，需要整改",
                "suggestion": "建议发回整改后重新评查"
            }
    
    def generate_report(self, result: Dict) -> str:
        """生成评查报告"""
        report = f"""
# 生态环境行政处罚案卷评查报告

## 一、基本信息

| 项目 | 内容 |
|------|------|
| 案件名称 | {result['case_name']} |
| 评查日期 | {result['review_date']} |
| 案件类型 | {result['basic_info']['case_type']} |
| 违法类型 | {result['basic_info']['violation_type']} |
| 当事人 | {result['basic_info']['company_name']} |
| 违法时间 | {result['basic_info']['violation_date']} |
| 违法地点 | {result['basic_info']['location']} |

## 二、合法性审查

### 2.1 一票否决项审查

**审查结果**: {"❌ 不通过" if result['legality_review']['has_veto_issues'] else "✅ 通过"}

"""
        
        if result['legality_review']['has_veto_issues']:
            report += "**存在问题**:\n\n"
            for issue in result['legality_review']['veto_issues']:
                report += f"- ❌ **{issue['name']}**: {issue['description']}\n"
        else:
            report += "✅ 所有一票否决项审查通过\n\n"
        
        report += f"""
### 2.2 其他合法性检查

| 检查项 | 结果 |
|--------|------|
| 证据完整性 | {"✅ 有" if result['legality_review']['has_evidence'] else "❌ 无"} |
| 程序合法性 | {"✅ 有" if result['legality_review']['has_procedure'] else "❌ 无"} |
| 职权合法性 | {"✅ 有" if result['legality_review']['has_authority'] else "❌ 无"} |

## 三、规范性审查

### 3.1 规范性评分

| 指标 | 数值 |
|------|------|
| 总分 | {result['normative_review']['total_items']}分 |
| 得分 | {result['normative_review']['final_score']}分 |
| 扣分 | {result['normative_review']['total_deduction']}分 |

"""
        
        if result['normative_review']['issues']:
            report += "### 3.2 存在问题\n\n"
            for issue in result['normative_review']['issues']:
                report += f"- ❌ 序号{issue['id']}: {issue['name']} (扣{issue['deduction']}分)\n"
        
        report += f"""
## 四、裁量审查

"""
        
        if result['discretion_review']['factors']:
            report += "| 裁量因素 | 影响 |\n|---------|------|\n"
            for factor in result['discretion_review']['factors']:
                report += f"| {factor['factor']} | {factor['impact']} |\n"
        else:
            report += "未发现特殊裁量因素\n"
        
        report += f"""
## 五、综合评定

### 5.1 综合评分

**综合得分**: {result['comprehensive_score']:.1f} 分

### 5.2 评定等级

| 等级 | 分数范围 | 评定结果 |
|------|----------|----------|
| A | 90-100分 | {"✅ 优秀" if result['conclusion']['level'] == 'A' else ""} |
| B | 80-89分 | {"✅ 良好" if result['conclusion']['level'] == 'B' else ""} |
| C | 60-79分 | {"✅ 合格" if result['conclusion']['level'] == 'C' else ""} |
| D | 60分以下 | {"✅ 不合格" if result['conclusion']['level'] == 'D' else ""} |

**评定等级**: {result['conclusion']['grade']}（{result['conclusion']['level']}级）

### 5.3 评查结论

**总体评价**: {result['conclusion']['summary']}

**处理建议**: {result['conclusion']['suggestion']}

---

**评查人**: HERMES智能评查系统  
**评查时间**: {result['review_date']}
"""
        
        return report


def main():
    """测试评查功能"""
    reviewer = CaseReviewer()
    
    # 示例案卷内容
    sample_case = """
    案件类型：行政处罚
    违法行为：超标排放水污染物
    当事人：某化工有限公司
    违法时间：2024年3月15日
    违法地点：湖南省某市某工业园区
    
    案情摘要：
    该企业2024年3月排放口外排废水COD浓度为580mg/L，
    超过排放标准500mg/L，超标0.16倍。
    企业及时整改，已停止超标排放行为。
    企业初次违法，无前科。
    
    处罚结果：
    罚款人民币10万元整。
    
    程序情况：
    已依法告知当事人陈述申辩权，
    当事人未提出陈述申辩。
    处罚决定已经集体讨论。
    """
    
    # 进行评查
    result = reviewer.analyze_case(sample_case, "某化工有限公司超标排放案")
    
    # 生成报告
    report = reviewer.generate_report(result)
    print(report)
    
    return 0


if __name__ == "__main__":
    exit(main())
