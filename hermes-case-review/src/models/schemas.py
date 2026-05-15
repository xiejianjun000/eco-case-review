"""
生态环境案卷评查系统 - 数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class CaseType(str, Enum):
    """案件类型枚举"""
    GENERAL_PENALTY = "一般行政处罚"
    NO_PENALTY = "不予行政处罚"
    DAILY_PENALTY = "按日连续处罚"
    SEAL_CONFISCATION = "查封扣押"
    TRANSFER_DETENTION = "移送拘留"
    TRANSFER_CRIME = "移送涉嫌环境污染犯罪"


class VetoCategory(str, Enum):
    """否决类别枚举"""
    ENFORCEMENT_SUBJECT = "执法主体"
    ILLEGAL_SUBJECT = "违法主体"
    EVIDENCE = "违法事实证据"
    LEGAL_APPLICATION = "法律适用"
    ENFORCEMENT_PROCEDURE = "执法程序"


class ReviewGrade(str, Enum):
    """评查等级枚举"""
    EXCELLENT = "优秀"
    GOOD = "良好"
    QUALIFIED = "合格"
    UNQUALIFIED = "不合格"


class VetoItem(BaseModel):
    """否决项模型"""
    number: int = Field(..., description="否决项编号（1-25）")
    category: VetoCategory = Field(..., description="否决类别")
    check_item: str = Field(..., description="检查项名称")
    problem_description: str = Field(..., description="问题描述")
    legal_basis: str = Field(..., description="法律依据")
    evidence_page: str = Field(..., description="证据页码")
    rule_reference: str = Field(..., description="评查细则条款")
    severity: str = Field(default="重大", description="严重程度")


class LegalityReview(BaseModel):
    """合法性评查结果"""
    has_veto: bool = Field(..., description="是否触发一票否决")
    veto_items: List[VetoItem] = Field(default_factory=list, description="否决项列表")
    legality_score: int = Field(..., description="合法性评分（0或50）")
    legality_pass: bool = Field(..., description="合法性是否通过")
    findings: List[str] = Field(default_factory=list, description="发现问题列表")


class BasicElementDeduction(BaseModel):
    """卷面基本要素扣分项"""
    item_name: str = Field(..., description="扣分项名称")
    deduction: float = Field(..., description="扣分值")
    reason: str = Field(..., description="扣分原因")
    evidence_page: str = Field(..., description="证据页码")
    rule_reference: str = Field(..., description="评查细则条款")


class DocumentScore(BaseModel):
    """文书评分项"""
    document_name: str = Field(..., description="文书名称")
    standard_score: float = Field(..., description="标准分")
    actual_score: float = Field(..., description="实际得分")
    is_complete: bool = Field(..., description="是否完整")
    problems: List[str] = Field(default_factory=list, description="问题列表")
    rule_reference: str = Field(..., description="评查细则条款")
    evidence_page: str = Field(..., description="证据页码")


class NormativeReview(BaseModel):
    """规范性评查结果"""
    document_score: float = Field(..., description="文书得分")
    document_standard: float = Field(..., description="文书标准分")
    basic_elements_deduction: float = Field(default=0.0, description="基本要素扣分")
    normative_score: float = Field(..., description="规范性评分（0-50）")
    basic_deductions: List[BasicElementDeduction] = Field(default_factory=list, description="基本要素扣分明细")
    document_scores: List[DocumentScore] = Field(default_factory=list, description="文书评分明细")
    findings: List[str] = Field(default_factory=list, description="发现问题列表")


class DiscretionFactor(BaseModel):
    """裁量因素"""
    factor_name: str = Field(..., description="因素名称")
    situation: str = Field(..., description="案卷记载情形")
    percentage: float = Field(..., description="裁量百分值")
    evidence_page: str = Field(..., description="证据依据")


class DiscretionReview(BaseModel):
    """裁量基准审查结果"""
    applicable: bool = Field(..., description="是否适用裁量基准")
    table_used: str = Field(..., description="所适用裁量表")
    legal_range: str = Field(..., description="法定处罚幅度")
    discretion_start: float = Field(..., description="裁量起点百分值")
    factors: List[DiscretionFactor] = Field(default_factory=list, description="裁量因素列表")
    total_percentage: float = Field(..., description="裁量百分值总和")
    calculated_fine: float = Field(..., description="裁量计算罚款金额")
    recorded_fine: float = Field(..., description="案卷记载罚款金额")
    fine_difference: float = Field(..., description="金额差异")
    reasonableness: str = Field(..., description="合理性评估")


class EvidenceChain(BaseModel):
    """证据链分析"""
    completeness_rate: float = Field(..., description="完整度百分比")
    has_investigation_record: bool = Field(..., description="是否有调查询问笔录")
    has_site_inspection: bool = Field(..., description="是否有现场检查笔录")
    has_evidence_photograph: bool = Field(..., description="是否有影像证据")
    has_certificate: bool = Field(..., description="是否有资质证明")
    legality: str = Field(..., description="合法性评价")
    relevance: str = Field(..., description="关联性评价")
    chain_integrity: str = Field(..., description="完整度评价")
    problems: List[str] = Field(default_factory=list, description="问题列表")


class DocumentCompleteness(BaseModel):
    """文书完整性检查"""
    required_documents: List[str] = Field(..., description="必需文书列表")
    present_documents: List[str] = Field(default_factory=list, description="实际存在的文书")
    missing_documents: List[str] = Field(default_factory=list, description="缺失文书列表")
    completeness_rate: float = Field(..., description="完整度百分比")


class CaseReviewRequest(BaseModel):
    """案卷评查请求"""
    case_id: Optional[str] = Field(None, description="案卷ID")
    case_file: str = Field(..., description="案卷文件路径")
    case_type: CaseType = Field(default=CaseType.GENERAL_PENALTY, description="案件类型")
    submitter: Optional[str] = Field(None, description="送卷人")
    submit_time: Optional[datetime] = Field(None, description="送卷时间")


class CaseReviewResult(BaseModel):
    """案卷评查结果"""
    case_id: str = Field(..., description="案卷ID")
    case_number: str = Field(..., description="案号")
    case_name: str = Field(..., description="案件名称")
    case_type: CaseType = Field(..., description="案件类型")
    respondent: str = Field(..., description="违法当事人")
    organizing_unit: str = Field(..., description="承办单位")
    violation: str = Field(..., description="违法行为")
    penalty_decision: str = Field(..., description="处罚决定")
    filing_date: datetime = Field(..., description="送卷日期")
    review_date: datetime = Field(default_factory=datetime.now, description="评查完成日期")
    file_pages: int = Field(..., description="文件页数")
    
    # 各模块评查结果
    legality_review: LegalityReview = Field(..., description="合法性评查")
    normative_review: NormativeReview = Field(..., description="规范性评查")
    discretion: DiscretionReview = Field(..., description="裁量基准")
    evidence_chain: EvidenceChain = Field(..., description="证据链分析")
    documents: DocumentCompleteness = Field(..., description="文书完整性")
    
    # 综合得分
    comprehensive_score: float = Field(..., description="综合得分（0-100）")
    comprehensive_grade: ReviewGrade = Field(..., description="评查等级")
    comprehensive_pass: bool = Field(..., description="是否通过")
    
    # 报告文件
    report_file: Optional[str] = Field(None, description="报告文件路径")


class ReviewReport(BaseModel):
    """评查报告模型"""
    result: CaseReviewResult = Field(..., description="评查结果")
    report_content: str = Field(..., description="报告内容（Markdown）")
    generated_at: datetime = Field(default_factory=datetime.now, description="生成时间")
