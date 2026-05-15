"""
生态环境案卷评查系统 - 核心评分引擎
"""
from src.models.schemas import (
    LegalityReview,
    NormativeReview,
    DiscretionReview,
    CaseReviewResult,
    ReviewGrade,
    CaseType,
    VetoItem,
    VetoCategory,
    BasicElementDeduction,
    DocumentScore
)
from typing import List, Tuple


class ScoringEngine:
    """评分引擎 - 核心评分逻辑"""
    
    def __init__(self):
        self.legality_pass_score = 50
        self.legality_fail_score = 0
        self.normative_max_score = 50
        self.comprehensive_max_score = 100
        
        # 等级阈值
        self.grade_thresholds = {
            ReviewGrade.EXCELLENT: 90.0,
            ReviewGrade.GOOD: 80.0,
            ReviewGrade.QUALIFIED: 60.0
        }
    
    def calculate_normative_score(
        self,
        document_score: float,
        document_standard: float,
        basic_deduction: float
    ) -> float:
        """
        计算规范性评分
        
        公式: 规范性得分 = 50 × (文书得分 / 标准分) - 基本要素扣分
        
        Args:
            document_score: 文书实际得分
            document_standard: 文书标准分
            basic_deduction: 基本要素扣分
            
        Returns:
            规范性评分（0-50）
        """
        if document_standard == 0:
            return 0.0
        
        ratio = document_score / document_standard
        normative_score = 50 * ratio - basic_deduction
        
        # 确保分数在有效范围内
        return max(0.0, min(self.normative_max_score, normative_score))
    
    def calculate_comprehensive_score(
        self,
        legality_score: int,
        normative_score: float
    ) -> float:
        """
        计算综合得分
        
        公式: 综合得分 = 合法性得分 + 规范性得分
        
        Args:
            legality_score: 合法性评分（0或50）
            normative_score: 规范性评分（0-50）
            
        Returns:
            综合得分（0-100）
        """
        comprehensive = legality_score + normative_score
        return max(0.0, min(self.comprehensive_max_score, comprehensive))
    
    def determine_grade(self, comprehensive_score: float) -> ReviewGrade:
        """
        根据综合得分确定等级
        
        Args:
            comprehensive_score: 综合得分
            
        Returns:
            评查等级
        """
        if comprehensive_score >= self.grade_thresholds[ReviewGrade.EXCELLENT]:
            return ReviewGrade.EXCELLENT
        elif comprehensive_score >= self.grade_thresholds[ReviewGrade.GOOD]:
            return ReviewGrade.GOOD
        elif comprehensive_score >= self.grade_thresholds[ReviewGrade.QUALIFIED]:
            return ReviewGrade.QUALIFIED
        else:
            return ReviewGrade.UNQUALIFIED
    
    def determine_pass(
        self,
        legality_score: int,
        comprehensive_score: float
    ) -> bool:
        """
        判断是否通过
        
        规则:
        - 触发一票否决（合法性=0）→ 不通过
        - 未触发否决且综合得分<60 → 不通过
        - 未触发否决且综合得分≥60 → 通过
        
        Args:
            legality_score: 合法性评分
            comprehensive_score: 综合得分
            
        Returns:
            是否通过
        """
        # 触发一票否决，不通过
        if legality_score == self.legality_fail_score:
            return False
        
        # 综合得分低于60分，不通过
        if comprehensive_score < self.grade_thresholds[ReviewGrade.QUALIFIED]:
            return False
        
        return True
    
    def process_full_review(
        self,
        case_data: dict
    ) -> Tuple[float, ReviewGrade, bool, dict]:
        """
        处理完整评查流程
        
        Args:
            case_data: 案卷数据字典
            
        Returns:
            (综合得分, 等级, 是否通过, 评查结果详情)
        """
        # 提取各模块评分
        legality_score = case_data.get('legality_score', 0)
        document_score = case_data.get('document_score', 0)
        document_standard = case_data.get('document_standard', 100)
        basic_deduction = case_data.get('basic_deduction', 0)
        
        # 计算规范性得分
        normative_score = self.calculate_normative_score(
            document_score,
            document_standard,
            basic_deduction
        )
        
        # 计算综合得分
        comprehensive_score = self.calculate_comprehensive_score(
            legality_score,
            normative_score
        )
        
        # 确定等级
        grade = self.determine_grade(comprehensive_score)
        
        # 判断是否通过
        is_pass = self.determine_pass(legality_score, comprehensive_score)
        
        # 构建结果详情
        result_detail = {
            'legality_score': legality_score,
            'normative_score': normative_score,
            'comprehensive_score': comprehensive_score,
            'grade': grade.value,
            'is_pass': is_pass,
            'calculation_details': {
                'normative_formula': f"50 × ({document_score}/{document_standard}) - {basic_deduction} = {normative_score}",
                'comprehensive_formula': f"{legality_score} + {normative_score} = {comprehensive_score}"
            }
        }
        
        return comprehensive_score, grade, is_pass, result_detail


