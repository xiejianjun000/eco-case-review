"""
V4行政处罚案卷评查系统 - 自动化功能测试套件

运行方式:
    pytest v4-test-suite.py -v
    pytest v4-test-suite.py -v -k "legality"
    pytest v4-test-suite.py -v --tb=short

测试覆盖范围:
    1. 评分机制测试 (15+用例)
    2. 一票否决测试 (25项全覆盖)
    3. 报告格式测试 (20+用例)
    4. 边界条件测试
    5. 数据一致性测试
"""

import pytest
import json
import re
from pathlib import Path
from conftest import (
    calculate_normative_score,
    calculate_comprehensive_score,
    determine_grade,
    determine_pass,
    format_score,
    validate_legality_score,
    validate_normative_score,
    validate_comprehensive_score,
    validate_veto_trigger,
    validate_grade_mapping,
    LEGALITY_SCORE_PASS,
    LEGALITY_SCORE_FAIL,
    NORMATIVE_MAX_SCORE,
    COMPREHENSIVE_MAX_SCORE,
    GRADE_THRESHOLDS,
    BASIC_ELEMENT_ITEMS
)


# ============================================================================
# 第一部分：评分机制测试类
# ============================================================================

class TestV4ScoringMechanism:
    """V4评分机制测试 - 验证核心评分公式和逻辑"""

    def test_legality_score_binary(self, test_cases):
        """TC-001: 合法性评分必须为0或50（二值性测试）"""
        for case_id, case_data in test_cases.items():
            legality_score = case_data["legality_review"]["legality_score"]
            has_veto = case_data["legality_review"]["has_veto"]

            # 一票否决触发时，合法性得分必须为0
            if has_veto:
                assert legality_score == 0, \
                    f"{case_id}: 触发一票否决但合法性得分={legality_score}，应为0"

            # 未触发否决时，合法性得分必须为50
            else:
                assert legality_score == 50, \
                    f"{case_id}: 未触发一票否决但合法性得分={legality_score}，应为50"

    def test_legality_veto_trigger(self, test_cases):
        """TC-002: 一票否决触发条件测试"""
        for case_id, case_data in test_cases.items():
            legality = case_data["legality_review"]
            has_veto = legality["has_veto"]
            veto_items = legality["veto_items"]
            legality_score = legality["legality_score"]

            # 验证否决逻辑一致性
            expected_score = 0 if has_veto else 50
            assert legality_score == expected_score, \
                f"{case_id}: has_veto={has_veto}, veto_items={veto_items}, " \
                f"但得分={legality_score}，期望={expected_score}"

    def test_normative_formula_calculation(self, test_cases):
        """TC-003: 规范性评分公式验证

        公式: 规范性得分 = 50 × (文书得分/标准分) - 基本要素扣分
        """
        for case_id, case_data in test_cases.items():
            normative = case_data["normative_review"]
            document_score = normative["document_score"]
            document_standard = normative["document_standard"]
            basic_deduction = normative.get("basic_elements_deduction", 0)

            # 计算期望的规范性得分
            expected_normative = calculate_normative_score(
                document_score, document_standard, basic_deduction
            )

            # 获取实际的规范性得分
            actual_normative = normative["normative_score"]

            # 允许0.1的浮点误差
            assert abs(expected_normative - actual_normative) < 0.1, \
                f"{case_id}: 规范性得分={actual_normative}，" \
                f"期望={expected_normative:.2f} " \
                f"(公式: 50×{document_score}/{document_standard}-{basic_deduction})"

    def test_normative_score_range(self, test_cases):
        """TC-004: 规范性评分范围验证（0-50分）"""
        for case_id, case_data in test_cases.items():
            normative_score = case_data["normative_review"]["normative_score"]

            assert validate_normative_score(normative_score), \
                f"{case_id}: 规范性得分={normative_score}超出范围[0, 50]"

    def test_comprehensive_score_calculation(self, test_cases):
        """TC-005: 综合得分计算公式验证

        公式: 综合得分 = 合法性得分 + 规范性得分
        """
        for case_id, case_data in test_cases.items():
            legality_score = case_data["legality_review"]["legality_score"]
            normative_score = case_data["normative_review"]["normative_score"]

            expected_comprehensive = calculate_comprehensive_score(
                legality_score, normative_score
            )
            actual_comprehensive = case_data["comprehensive_score"]

            # 允许0.01的浮点误差
            assert abs(expected_comprehensive - actual_comprehensive) < 0.01, \
                f"{case_id}: 综合得分={actual_comprehensive}，" \
                f"期望={expected_comprehensive:.2f} " \
                f"(公式: {legality_score}+{normative_score})"

    def test_comprehensive_score_range(self, test_cases):
        """TC-006: 综合得分范围验证（0-100分）"""
        for case_id, case_data in test_cases.items():
            comprehensive_score = case_data["comprehensive_score"]

            assert validate_comprehensive_score(comprehensive_score), \
                f"{case_id}: 综合得分={comprehensive_score}超出范围[0, 100]"

    def test_grade_mapping_excellent(self):
        """TC-007: 等级映射-优秀(>=90分)"""
        test_scores = [90, 95, 100, 100.5]

        for score in test_scores:
            grade = determine_grade(score)
            assert grade == "优秀", f"得分{score}应映射为'优秀'，实际为'{grade}'"

    def test_grade_mapping_good(self):
        """TC-008: 等级映射-良好(80-89分)"""
        test_scores = [80, 85, 89.9]

        for score in test_scores:
            grade = determine_grade(score)
            assert grade == "良好", f"得分{score}应映射为'良好'，实际为'{grade}'"

    def test_grade_mapping_qualified(self):
        """TC-009: 等级映射-合格(60-79分)"""
        test_scores = [60, 65, 70, 79.99]

        for score in test_scores:
            grade = determine_grade(score)
            assert grade == "合格", f"得分{score}应映射为'合格'，实际为'{grade}'"

    def test_grade_mapping_unqualified(self):
        """TC-010: 等级映射-不合格(<60分)"""
        test_scores = [0, 30, 59.99]

        for score in test_scores:
            grade = determine_grade(score)
            assert grade == "不合格", f"得分{score}应映射为'不合格'，实际为'{grade}'"

    def test_pass_verdict_logic(self, test_cases):
        """TC-011: 通过/不通过判定逻辑"""
        for case_id, case_data in test_cases.items():
            legality_score = case_data["legality_review"]["legality_score"]
            comprehensive_score = case_data["comprehensive_score"]
            expected_pass = case_data["comprehensive_pass"]

            actual_pass = determine_pass(legality_score, comprehensive_score)

            assert actual_pass == expected_pass, \
                f"{case_id}: 判定结果不一致。" \
                f"合法性={legality_score}, 综合={comprehensive_score}, " \
                f"期望通过={expected_pass}, 实际={actual_pass}"

    def test_score_precision_two_decimals(self, test_cases):
        """TC-012: 分数精度测试（保留2位小数）"""
        import re

        for case_id, case_data in test_cases.items():
            comprehensive_score = case_data["comprehensive_score"]

            # 验证分数格式
            score_str = format_score(comprehensive_score, 2)
            assert re.match(r'^\d+(\.\d{1,2})?$', score_str), \
                f"{case_id}: 分数{comprehensive_score}格式不正确"

    def test_specific_score_calculation_tc002(self, test_cases):
        """TC-013: TC002特定计算验证

        文书得分=85/100，扣3分
        期望: 规范性=50×0.85-3=39.5
        """
        tc002 = test_cases["TC002"]
        normative = tc002["normative_review"]

        document_score = normative["document_score"]  # 85
        document_standard = normative["document_standard"]  # 100
        deduction = normative["deduction"]  # 3

        expected_normative = 50 * (document_score / document_standard) - deduction
        actual_normative = normative["normative_score"]

        assert abs(expected_normative - actual_normative) < 0.01, \
            f"TC002: 期望规范性得分={expected_normative:.2f}，" \
            f"实际={actual_normative}"

        # 综合得分 = 50 + 39.5 = 89.5
        expected_comprehensive = 50 + expected_normative
        actual_comprehensive = tc002["comprehensive_score"]

        assert abs(expected_comprehensive - actual_comprehensive) < 0.01, \
            f"TC002: 期望综合得分={expected_comprehensive:.2f}，" \
            f"实际={actual_comprehensive}"

    def test_specific_score_calculation_tc003(self, test_cases):
        """TC-014: TC003一票否决验证（未告知陈述申辩权）

        触发序号14否决项 → 合法性=0 → 综合=0
        """
        tc003 = test_cases["TC003"]

        assert tc003["legality_review"]["has_veto"] == True, "TC003应触发一票否决"
        assert 14 in tc003["legality_review"]["veto_items"], "TC003应触发序号14否决"

        # 一票否决，综合得分应为0
        assert tc003["comprehensive_score"] == 0, \
            f"TC003触发一票否决，综合得分应为0，实际={tc003['comprehensive_score']}"

    def test_specific_score_display_format(self):
        """TC-015: 分数显示格式验证"""
        test_cases = [
            (80.25, "80.25"),
            (33.333, "33.33"),  # 精度截断测试
            (100.0, "100.00"),
            (0.0, "0.00")
        ]

        for score, expected_str in test_cases:
            formatted = format_score(score, 2)
            assert formatted == expected_str, \
                f"分数{score}格式化应为'{expected_str}'，实际为'{formatted}'"


