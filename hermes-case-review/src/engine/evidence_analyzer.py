"""
证据链分析模块 - 分析证据的合法性、关联性、完整性
"""
from typing import Dict, List, Any
from loguru import logger


class EvidenceChainAnalyzer:
    """证据链分析器 - 分析证据三性"""
    
    EVIDENCE_TYPES = [
        '现场检查笔录',
        '调查询问笔录',
        '监测报告',
        '检测报告',
        '鉴定意见',
        '书证',
        '物证',
        '视听资料',
        '电子数据',
        '证人证言',
        '当事人陈述',
        '其他证据'
    ]
    
    def analyze(self, case_content: str) -> Dict[str, Any]:
        """
        分析证据链
        
        Args:
            case_content: 案卷内容
            
        Returns:
            证据链分析结果
        """
        result = {
            'completeness_rate': 0,
            'has_inspection_record': False,
            'has_interview_record': False,
            'has_monitoring_report': False,
            'has_visual_evidence': False,
            'legality': '未知',
            'relevance': '未知',
            'objectivity': '未知',
            'problems': [],
            'suggestions': [],
            'evidence_types_found': [],
            'evidence_count': 0
        }
        
        try:
            # 检测各种证据类型
            for evidence_type in self.EVIDENCE_TYPES:
                if evidence_type in case_content:
                    result['evidence_types_found'].append(evidence_type)
                    result['evidence_count'] += 1
            
            # 特殊检测
            result['has_inspection_record'] = '现场检查笔录' in case_content
            result['has_interview_record'] = '调查询问笔录' in case_content
            result['has_monitoring_report'] = '监测报告' in case_content or '检测报告' in case_content
            result['has_visual_evidence'] = '照片' in case_content or '视频' in case_content or '录像' in case_content
            
            # 计算完整度
            result['completeness_rate'] = self._calculate_completeness(result)
            
            # 评估合法性
            result['legality'] = self._evaluate_legality(case_content, result)
            
            # 评估关联性
            result['relevance'] = self._evaluate_relevance(case_content)
            
            # 评估客观性
            result['objectivity'] = self._evaluate_objectivity(case_content)
            
            # 识别问题
            result['problems'] = self._identify_problems(case_content, result)
            
            # 生成建议
            result['suggestions'] = self._generate_suggestions(result)
            
            result['success'] = True
            
        except Exception as e:
            logger.error(f"证据链分析失败: {e}")
            result['success'] = False
            result['error'] = str(e)
        
        return result
    
    def _calculate_completeness(self, result: Dict) -> int:
        """计算证据链完整度"""
        score = 0
        
        # 基本证据（每项15分）
        if result['has_inspection_record']:
            score += 20
        if result['has_interview_record']:
            score += 20
        if result['has_monitoring_report']:
            score += 20
        
        # 其他证据类型（每种5分，最多20分）
        other_evidence = [e for e in result['evidence_types_found'] 
                          if e not in ['现场检查笔录', '调查询问笔录', '监测报告', '检测报告']]
        score += min(len(other_evidence) * 5, 20)
        
        # 视听资料（20分）
        if result['has_visual_evidence']:
            score += 20
        
        return min(score, 100)
    
    def _evaluate_legality(self, content: str, result: Dict) -> str:
        """评估证据合法性"""
        issues = []
        
        # 检查执法资格
        if '执法证件' not in content and '执法人员' not in content:
            issues.append('未提及执法证件')
        
        # 检查见证人
        if '见证人' not in content and '在场' not in content:
            issues.append('未提及见证人')
        
        # 检查签名
        if '签名' not in content:
            issues.append('未提及签名确认')
        
        if not issues:
            return '合法'
        elif len(issues) <= 2:
            return f'基本合法（{", ".join(issues)}）'
        else:
            return f'存在问题（{", ".join(issues)}）'
    
    def _evaluate_relevance(self, content: str) -> str:
        """评估证据关联性"""
        # 检查关键要素是否存在
        key_elements = ['违法事实', '时间', '地点', '当事人', '证据']
        found_count = sum(1 for elem in key_elements if elem in content)
        
        if found_count == len(key_elements):
            return '紧密关联'
        elif found_count >= 3:
            return '基本关联'
        else:
            return '关联性不足'
    
    def _evaluate_objectivity(self, content: str) -> str:
        """评估证据客观性"""
        # 检查是否有主观推断
        subjective_words = ['可能', '大概', '估计', '推测', '似乎']
        has_subjective = any(word in content for word in subjective_words)
        
        # 检查是否有矛盾
        if '不一致' in content or '矛盾' in content:
            return '存在矛盾'
        elif has_subjective:
            return '部分主观'
        else:
            return '客观真实'
    
    def _identify_problems(self, content: str, result: Dict) -> List[str]:
        """识别证据链问题"""
        problems = []
        
        if not result['has_inspection_record']:
            problems.append('缺少现场检查笔录')
        
        if not result['has_interview_record']:
            problems.append('缺少调查询问笔录')
        
        if not result['has_monitoring_report']:
            problems.append('缺少监测/检测报告')
        
        if '签名' not in content:
            problems.append('证据材料未签名确认')
        
        if '日期' not in content:
            problems.append('证据材料缺少日期')
        
        return problems
    
    def _generate_suggestions(self, result: Dict) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if result['completeness_rate'] < 60:
            suggestions.append('建议补充完善证据材料')
        
        if '缺少现场检查笔录' in result['problems']:
            suggestions.append('建议补充现场检查笔录')
        
        if '缺少调查询问笔录' in result['problems']:
            suggestions.append('建议补充调查询问笔录')
        
        if '缺少监测/检测报告' in result['problems']:
            suggestions.append('建议补充监测或检测报告')
        
        if result['legality'] != '合法':
            suggestions.append('建议审查证据收集程序合法性')
        
        if result['relevance'] == '关联性不足':
            suggestions.append('建议补充与违法事实相关的证据')
        
        return suggestions


# 全局实例
evidence_chain_analyzer = EvidenceChainAnalyzer()
