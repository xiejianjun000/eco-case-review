"""
AI 智能分析模块 - 基于大模型的案卷内容分析
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import httpx
from loguru import logger

from src.config.settings import settings


class AIAnalyzer:
    """AI 智能分析器 - 使用大模型分析案卷内容"""
    
    def __init__(self):
        self.api_key = settings.HERMES_API_KEY
        self.model_provider = settings.HERMES_MODEL_PROVIDER
        self.model_name = settings.HERMES_MODEL_NAME
        self.api_base = self._get_api_base()
        
    def _get_api_base(self) -> str:
        """获取 API 基础地址"""
        if self.model_provider == "deepseek":
            return "https://api.deepseek.com/v1/chat/completions"
        elif self.model_provider == "openai":
            return "https://api.openai.com/v1/chat/completions"
        elif self.model_provider == "zhipu":
            return "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        elif self.model_provider == "anthropic":
            return "https://api.anthropic.com/v1/messages"
        else:
            return "https://api.deepseek.com/v1/chat/completions"
    
    async def analyze_case_content(self, content: str, case_type: str = "一般行政处罚") -> Dict[str, Any]:
        """
        使用大模型分析案卷内容
        
        Args:
            content: 案卷文本内容
            case_type: 案件类型
            
        Returns:
            分析结果字典
        """
        try:
            prompt = self._build_analysis_prompt(content, case_type)
            response = await self._call_llm(prompt)
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"AI 分析失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'veto_items': [],
                'issues': [],
                'suggestions': []
            }
    
    def _build_analysis_prompt(self, content: str, case_type: str) -> str:
        """构建分析提示词"""
        return f"""
你是生态环境行政执法案卷合法性审查专家，精通《生态环境行政执法案卷评查细则（2024年版）》。

请分析以下案卷内容，识别合法性问题：

【案卷内容】
{content}

【案件类型】
{case_type}

【评查标准】
请检查以下25项否决条件：

1. 执法主体（2项）
   - 序号1: 实施机关超出法定职权、管辖范围实施行政处罚
   - 序号2: 执法人员不具有行政执法资格，或少于两人

2. 违法主体（3项）
   - 序号3: 违法主体不清（案卷中不同文书当事人名称不一致）
   - 序号4: 处罚对象错误
   - 序号5: 事实与证据不符

3. 违法事实证据（2项）
   - 序号6: 证据不足
   - 序号7: 未核实主观过错

4. 法律适用（6项）
   - 序号8: 事实描述与法律规定不符
   - 序号9: 无法律依据
   - 序号10: 未准确引用法律条款
   - 序号11: 滥用兜底条款
   - 序号12: 加重/减轻处罚错误
   - 序号13: 查封扣押对象错误

5. 执法程序（12项）
   - 序号14: 未告知程序性权利
   - 序号15: 未对申请作出决定（回避/陈述/申辩/听证）
   - 序号16: 查封扣押未告知权利
   - 序号17: 未经集体讨论
   - 序号18: 调查人员参与表决
   - 序号19: 应审核未审核
   - 序号20: 超过追责期限
   - 序号21: 调查审查人员混同
   - 序号22: 未责令改正（按日连续处罚）
   - 序号23: 未在规定时间复查
   - 序号24: 处罚决定书时间错误
   - 序号25: 查封扣押超期

【输出格式】
请以JSON格式输出：
{{
    "has_veto": true/false,
    "veto_items": [
        {{
            "number": 序号,
            "category": "类别",
            "description": "问题描述",
            "evidence": "证据位置/页码",
            "legal_basis": "法律依据"
        }}
    ],
    "issues": [
        {{
            "severity": "严重/一般/轻微",
            "description": "问题描述",
            "suggestion": "改进建议"
        }}
    ],
    "suggestions": ["建议1", "建议2"],
    "summary": "综合分析摘要"
}}

请仔细阅读案卷内容，只输出JSON格式结果，不要添加其他文字。
"""
    
    async def _call_llm(self, prompt: str) -> str:
        """调用大模型 API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        if self.model_provider == "anthropic":
            data = {
                "model": "claude-3-5-sonnet-20240620",
                "max_tokens": 4000,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        else:
            data = {
                "model": self.model_name,
                "max_tokens": 4000,
                "temperature": 0.1,
                "messages": [
                    {"role": "system", "content": "你是一位专业的生态环境行政执法案卷审查专家。"},
                    {"role": "user", "content": prompt}
                ]
            }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_base,
                headers=headers,
                json=data,
                timeout=120
            )
            response.raise_for_status()
            return response.json()
    
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """解析 LLM 响应"""
        try:
            if self.model_provider == "anthropic":
                content = response['content'][0]['text']
            else:
                content = response['choices'][0]['message']['content']
            
            # 尝试解析 JSON
            try:
                result = json.loads(content)
            except:
                # 如果不是有效的 JSON，尝试提取 JSON 部分
                import re
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    result = json.loads(match.group())
                else:
                    result = {
                        'has_veto': False,
                        'veto_items': [],
                        'issues': [],
                        'suggestions': [],
                        'summary': content
                    }
            
            result['success'] = True
            return result
            
        except Exception as e:
            logger.error(f"解析响应失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'has_veto': False,
                'veto_items': [],
                'issues': [],
                'suggestions': []
            }
    
    async def analyze_normative(self, content: str) -> Dict[str, Any]:
        """分析规范性问题"""
        prompt = f"""
你是生态环境行政执法案卷规范性评分专家。

请分析以下案卷内容，评估规范性：

【案卷内容】
{content}

【评分标准】
1. 卷面基本要素（20分，扣分制）
   - 文书基本要素（10分）：部门名称、文书名称、发文字号、印章、日期、审批意见
   - 笔录基本要素（10分）：时间、地点、执法人员、当事人、权利告知、签名

2. 文书完整性（14项）
   - 立案审批表、现场检查笔录、调查询问笔录、监测报告、案件调查报告、
     责令改正决定书、行政处罚事先告知书、听证通知书、听证笔录、
     行政处罚决定书、催告书、强制执行申请书、结案审批表

【输出格式】
JSON格式：
{{
    "document_score": 实际得分(0-100),
    "basic_deduction": 基本要素扣分数,
    "missing_documents": ["缺失文书1", "缺失文书2"],
    "document_issues": [
        {{
            "document_name": "文书名称",
            "issue": "问题描述",
            "score": 实际得分,
            "standard_score": 标准分
        }}
    ],
    "basic_element_issues": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"]
}}

只输出JSON，不要其他文字。
"""
        
        response = await self._call_llm(prompt)
        return self._parse_response(response)
    
    async def analyze_evidence_chain(self, content: str) -> Dict[str, Any]:
        """分析证据链"""
        prompt = f"""
你是证据链分析专家。请分析以下案卷的证据链完整性：

【案卷内容】
{content}

【分析要点】
1. 证据完整性：是否有现场检查笔录、调查询问笔录、监测报告、影像证据
2. 证据合法性：证据收集程序是否合法
3. 证据关联性：证据是否与违法事实相关
4. 证据客观性：证据是否真实可靠

【输出格式】
JSON格式：
{{
    "completeness_rate": 完整度百分比(0-100),
    "has_inspection_record": true/false,
    "has_interview_record": true/false,
    "has_monitoring_report": true/false,
    "has_visual_evidence": true/false,
    "legality": "评价",
    "relevance": "评价",
    "objectivity": "评价",
    "problems": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"]
}}

只输出JSON。
"""
        
        response = await self._call_llm(prompt)
        return self._parse_response(response)


# 全局实例
ai_analyzer = AIAnalyzer()