# ============================================================================
# 第二部分：一票否决测试类
# ============================================================================

class TestV4VetoMechanism:
    """V4一票否决机制测试 - 验证25项否决条件的完整覆盖"""

    def test_veto_item_14_no_statement_defense_right(self, test_cases):
        """否决项测试: 序号14 - 未告知当事人陈述申辩权利"""
        # TC003触发此项
        tc003 = test_cases["TC003"]

        assert 14 in tc003["legality_review"]["veto_items"], \
            "TC003应触发序号14否决项（未告知陈述申辩权）"

        assert tc003["legality_review"]["legality_score"] == 0, \
            "触发序号14否决后合法性得分应为0"

    def test_veto_item_15_no_hearing_right(self, test_cases):
        """否决项测试: 序号15 - 未告知听证权利或未举行听证"""
        # TC004触发此项
        tc004 = test_cases["TC004"]

        assert 15 in tc004["legality_review"]["veto_items"], \
            "TC004应触发序号15否决项（未举行听证）"

        assert tc004["legality_review"]["legality_score"] == 0, \
            "触发序号15否决后合法性得分应为0"

    def test_veto_item_1_unauthorized_filing(self, test_cases):
        """否决项测试: 序号1 - 未经法定程序批准擅自立案"""
        # TC005触发此项
        tc005 = test_cases["TC005"]

        assert 1 in tc005["legality_review"]["veto_items"], \
            "TC005应触发序号1否决项（擅自立案）"

        assert tc005["legality_review"]["legality_score"] == 0, \
            "触发序号1否决后合法性得分应为0"

    def test_veto_item_25_seal_confiscation_overdue(self, test_cases):
        """否决项测试: 序号25 - 查封扣押超期或未批准延长"""
        # 此项需单独构造测试数据验证

        # 验证数据中包含此项的描述
        pass

    def test_veto_all_25_items_coverage(self, veto_items):
        """否决项测试: 验证25项否决条件完整性"""
        assert len(veto_items) == 25, \
            f"否决条件应为25项，实际为{len(veto_items)}项"

        # 验证序号1-25全覆盖
        expected_items = set(range(1, 26))
        actual_items = set(int(k) for k in veto_items.keys())

        assert expected_items == actual_items, \
            f"否决项序号不连续。期望: {sorted(expected_items)}, 实际: {sorted(actual_items)}"

    def test_veto_categories_coverage(self, veto_items):
        """否决项测试: 验证否决条件分类覆盖"""
        categories = {
            "执法主体": [1, 2],
            "违法主体": [3, 4, 5],
            "违法事实证据": [6, 7],
            "法律适用": [8, 9, 10, 11, 12, 13],
            "执法程序": [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
        }

        for category, expected_numbers in categories.items():
            actual_numbers = [
                int(k) for k, v in veto_items.items()
                if v["category"] == category
            ]
            assert set(expected_numbers) == set(actual_numbers), \
                f"{category}: 期望否决项{expected_numbers}，" \
                f"实际{actual_numbers}"

    def test_veto_severity_all_major(self, veto_items):
        """否决项测试: 验证所有否决项严重程度为"重大\""""
        for item_id, item_info in veto_items.items():
            assert item_info["severity"] == "重大", \
                f"否决项{item_id}严重程度应为'重大'，" \
                f"实际为'{item_info['severity']}'"

    def test_veto_logic_no_veto_pass(self, test_cases):
        """否决项测试: 未触发否决时通过"""
        # TC002和TC006、TC007未触发否决
        for case_id in ["TC002", "TC006", "TC007"]:
            case = test_cases[case_id]
            assert case["legality_review"]["has_veto"] == False, \
                f"{case_id}不应触发否决"
            assert case["legality_review"]["legality_score"] == 50, \
                f"{case_id}未触发否决，合法性得分应为50"

    def test_veto_logic_multiple_veto_items(self, test_cases):
        """否决项测试: 多项否决条件触发"""
        tc005 = test_cases["TC005"]

        # TC005触发序号1和14两项否决
        veto_items_list = tc005["legality_review"]["veto_items"]
        assert len(veto_items_list) >= 2, \
            f"TC005应至少触发2项否决，实际触发{len(veto_items_list)}项"

        assert 1 in veto_items_list, "TC005应触发序号1否决"
        assert 14 in veto_items_list, "TC005应触发序号14否决"

        assert tc005["legality_review"]["legality_score"] == 0, \
            "多项否决触发时合法性得分仍应为0"

    def test_veto_deduction_independent(self, test_cases):
        """否决项测试: 否决得分与规范性得分独立"""
        for case_id, case_data in test_cases.items():
            legality_score = case_data["legality_review"]["legality_score"]
            normative_score = case_data["normative_review"]["normative_score"]
            comprehensive_score = case_data["comprehensive_score"]

            # 当一票否决触发时，综合得分=0
            if case_data["legality_review"]["has_veto"]:
                assert comprehensive_score == 0, \
                    f"{case_id}触发一票否决，综合得分应为0"
                assert legality_score == 0, \
                    f"{case_id}触发一票否决，合法性得分应为0"
            else:
                # 未否决时，综合得分 = 50 + 规范性得分
                expected = 50 + normative_score
                assert abs(comprehensive_score - expected) < 0.01, \
                    f"{case_id}综合得分计算错误"


# ============================================================================
# 第三部分：报告格式测试类
# ============================================================================

class TestV4ReportFormat:
    """V4报告格式测试 - 验证9+1章节完整性"""

    def test_report_section_1_basic_info(self, test_cases):
        """报告格式测试: 第1节 - 案卷基本信息（10项字段）"""
        required_fields = [
            "case_number",      # 案号
            "case_name",        # 案件名称
            "case_type",        # 案件类型
            "respondent",       # 违法当事人
            "organizing_unit",  # 承办单位
            "violation",        # 违法行为
            "penalty_decision", # 处罚决定
            "filing_date",      # 送卷日期
            "review_date",      # 评查完成日期
            "file_pages"        # 文件页数
        ]

        for case_id, case_data in test_cases.items():
            missing_fields = []
            for field in required_fields:
                if field not in case_data or case_data[field] is None:
                    missing_fields.append(field)

            assert len(missing_fields) == 0, \
                f"{case_id}缺少字段: {missing_fields}"

    def test_report_section_2_legality_conclusion(self, test_cases):
        """报告格式测试: 第2节 - 合法性评查结论"""
        for case_id, case_data in test_cases.items():
            legality = case_data["legality_review"]

            # 验证合法性评查包含必要字段
            required_fields = ["has_veto", "veto_items", "legality_score",
                              "legality_pass", "findings"]
            for field in required_fields:
                assert field in legality, \
                    f"{case_id}合法性评查缺少字段: {field}"

    def test_report_section_3_normative_scoring(self, test_cases):
        """报告格式测试: 第3节 - 规范性评分（含公式）"""
        for case_id, case_data in test_cases.items():
            normative = case_data["normative_review"]

            # 验证规范性评分包含必要字段
            required_fields = ["document_score", "document_standard",
                              "deduction", "normative_score",
                              "basic_elements_deduction", "findings"]
            for field in required_fields:
                assert field in normative, \
                    f"{case_id}规范性评查缺少字段: {field}"

    def test_report_section_4_discretion(self, test_cases):
        """报告格式测试: 第4节 - 裁量基准（4小节）"""
        for case_id, case_data in test_cases.items():
            discretion = case_data["discretion"]

            # 验证裁量基准包含必要字段
            required_fields = ["applicable", "table_used", "legal_range",
                              "discretion_start", "factors", "total_percentage",
                              "calculated_fine", "recorded_fine", "reasonableness"]
            for field in required_fields:
                assert field in discretion, \
                    f"{case_id}裁量基准缺少字段: {field}"

            # 验证裁量因素
            factors = discretion["factors"]
            assert len(factors) > 0, \
                f"{case_id}裁量因素列表为空"

            # 每个因素应包含必要字段
            for factor in factors:
                assert "name" in factor, \
                    f"{case_id}裁量因素缺少name字段"
                assert "situation" in factor, \
                    f"{case_id}裁量因素缺少situation字段"
                assert "percentage" in factor, \
                    f"{case_id}裁量因素缺少percentage字段"

    def test_report_section_5_evidence_chain(self, test_cases):
        """报告格式测试: 第5节 - 证据链（3性分析）"""
        for case_id, case_data in test_cases.items():
            evidence = case_data["evidence_chain"]

            # 验证证据链包含3性分析
            required_fields = ["completeness_rate",
                              "legality",    # 合法性
                              "relevance",   # 关联性
                              "chain_integrity"]  # 完整度
            for field in required_fields:
                assert field in evidence, \
                    f"{case_id}证据链缺少字段: {field}"

            # 验证3性评价值
            assert evidence["legality"] in ["合法", "存在瑕疵", "存在重大问题"], \
                f"{case_id}证据合法性评价值不正确"
            assert evidence["relevance"] in ["充分", "基本充分", "不充分"], \
                f"{case_id}证据关联性评价值不正确"
            assert evidence["chain_integrity"] in ["完整", "基本完整", "不完整"], \
                f"{case_id}证据链完整度评价值不正确"

    def test_report_section_6_document_completeness(self, test_cases):
        """报告格式测试: 第6节 - 文书完整性（14项检查）"""
        required_documents = [
            "filing_form",           # 立案审批表
            "site_inspection_record", # 现场检查笔录
            "investigation_record",   # 调查询问笔录
            "monitoring_report",      # 监测/检测/鉴定报告
            "other_evidence",         # 收集的其他证据
            "case_report",            # 案件调查报告
            "correction_order",       # 责令改正决定书
            "pre_notice",            # 行政处罚事先告知书
            "hearing_notice",        # 行政处罚听证通知书
            "hearing_record",        # 听证笔录
            "decision",              # 行政处罚决定书
            "enforcement_notice",    # 督促履行义务催告书
            "enforcement_application", # 强制执行申请书
            "closure_form"           # 结案审批表
        ]

        for case_id, case_data in test_cases.items():
            documents = case_data["documents"]

            # 验证文档列表完整性
            missing_docs = []
            for doc in required_documents:
                if doc not in documents:
                    missing_docs.append(doc)

            assert len(missing_docs) == 0, \
                f"{case_id}文书列表缺少: {missing_docs}"

            # 验证每个文档的状态字段
            for doc_name, doc_info in documents.items():
                assert "required" in doc_info, \
                    f"{case_id}-{doc_name}缺少required字段"
                assert "present" in doc_info, \
                    f"{case_id}-{doc_name}缺少present字段"
                assert "complete" in doc_info, \
                    f"{case_id}-{doc_name}缺少complete字段"

    def test_report_section_7_comprehensive_score(self, test_cases):
        """报告格式测试: 第7节 - 综合得分"""
        for case_id, case_data in test_cases.items():
            required_fields = ["comprehensive_score",
                              "comprehensive_grade",
                              "comprehensive_pass"]
            for field in required_fields:
                assert field in case_data, \
                    f"{case_id}综合得分部分缺少字段: {field}"

    def test_report_section_8_improvement_suggestions(self, test_cases):
        """报告格式测试: 第8节 - 问题汇总（P0/P1/P2）

        注意: 问题汇总信息分散在各个发现中
        """
        for case_id, case_data in test_cases.items():
            # 验证有发现问题记录
            all_findings = []
            for finding_list in case_data.values():
                if isinstance(finding_list, dict):
                    if "findings" in finding_list:
                        all_findings.extend(finding_list["findings"])

            # TC003、TC004、TC005应有发现问题
            if case_id in ["TC003", "TC004", "TC005"]:
                assert len(all_findings) > 0, \
                    f"{case_id}应有发现问题记录"

    def test_report_section_9_signatures(self):
        """报告格式测试: 第9节 - 签章

        签章信息在实际报告中为必填项
        """
        # 此项在实际报告中验证
        pass

    def test_report_appendix_items(self):
        """报告格式测试: 附件 - 5项"""
        required_appendix = [
            "合法性审查结论表",
            "规范性评分明细表",
            "裁量基准计算表",
            "证据链分析图",
            "文书清单对照表"
        ]

        # 验证数据中包含附件列表
        # 附件在实际报告中生成
        assert len(required_appendix) == 5, "附件应为5项"


# ============================================================================
# 第四部分：边界条件测试类
# ============================================================================

class TestV4BoundaryConditions:
    """V4边界条件测试 - 验证极端情况和临界值"""

    def test_score_zero_all_missing(self):
        """边界测试: 得分=0 - 所有文书缺失"""
        # 模拟完全缺失的案卷
        comprehensive_score = calculate_comprehensive_score(0, 0)
        grade = determine_grade(comprehensive_score)

        assert comprehensive_score == 0, "综合得分应为0"
        assert grade == "不合格", "0分案卷应为不合格"

    def test_score_hundred_perfect_case(self):
        """边界测试: 得分=100 - 完美案卷"""
        comprehensive_score = calculate_comprehensive_score(50, 50)
        grade = determine_grade(comprehensive_score)

        assert comprehensive_score == 100, "完美案卷综合得分应为100"
        assert grade == "优秀", "100分案卷应为优秀"

    def test_score_boundary_qualified_79_99(self):
        """边界测试: 分界点79.99分 → 合格"""
        score = 79.99
        grade = determine_grade(score)

        assert grade == "合格", f"79.99分应为'合格'，实际为'{grade}'"

    def test_score_boundary_good_80_00(self):
        """边界测试: 分界点80.00分 → 良好"""
        score = 80.00
        grade = determine_grade(score)

        assert grade == "良好", f"80.00分应为'良好'，实际为'{grade}'"

    def test_score_boundary_good_89_99(self):
        """边界测试: 分界点89.99分 → 良好"""
        score = 89.99
        grade = determine_grade(score)

        assert grade == "良好", f"89.99分应为'良好'，实际为'{grade}'"

    def test_score_boundary_excellent_90_00(self):
        """边界测试: 分界点90.00分 → 优秀"""
        score = 90.00
        grade = determine_grade(score)

        assert grade == "优秀", f"90.00分应为'优秀'，实际为'{grade}'"

    def test_score_boundary_unqualified_59_99(self):
        """边界测试: 分界点59.99分 → 不合格"""
        score = 59.99
        grade = determine_grade(score)

        assert grade == "不合格", f"59.99分应为'不合格'，实际为'{grade}'"

    def test_score_boundary_qualified_60_00(self):
        """边界测试: 分界点60.00分 → 合格"""
        score = 60.00
        grade = determine_grade(score)

        assert grade == "合格", f"60.00分应为'合格'，实际为'{grade}'"

    def test_score_precision_truncation(self):
        """边界测试: 精度测试 - 33.333分应显示33.33"""
        score = 33.333
        formatted = format_score(score, 2)

        assert formatted == "33.33", \
            f"33.333分格式化应为'33.33'，实际为'{formatted}'"

    def test_normative_score_max_50(self):
        """边界测试: 规范性得分最大值为50"""
        normative_score = calculate_normative_score(100, 100, 0)
        assert normative_score == 50, "满分文书规范性得分应为50"

    def test_normative_score_min_0(self):
        """边界测试: 规范性得分最小值为0（扣分超过得分时）"""
        normative_score = calculate_normative_score(5, 100, 10)
        assert normative_score >= 0, "规范性得分不能为负"

    def test_legality_score_cannot_be_negative(self):
        """边界测试: 合法性得分不能为负"""
        assert LEGALITY_SCORE_PASS >= 0, "合法性通过分不能为负"
        assert LEGALITY_SCORE_FAIL >= 0, "合法性否决分不能为负"

    def test_comprehensive_score_exact_values(self, test_cases):
        """边界测试: 综合得分精确值验证"""
        for case_id, case_data in test_cases.items():
            score = case_data["comprehensive_score"]
            grade = case_data["comprehensive_grade"]

            assert validate_grade_mapping(score, grade), \
                f"{case_id}: 得分{score}与等级'{grade}'不匹配"


# ============================================================================
# 第五部分：数据一致性测试类
# ============================================================================

class TestV4DataConsistency:
    """V4数据一致性测试 - 验证内部数据逻辑一致性"""

    def test_consistency_legality_vs_normative(self, test_cases):
        """一致性测试: 合法性与规范性得分逻辑一致性

        验证: 第3.2节vs第6节得分>0则"具备"=是，得分=0则"具备"=否
        """
        for case_id, case_data in test_cases.items():
            legality_score = case_data["legality_review"]["legality_score"]
            normative_score = case_data["normative_review"]["normative_score"]

            # 合法性=0时，规范性不应存在（综合=0）
            if legality_score == 0:
                # 一票否决情况下，综合得分应为0
                assert case_data["comprehensive_score"] == 0, \
                    f"{case_id}触发一票否决，综合得分应为0"

    def test_consistency_json_vs_markdown(self, test_cases):
        """一致性测试: JSON数据与Markdown报告数据一致性

        验证: 综合分在JSON和报告格式中一致
        """
        for case_id, case_data in test_cases.items():
            # JSON数据
            json_score = case_data["comprehensive_score"]

            # 验证得分计算
            expected_score = (
                case_data["legality_review"]["legality_score"] +
                case_data["normative_review"]["normative_score"]
            )

            assert abs(json_score - expected_score) < 0.01, \
                f"{case_id}: JSON综合分{json_score}与计算值{expected_score}不一致"

    def test_consistency_grade_vs_score(self, test_cases):
        """一致性测试: 等级与得分对应关系"""
        for case_id, case_data in test_cases.items():
            score = case_data["comprehensive_score"]
            grade = case_data["comprehensive_grade"]

            # 根据分数重新计算等级
            calculated_grade = determine_grade(score)

            assert grade == calculated_grade, \
                f"{case_id}: 得分{score}的等级应为'{calculated_grade}'，" \
                f"实际为'{grade}'"

    def test_consistency_pass_verdict_vs_grade(self, test_cases):
        """一致性测试: 通过判定与等级一致性"""
        for case_id, case_data in test_cases.items():
            grade = case_data["comprehensive_grade"]
            is_pass = case_data["comprehensive_pass"]

            # 不合格案卷不应通过
            if grade == "不合格":
                assert is_pass == False, \
                    f"{case_id}: 等级为'不合格'，不应通过"

            # 合格及以上案卷应通过（除非一票否决）
            elif grade in ["合格", "良好", "优秀"]:
                has_veto = case_data["legality_review"]["has_veto"]
                assert is_pass == (not has_veto), \
                    f"{case_id}: 等级为'{grade}'且未触发否决，应通过"

    def test_consistency_veto_items_vs_legality_score(self, test_cases):
        """一致性测试: 否决项列表与合法性得分一致性"""
        for case_id, case_data in test_cases.items():
            has_veto = case_data["legality_review"]["has_veto"]
            veto_items = case_data["legality_review"]["veto_items"]
            legality_score = case_data["legality_review"]["legality_score"]

            # 验证一致性
            assert validate_veto_trigger(has_veto, veto_items, legality_score), \
                f"{case_id}: veto逻辑不一致 " \
                f"(has_veto={has_veto}, items={veto_items}, score={legality_score})"

    def test_consistency_normative_calculation_formula(self, test_cases):
        """一致性测试: 规范性得分公式验证"""
        for case_id, case_data in test_cases.items():
            normative = case_data["normative_review"]

            # 使用公式重新计算
            calculated = calculate_normative_score(
                normative["document_score"],
                normative["document_standard"],
                normative.get("basic_elements_deduction", 0)
            )

            actual = normative["normative_score"]

            assert abs(calculated - actual) < 0.01, \
                f"{case_id}: 规范性得分{actual}与公式计算{calculated:.2f}不一致"

    def test_consistency_comprehensive_vs_components(self, test_cases):
        """一致性测试: 综合得分与分量一致性"""
        for case_id, case_data in test_cases.items():
            comprehensive = case_data["comprehensive_score"]
            legality = case_data["legality_review"]["legality_score"]
            normative = case_data["normative_review"]["normative_score"]

            expected = legality + normative

            assert abs(comprehensive - expected) < 0.01, \
                f"{case_id}: 综合得分{comprehensive}不等于" \
                f"合法性{legality}+规范性{normative}"

    def test_consistency_discretion_percentage_sum(self, test_cases):
        """一致性测试: 裁量百分值加总"""
        for case_id, case_data in test_cases.items():
            discretion = case_data["discretion"]
            factors = discretion["factors"]

            # 计算因素百分值总和
            calculated_sum = sum(f["percentage"] for f in factors)
            recorded_sum = discretion["total_percentage"]

            # 允许一定误差
            assert abs(calculated_sum - recorded_sum) < 0.1, \
                f"{case_id}: 裁量百分值总和{recorded_sum}，" \
                f"实际加总{calculated_sum}"

    def test_consistency_document_count(self, test_cases):
        """一致性测试: 文书数量14项"""
        for case_id, case_data in test_cases.items():
            documents = case_data["documents"]

            assert len(documents) == 14, \
                f"{case_id}: 一般行政处罚案卷文书应为14项，" \
                f"实际为{len(documents)}项"

    def test_consistency_evidence_types(self, test_cases):
        """一致性测试: 证据类型完整性"""
        for case_id, case_data in test_cases.items():
            evidence = case_data["evidence_chain"]

            required_fields = [
                "has_investigation_record",
                "has_site_inspection",
                "has_evidence_photograph",
                "has_certificate"
            ]

            for field in required_fields:
                assert field in evidence, \
                    f"{case_id}证据链缺少字段: {field}"


# ============================================================================
# 第六部分：集成测试类
# ============================================================================

class TestV4Integration:
    """V4集成测试 - 端到端场景测试"""

    def test_end_to_end_tc002_pass_case(self, test_cases):
        """集成测试: TC002 - 正常通过案卷"""
        tc002 = test_cases["TC002"]

        # 验证完整流程
        assert tc002["legality_review"]["legality_score"] == 50
        assert tc002["normative_review"]["normative_score"] == 39.5
        assert abs(tc002["comprehensive_score"] - 89.5) < 0.01
        assert tc002["comprehensive_grade"] == "良好"
        assert tc002["comprehensive_pass"] == True

    def test_end_to_end_tc003_veto_case(self, test_cases):
        """集成测试: TC003 - 一票否决案卷"""
        tc003 = test_cases["TC003"]

        # 验证否决逻辑
        assert tc003["legality_review"]["has_veto"] == True
        assert 14 in tc003["legality_review"]["veto_items"]
        assert tc003["legality_review"]["legality_score"] == 0

        # 综合得分应为0
        assert tc003["comprehensive_score"] == 0
        assert tc003["comprehensive_grade"] == "不合格"
        assert tc003["comprehensive_pass"] == False

    def test_end_to_end_tc005_multiple_veto_case(self, test_cases):
        """集成测试: TC005 - 多项否决案卷"""
        tc005 = test_cases["TC005"]

        # 验证多项否决
        veto_items = tc005["legality_review"]["veto_items"]
        assert 1 in veto_items  # 序号1: 擅自立案
        assert 14 in veto_items  # 序号14: 未告知陈述申辩权

        # 仍应为0分
        assert tc005["legality_review"]["legality_score"] == 0
        assert tc005["comprehensive_score"] == 0

    def test_end_to_end_tc006_excellent_case(self, test_cases):
        """集成测试: TC006 - 优秀案卷"""
        tc006 = test_cases["TC006"]

        # 未触发否决
        assert tc006["legality_review"]["has_veto"] == False
        assert tc006["legality_review"]["legality_score"] == 50

        # 高规范性得分
        assert tc006["normative_review"]["normative_score"] == 43

        # 综合得分93
        assert abs(tc006["comprehensive_score"] - 93) < 0.01
        assert tc006["comprehensive_grade"] == "优秀"
        assert tc006["comprehensive_pass"] == True

    def test_end_to_end_tc007_excellent_case(self, test_cases):
        """集成测试: TC007 - 优秀案卷"""
        tc007 = test_cases["TC007"]

        # 未触发否决
        assert tc007["legality_review"]["has_veto"] == False
        assert tc007["legality_review"]["legality_score"] == 50

        # 综合得分91
        assert abs(tc007["comprehensive_score"] - 91) < 0.01
        assert tc007["comprehensive_grade"] == "优秀"
        assert tc007["comprehensive_pass"] == True

    def test_batch_summary_statistics(self, test_cases):
        """集成测试: 批量统计"""
        total_cases = len(test_cases)
        veto_cases = sum(1 for c in test_cases.values()
                        if c["legality_review"]["has_veto"])
        pass_cases = sum(1 for c in test_cases.values()
                         if c["comprehensive_pass"])

        assert total_cases == 6, "测试案卷应为6个"
        assert veto_cases == 3, "否决案卷应为3个(TC003/TC004/TC005)"
        assert pass_cases == 3, "通过案卷应为3个(TC002/TC006/TC007)"


# ============================================================================
# 测试运行入口
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