class VetoChecker:
    """否决检查器 - 检查25项否决条件"""
    
    # 25项否决条件定义
    VETO_ITEMS = {
        # 执法主体（2项）
        1: {
            'category': VetoCategory.ENFORCEMENT_SUBJECT,
            'name': '实施机关职权',
            'description': '实施机关超出法定职权、管辖范围实施行政处罚或行政强制'
        },
        2: {
            'category': VetoCategory.ENFORCEMENT_SUBJECT,
            'name': '执法人员资格',
            'description': '执法人员不具有行政执法资格，或少于两人'
        },
        # 违法主体（3项）
        3: {
            'category': VetoCategory.ILLEGAL_SUBJECT,
            'name': '违法主体不清',
            'description': '案卷中不同文书当事人名称不一致，且无合理解释'
        },
        4: {
            'category': VetoCategory.ILLEGAL_SUBJECT,
            'name': '处罚对象错误',
            'description': '行政处罚或行政强制的对象不是证据材料中查明的违法主体'
        },
        5: {
            'category': VetoCategory.ILLEGAL_SUBJECT,
            'name': '事实与证据不符',
            'description': '决定书中认定的违法事实与证据材料所指向的违法事实不符'
        },
        # 违法事实证据（2项）
        6: {
            'category': VetoCategory.EVIDENCE,
            'name': '证据不足',
            'description': '证据材料不足以证明当事人的违法行为而予以处罚'
        },
        7: {
            'category': VetoCategory.EVIDENCE,
            'name': '未核实主观过错',
            'description': '当事人有证据足以证明没有主观过错，未经核实仍予以处罚'
        },
        # 法律适用（6项）
        8: {
            'category': VetoCategory.LEGAL_APPLICATION,
            'name': '事实描述不符',
            'description': '违法事实认定的描述与适用的法律规定不符'
        },
        9: {
            'category': VetoCategory.LEGAL_APPLICATION,
            'name': '无法律依据',
            'description': '作出的决定无法律、法规、规章依据'
        },
        10: {
            'category': VetoCategory.LEGAL_APPLICATION,
            'name': '未准确引用',
            'description': '决定书中未准确引用法律、法规、规章的相应条款'
        },
        11: {
            'category': VetoCategory.LEGAL_APPLICATION,
            'name': '兜底条款滥用',
            'description': '无法定理由和证据适用法律、法规、规章规定的兜底条款或等外条款'
        },
        12: {
            'category': VetoCategory.LEGAL_APPLICATION,
            'name': '加重/减轻处罚错误',
            'description': '加重行政处罚或无法定理由减轻行政处罚'
        },
        13: {
            'category': VetoCategory.LEGAL_APPLICATION,
            'name': '查封扣押对象错误',
            'description': '查封、扣押与违法行为无关的设施、设备、物品、工具或场所'
        },
        # 执法程序（12项）
        14: {
            'category': VetoCategory.ENFORCEMENT_PROCEDURE,
            'name': '未告知程序性权利',
            'description': '作出行政处罚决定前未告知程序性权利（陈述、申辩、听证等）'
        },
        15: {
            'category': VetoCategory.ENFORCEMENT_PROCEDURE,
            'name': '未对申请作出决定',
            'description': '虽告知上述权利但未对回避申请作出决定，拒绝听取陈述申辩，未举行听证'
        },
        16: {
            'category': VetoCategory.ENFORCEMENT_PROCEDURE,
            'name': '查封扣押未告知',
            'description': '查封、扣押未当场告知当事人采取行政强制措施的理由、依据及权利'
        },
        17: {
            'category': VetoCategory.ENFORCEMENT_PROCEDURE,
            'name': '未经集体讨论',
            'description': '对情节复杂或者重大违法行为给予行政处罚前，未经行政机关负责人集体讨论决定'
        },
        18: {
            'category': VetoCategory.ENFORCEMENT_PROCEDURE,
            'name': '调查人员参与表决',
            'description': '集体讨论时，调查人员参与了表决'
        },
        19: {
            'category': VetoCategory.ENFORCEMENT_PROCEDURE,
            'name': '应审核未审核',
            'description': '应经法制审核才能作出决定的，未按规定进行法制审核或法制审核未通过即作出决定'
        },
        20: {
            'category': VetoCategory.ENFORCEMENT_PROCEDURE,
            'name': '超过追责期限',
            'description': '对超过法定追责期限的违法行为给予行政处罚'
        },
        21: {
            'category': VetoCategory.ENFORCEMENT_PROCEDURE,
            'name': '调查审查人员混同',
            'description': '案件调查人员同时作为本案的审查人员'
        },
        22: {
            'category': VetoCategory.ENFORCEMENT_PROCEDURE,
            'name': '未责令改正',
            'description': '作出按日连续处罚决定前，没有证据证明已责令当事人改正违法行为'
        },
        23: {
            'category': VetoCategory.ENFORCEMENT_PROCEDURE,
            'name': '未在规定时间复查',
            'description': '责令改正之后，作出按日连续处罚决定前，未在规定时间内实施复查'
        },
        24: {
            'category': VetoCategory.ENFORCEMENT_PROCEDURE,
            'name': '处罚决定书时间错误',
            'description': '按日连续处罚决定书早于原行政处罚决定书作出或送达'
        },
        25: {
            'category': VetoCategory.ENFORCEMENT_PROCEDURE,
            'name': '查封扣押超期',
            'description': '查封、扣押超期未作出解除决定，或者未经批准延长查封、扣押期限'
        },
    }
    
    def check_veto(self, case_data: dict) -> Tuple[bool, List[int], List[VetoItem]]:
        """
        检查是否触发一票否决
        
        Args:
            case_data: 案卷数据
            
        Returns:
            (是否触发否决, 否决项编号列表, 否决项详情列表)
        """
        triggered_items = []
        veto_details = []
        
        # 检查每一项否决条件
        for item_number, item_info in self.VETO_ITEMS.items():
            if self._check_single_item(item_number, case_data):
                triggered_items.append(item_number)
                veto_details.append(VetoItem(
                    number=item_number,
                    category=item_info['category'],
                    check_item=item_info['name'],
                    problem_description=item_info['description'],
                    legal_basis=self._get_legal_basis(item_number),
                    evidence_page=case_data.get(f'evidence_page_{item_number}', ''),
                    rule_reference=f'一.{item_number}',
                    severity='重大'
                ))
        
        has_veto = len(triggered_items) > 0
        return has_veto, triggered_items, veto_details
    
    def _check_single_item(self, item_number: int, case_data: dict) -> bool:
        """
        检查单个否决项
        
        Args:
            item_number: 否决项编号
            case_data: 案卷数据
            
        Returns:
            是否触发该否决项
        """
        # 从案卷数据中获取该否决项的检查结果
        key = f'veto_{item_number}'
        if key in case_data:
            return bool(case_data[key])
        return False
    
    def _get_legal_basis(self, item_number: int) -> str:
        """获取否决项的法律依据"""
        legal_bases = {
            1: '《行政处罚法》第15、18、20、21条',
            2: '《行政处罚法》第42条',
            3: '《行政处罚法》第5条',
            4: '《环境影响评价法》第31条',
            5: '《行政处罚法》第5条',
            6: '《行政处罚法》第36、40条',
            7: '《行政处罚法》第33条',
            8: '《行政处罚法》第5条',
            9: '《行政处罚法》第5条',
            10: '《行政处罚法》第6条',
            11: '《行政强制法》第3条',
            12: '《行政处罚法》第32条',
            13: '《行政强制法》第23条',
            14: '《行政处罚法》第44-45条',
            15: '《行政处罚法》第43、45、65条',
            16: '《行政强制法》第18条',
            17: '《行政处罚法》第57条',
            18: '《行政处罚法》第43条',
            19: '《行政处罚法》第58条',
            20: '《行政处罚法》第36条',
            21: '《环境行政处罚办法》第57条',
            22: '《环境保护法》第59条',
            23: '《按日连续处罚暂行办法》第5条',
            24: '《环境保护法》第59条',
            25: '《行政强制法》第25条',
        }
        return legal_bases.get(item_number, '')


# 全局实例
scoring_engine = ScoringEngine()
veto_checker = VetoChecker()
