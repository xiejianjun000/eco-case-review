"""
自我学习模块 - 从评查实践中学习优化
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json
from loguru import logger
from collections import defaultdict


class SelfLearningModule:
    """自我学习模块 - 自动学习和优化评查能力"""
    
    def __init__(self):
        self.learning_data_path = Path(__file__).parent.parent.parent / 'learning_data'
        self.learning_data_path.mkdir(parents=True, exist_ok=True)
        
        # 学习数据存储
        self.problem_patterns = self._load_problem_patterns()
        self.scoring_experience = self._load_scoring_experience()
        self.user_preferences = self._load_user_preferences()
        self.case_patterns = self._load_case_patterns()
    
    def _load_problem_patterns(self) -> Dict[str, Any]:
        """加载问题模式数据"""
        file_path = self.learning_data_path / 'problem_patterns.json'
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载问题模式失败: {e}")
        return {}
    
    def _load_scoring_experience(self) -> Dict[str, Any]:
        """加载评分经验数据"""
        file_path = self.learning_data_path / 'scoring_experience.json'
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载评分经验失败: {e}")
        return {}
    
    def _load_user_preferences(self) -> Dict[str, Any]:
        """加载用户偏好数据"""
        file_path = self.learning_data_path / 'user_preferences.json'
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载用户偏好失败: {e}")
        return {}
    
    def _load_case_patterns(self) -> Dict[str, Any]:
        """加载案例模式数据"""
        file_path = self.learning_data_path / 'case_patterns.json'
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载案例模式失败: {e}")
        return {}
    
    def _save_problem_patterns(self):
        """保存问题模式数据"""
        file_path = self.learning_data_path / 'problem_patterns.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.problem_patterns, f, ensure_ascii=False, indent=2)
    
    def _save_scoring_experience(self):
        """保存评分经验数据"""
        file_path = self.learning_data_path / 'scoring_experience.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.scoring_experience, f, ensure_ascii=False, indent=2)
    
    def _save_user_preferences(self):
        """保存用户偏好数据"""
        file_path = self.learning_data_path / 'user_preferences.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.user_preferences, f, ensure_ascii=False, indent=2)
    
    def _save_case_patterns(self):
        """保存案例模式数据"""
        file_path = self.learning_data_path / 'case_patterns.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.case_patterns, f, ensure_ascii=False, indent=2)
    
    def learn_from_review(self, review_result: Dict[str, Any]):
        """
        从评查结果中学习
        
        Args:
            review_result: 评查结果
        """
        try:
            # 学习问题模式
            self._learn_problem_patterns(review_result)
            
            # 学习评分经验
            self._learn_scoring_experience(review_result)
            
            # 学习案例模式
            self._learn_case_patterns(review_result)
            
            # 保存学习数据
            self._save_problem_patterns()
            self._save_scoring_experience()
            self._save_case_patterns()
            
            logger.info("学习完成")
            
        except Exception as e:
            logger.error(f"学习失败: {e}")
    
    def _learn_problem_patterns(self, review_result: Dict[str, Any]):
        """学习问题模式"""
        # 提取问题
        issues = []
        
        # 合法性问题
        veto_items = review_result.get('legality_review', {}).get('veto_items', [])
        for item in veto_items:
            if isinstance(item, dict):
                issues.append(item.get('description', ''))
            else:
                issues.append(str(item))
        
        # 规范性问题
        normative_findings = review_result.get('normative_review', {}).get('findings', [])
        issues.extend(normative_findings)
        
        # 证据链问题
        evidence_problems = review_result.get('evidence_chain', {}).get('problems', [])
        issues.extend(evidence_problems)
        
        # 统计问题频率
        for issue in issues:
            if issue not in self.problem_patterns:
                self.problem_patterns[issue] = {
                    'count': 1,
                    'first_seen': datetime.now().isoformat(),
                    'last_seen': datetime.now().isoformat(),
                    'suggestions': []
                }
            else:
                self.problem_patterns[issue]['count'] += 1
                self.problem_patterns[issue]['last_seen'] = datetime.now().isoformat()
    
    def _learn_scoring_experience(self, review_result: Dict[str, Any]):
        """学习评分经验"""
        case_type = review_result.get('case_type', 'unknown')
        comprehensive_score = review_result.get('comprehensive_score', 0)
        grade = review_result.get('comprehensive_grade', 'unknown')
        
        # 按案件类型统计评分分布
        if case_type not in self.scoring_experience:
            self.scoring_experience[case_type] = {
                'total_cases': 0,
                'grade_distribution': defaultdict(int),
                'avg_score': 0,
                'score_history': []
            }
        
        self.scoring_experience[case_type]['total_cases'] += 1
        self.scoring_experience[case_type]['grade_distribution'][grade] += 1
        self.scoring_experience[case_type]['score_history'].append(comprehensive_score)
        
        # 计算平均分
        scores = self.scoring_experience[case_type]['score_history']
        self.scoring_experience[case_type]['avg_score'] = sum(scores) / len(scores)
    
    def _learn_case_patterns(self, review_result: Dict[str, Any]):
        """学习案例模式"""
        violation = review_result.get('violation', 'unknown')
        penalty_amount = review_result.get('discretion', {}).get('recorded_fine', 0)
        reasonableness = review_result.get('discretion', {}).get('reasonableness', 'unknown')
        
        # 记录违法行为与罚款金额的关系
        if violation not in self.case_patterns:
            self.case_patterns[violation] = {
                'total_cases': 0,
                'avg_penalty': 0,
                'penalty_range': {'min': float('inf'), 'max': 0},
                'reasonableness_distribution': defaultdict(int),
                'penalties': []
            }
        
        self.case_patterns[violation]['total_cases'] += 1
        self.case_patterns[violation]['penalties'].append(penalty_amount)
        self.case_patterns[violation]['reasonableness_distribution'][reasonableness] += 1
        
        # 更新金额范围
        if penalty_amount > 0:
            self.case_patterns[violation]['penalty_range']['min'] = min(
                self.case_patterns[violation]['penalty_range']['min'], penalty_amount
            )
            self.case_patterns[violation]['penalty_range']['max'] = max(
                self.case_patterns[violation]['penalty_range']['max'], penalty_amount
            )
            
            # 计算平均罚款
            penalties = [p for p in self.case_patterns[violation]['penalties'] if p > 0]
            self.case_patterns[violation]['avg_penalty'] = sum(penalties) / len(penalties)
    
    def get_common_problems(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取常见问题列表
        
        Args:
            limit: 返回数量限制
            
        Returns:
            问题列表，按频率排序
        """
        problems = []
        for issue, data in self.problem_patterns.items():
            problems.append({
                'issue': issue,
                'count': data['count'],
                'first_seen': data['first_seen'],
                'last_seen': data['last_seen']
            })
        
        # 按频率排序
        problems.sort(key=lambda x: x['count'], reverse=True)
        return problems[:limit]
    
    def get_scoring_statistics(self, case_type: str = None) -> Dict[str, Any]:
        """
        获取评分统计信息
        
        Args:
            case_type: 案件类型（可选）
            
        Returns:
            统计信息
        """
        if case_type:
            return self.scoring_experience.get(case_type, {})
        
        # 返回所有类型的统计
        total_cases = sum(
            data['total_cases'] for data in self.scoring_experience.values()
        )
        
        return {
            'total_case_types': len(self.scoring_experience),
            'total_cases': total_cases,
            'case_types': list(self.scoring_experience.keys())
        }
    
    def suggest_improvements(self, review_result: Dict[str, Any]) -> List[str]:
        """
        基于学习数据提供改进建议
        
        Args:
            review_result: 当前评查结果
            
        Returns:
            改进建议列表
        """
        suggestions = []
        case_type = review_result.get('case_type', 'unknown')
        
        # 对比同类案件评分
        if case_type in self.scoring_experience:
            avg_score = self.scoring_experience[case_type]['avg_score']
            current_score = review_result.get('comprehensive_score', 0)
            
            if current_score < avg_score:
                suggestions.append(f"当前评分({current_score})低于同类案件平均分({avg_score:.1f})")
        
        # 常见问题提醒
        common_problems = self.get_common_problems(5)
        if common_problems:
            suggestions.append(f"注意常见问题：{common_problems[0]['issue']}")
        
        # 裁量合理性建议
        reasonableness = review_result.get('discretion', {}).get('reasonableness', 'unknown')
        if reasonableness not in ['合理', '基本合理'] and case_type in self.case_patterns:
            avg_penalty = self.case_patterns[case_type]['avg_penalty']
            suggestions.append(f"同类案件平均罚款金额约为 {avg_penalty:.1f} 万元")
        
        return suggestions
    
    def update_user_preference(self, user_id: str, key: str, value: Any):
        """
        更新用户偏好
        
        Args:
            user_id: 用户ID
            key: 偏好键
            value: 偏好值
        """
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        
        self.user_preferences[user_id][key] = value
        self._save_user_preferences()
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户偏好
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户偏好字典
        """
        return self.user_preferences.get(user_id, {})


# 全局实例
self_learning_module = SelfLearningModule()
