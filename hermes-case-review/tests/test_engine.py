"""
测试用例：案卷评查系统
"""
import pytest
from src.engine.scoring_engine import scoring_engine, veto_checker
from src.models.schemas import ReviewGrade


class TestScoringEngine:
    """评分引擎测试"""
    
    def test_normative_score_calculation(self):
        """测试规范性评分计算"""
        # 正常情况
        score = scoring_engine.calculate_normative_score(
            document_score=85,
            document_standard=100,
            basic_deduction=3
        )
        assert score == 39.5  # 50 * 0.85 - 3 = 39.5
        
    def test_normative_score_full_marks(self):
        """测试满分情况"""
        score = scoring_engine.calculate_normative_score(
            document_score=100,
            document_standard=100,
            basic_deduction=0
        )
        assert score == 50  # 50 * 1.0 - 0 = 50
        
    def test_normative_score_zero(self):
        """测试零分情况"""
        score = scoring_engine.calculate_normative_score(
            document_score=0,
            document_standard=100,
            basic_deduction=10
        )
        assert score == 0  # 扣分超过得分
        
    def test_comprehensive_score_calculation(self):
        """测试综合得分计算"""
        score = scoring_engine.calculate_comprehensive_score(
            legality_score=50,
            normative_score=39.5
        )
        assert score == 89.5
        
    def test_comprehensive_score_veto(self):
        """测试否决情况"""
        score = scoring_engine.calculate_comprehensive_score(
            legality_score=0,
            normative_score=39.5
        )
        assert score == 39.5  # 0 + 39.5 = 39.5
        
    def test_grade_excellent(self):
        """测试优秀等级"""
        grade = scoring_engine.determine_grade(95)
        assert grade == ReviewGrade.EXCELLENT
        
    def test_grade_good(self):
        """测试良好等级"""
        grade = scoring_engine.determine_grade(85)
        assert grade == ReviewGrade.GOOD
        
    def test_grade_qualified(self):
        """测试合格等级"""
        grade = scoring_engine.determine_grade(70)
        assert grade == ReviewGrade.QUALIFIED
        
    def test_grade_unqualified(self):
        """测试不合格等级"""
        grade = scoring_engine.determine_grade(55)
        assert grade == ReviewGrade.UNQUALIFIED
        
    def test_pass_with_veto(self):
        """测试否决情况不通过"""
        is_pass = scoring_engine.determine_pass(0, 50)
        assert is_pass == False
        
    def test_pass_low_score(self):
        """测试低分不通过"""
        is_pass = scoring_engine.determine_pass(50, 55)
        assert is_pass == False
        
    def test_pass_normal(self):
        """测试正常通过"""
        is_pass = scoring_engine.determine_pass(50, 80)
        assert is_pass == True


class TestVetoChecker:
    """否决检查器测试"""
    
    def test_veto_check_no_issues(self):
        """测试无否决项情况"""
        case_data = {
            'veto_1': False,
            'veto_14': False,
            'veto_20': False,
        }
        
        has_veto, items, details = veto_checker.check_veto(case_data)
        assert has_veto == False
        assert len(items) == 0
        
    def test_veto_check_single_issue(self):
        """测试单个否决项"""
        case_data = {
            'veto_14': True,
        }
        
        has_veto, items, details = veto_checker.check_veto(case_data)
        assert has_veto == True
        assert 14 in items
        
    def test_veto_check_multiple_issues(self):
        """测试多个否决项"""
        case_data = {
            'veto_1': True,
            'veto_14': True,
            'veto_20': True,
        }
        
        has_veto, items, details = veto_checker.check_veto(case_data)
        assert has_veto == True
        assert len(items) == 3
        assert 1 in items
        assert 14 in items
        assert 20 in items
        
    def test_all_veto_items_defined(self):
        """测试所有25项否决条件都已定义"""
        assert len(veto_checker.VETO_ITEMS) == 25
        
    def test_veto_item_legal_basis(self):
        """测试否决项法律依据"""
        legal_basis = veto_checker._get_legal_basis(1)
        assert '《行政处罚法》' in legal_basis


class TestGradeBoundaries:
    """等级边界测试"""
    
    def test_boundary_90_excellent(self):
        """边界测试：90分应评为优秀"""
        grade = scoring_engine.determine_grade(90)
        assert grade == ReviewGrade.EXCELLENT
        
    def test_boundary_89_good(self):
        """边界测试：89.99分应评为良好"""
        grade = scoring_engine.determine_grade(89.99)
        assert grade == ReviewGrade.GOOD
        
    def test_boundary_80_good(self):
        """边界测试：80分应评为良好"""
        grade = scoring_engine.determine_grade(80)
        assert grade == ReviewGrade.GOOD
        
    def test_boundary_79_qualified(self):
        """边界测试：79.99分应评为合格"""
        grade = scoring_engine.determine_grade(79.99)
        assert grade == ReviewGrade.QUALIFIED
        
    def test_boundary_60_qualified(self):
        """边界测试：60分应评为合格"""
        grade = scoring_engine.determine_grade(60)
        assert grade == ReviewGrade.QUALIFIED
        
    def test_boundary_59_unqualified(self):
        """边界测试：59.99分应评为不合格"""
        grade = scoring_engine.determine_grade(59.99)
        assert grade == ReviewGrade.UNQUALIFIED


class TestEndToEnd:
    """端到端测试"""
    
    def test_full_review_pass_case(self):
        """测试完整评查流程 - 通过案卷"""
        case_data = {
            'legality_score': 50,  # 未触发否决
            'document_score': 85,
            'document_standard': 100,
            'basic_deduction': 3
        }
        
        comprehensive, grade, is_pass, details = scoring_engine.process_full_review(case_data)
        
        assert comprehensive == 89.5
        assert grade == ReviewGrade.GOOD
        assert is_pass == True
        
    def test_full_review_veto_case(self):
        """测试完整评查流程 - 否决赛卷"""
        case_data = {
            'legality_score': 0,  # 触发否决
            'document_score': 90,
            'document_standard': 100,
            'basic_deduction': 0
        }
        
        comprehensive, grade, is_pass, details = scoring_engine.process_full_review(case_data)
        
        assert comprehensive == 45  # 0 + 45 = 45
        assert grade == ReviewGrade.UNQUALIFIED
        assert is_pass == False
        
    def test_full_review_excellent_case(self):
        """测试完整评查流程 - 优秀案卷"""
        case_data = {
            'legality_score': 50,
            'document_score': 95,
            'document_standard': 100,
            'basic_deduction': 2
        }
        
        comprehensive, grade, is_pass, details = scoring_engine.process_full_review(case_data)
        
        # 50 * 0.95 - 2 = 45.5
        # 50 + 45.5 = 95.5
        assert comprehensive >= 95
        assert grade == ReviewGrade.EXCELLENT
        assert is_pass == True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
