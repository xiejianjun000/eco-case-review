"""
智能体知识集成模块
将知识学习系统与HERMES智能体无缝集成
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from .knowledge_system import AgentKnowledgeSystem, LegalProvision, CaseAnalysis


class AgentKnowledgeIntegrator:
    """
    智能体知识集成器
    将法律知识系统集成到智能体的工作流程中
    """
    
    def __init__(self):
        self.knowledge_system = AgentKnowledgeSystem()
        self.initialized = False
        
    def initialize(self) -> bool:
        """初始化知识系统"""
        try:
            print("🔧 初始化智能体知识系统...")
            doc_count = self.knowledge_system.load_knowledge_base()
            
            # 学习所有Markdown文件
            md_files = list(self.knowledge_system.knowledge_base_path.glob("**/*.md"))
            for md_file in md_files:
                provisions = self.knowledge_system.learn_legal_provisions(str(md_file))
                self.knowledge_system.provisions.extend(provisions)
            
            self.initialized = True
            print(f"✅ 知识系统初始化完成！共加载 {len(self.knowledge_system.provisions)} 条法律条文")
            return True
            
        except Exception as e:
            print(f"❌ 初始化失败: {str(e)}")
            return False
    
    def get_system_prompt(self) -> str:
        """
        获取增强后的系统提示词
        包含法律知识和思考框架
        """
        base_prompt = """你是一位专业的生态环境行政执法案件审查专家。
你具备以下核心能力：
1. 深入理解环境保护法律体系
2. 掌握各污染防治法的适用范围
3. 熟悉行政处罚程序规定
4. 能够进行法律推理和裁量判断

在进行案卷审查时，你会：
1. 全面梳理案件涉及的法律法规条文
2. 对照法律条文分析案件事实
3. 进行逻辑推理，形成审查意见
4. 给出专业、准确的评查结论"""
        
        # 添加思考框架
        thinking_framework = """

## 思考框架

当你分析案件时，请按以下框架思考：

### 第一步：问题理解
- 准确识别问题的法律性质
- 确定涉及的法律法规
- 梳理法律关系

### 第二步：知识检索
- 从知识库检索相关法条
- 识别法条的构成要件
- 分析法条之间的关联

### 第三步：规则应用
- 将法律规则与大前提对应
- 将案件事实与小前提对应
- 检验逻辑一致性

### 第四步：逻辑推理
大前提：如果行为违反了第X条规定，则应当承担第Y条规定的法律责任
小前提：本案中该行为确实违反了第X条规定
结论：因此，本案应当承担第Y条规定的法律责任

### 第五步：裁量分析
- 识别法定裁量因素
- 确定从重从轻情节
- 计算罚款金额范围

### 第六步：结论形成
综合以上分析，形成明确结论，说明理由依据

## 25项评查标准

在进行案卷评查时，请重点检查以下25项标准：

### 一票否决项（序号1-8）
1. 处罚对象认定错误或不清
2. 主要事实认定不清
3. 违反法定程序
4. 适用法律依据错误
5. 超越职权
6. 滥用职权
7. 主要证据不足
8. 行政处罚明显不当

### 扣分项（序号9-25）
9. 未告知程序性权利
10. 未经集体讨论决定
11. 应经法制审核未审核
12. 应经集体讨论未讨论
13. 罚款金额计算错误
14. 法律引用不准确
15. 文书格式不规范
16. 签名盖章缺失
17. 日期错误
18. 证据链不完整
19. 裁量理由不充分
20. 救济途径告知不全
21. 文书送达不规范
22. 案卷装订不规范
23. 目录编制不规范
24. 副卷管理不规范
25. 其他不规范问题"""
        
        return base_prompt + thinking_framework
    
    def analyze_case_with_knowledge(self, case_content: str, case_type: str = "行政处罚") -> Dict[str, Any]:
        """
        使用知识系统分析案卷
        """
        if not self.initialized:
            self.initialize()
        
        # 调用知识系统分析
        analysis = self.knowledge_system.analyze_case(case_content, case_type)
        
        # 格式化结果
        result = {
            "case_id": analysis.case_id,
            "analysis": {
                "relevant_provisions": [
                    {
                        "law": p.law_name,
                        "article": p.article,
                        "content": p.content,
                        "keywords": p.keywords
                    }
                    for p in analysis.relevant_provisions
                ],
                "legal_issues": analysis.legal_issues,
                "suggestions": analysis.suggestions,
                "reasoning": analysis.reasoning
            }
        }
        
        return result
    
    def think_legal_question(self, question: str, context: str = "") -> str:
        """
        使用思考框架回答法律问题
        """
        if not self.initialized:
            self.initialize()
        
        return self.knowledge_system.think(question, context)
    
    def retrieve_legal_provisions(self, query: str, top_k: int = 5) -> List[Dict[str, str]]:
        """
        检索相关法律条文
        """
        if not self.initialized:
            self.initialize()
        
        provisions = self.knowledge_system._retrieve_relevant_provisions(query)
        
        return [
            {
                "law": p.law_name,
                "article": p.article,
                "content": p.content,
                "keywords": p.keywords,
                "category": p.category
            }
            for p in provisions[:top_k]
        ]


def create_agent_with_knowledge() -> AgentKnowledgeIntegrator:
    """创建带知识系统的智能体"""
    integrator = AgentKnowledgeIntegrator()
    integrator.initialize()
    return integrator
