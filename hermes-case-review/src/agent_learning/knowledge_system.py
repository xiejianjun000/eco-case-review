"""
智能体知识学习系统核心模块
让AI智能体能够自动学习、理解、应用法律知识
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LegalProvision:
    """法律条文"""
    law_name: str          # 法律名称
    article: str           # 条款编号
    content: str           # 条款内容
    keywords: List[str]    # 关键词
    category: str         # 分类
    source_file: str       # 来源文件


@dataclass
class CaseAnalysis:
    """案卷分析结果"""
    case_id: str
    relevant_provisions: List[LegalProvision]  # 相关法条
    legal_issues: List[str]                   # 法律问题
    suggestions: List[str]                    # 处理建议
    reasoning: str                            # 推理过程


class AgentKnowledgeSystem:
    """
    智能体知识系统
    核心功能：
    1. 知识学习 - 自动阅读理解法律条文
    2. 知识检索 - 语义相似度匹配
    3. 案卷分析 - 对标法律条文，发现问题
    4. 思考推理 - 法律适用推理
    """
    
    def __init__(self, knowledge_base_path: str = "/workspace/hermes-case-review/knowledge"):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.provisions: List[LegalProvision] = []
        self.knowledge_index: Dict[str, Any] = {}
        
    def load_knowledge_base(self):
        """加载知识库"""
        print("📚 正在加载知识库...")
        
        # 加载索引文件
        index_file = self.knowledge_base_path / "knowledge_index.json"
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                self.knowledge_index = json.load(f)
            print(f"✅ 已加载索引: {len(self.knowledge_index.get('documents', []))} 个文档")
        
        # 加载Markdown文件
        md_files = list(self.knowledge_base_path.glob("**/*.md"))
        print(f"✅ 找到 {len(md_files)} 个Markdown文件")
        
        return len(md_files)
    
    def learn_legal_provisions(self, file_path: str) -> List[LegalProvision]:
        """学习法律条文"""
        provisions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取法条（这里使用简单的正则，实际需要更复杂的解析）
            import re
            # 匹配第X条、第X章等模式
            articles = re.split(r'(第[一二三四五六七八九十百]+[条章节款项]|第\d+[条章节款项])', content)
            
            law_name = Path(file_path).stem
            
            for i in range(1, len(articles), 2):
                if i < len(articles) - 1:
                    article_num = articles[i]
                    article_content = articles[i + 1]
                    
                    # 提取关键词
                    keywords = self._extract_keywords(article_content)
                    
                    provision = LegalProvision(
                        law_name=law_name,
                        article=article_num,
                        content=article_content[:500],  # 限制长度
                        keywords=keywords,
                        category=self._categorize(law_name),
                        source_file=file_path
                    )
                    provisions.append(provision)
            
            print(f"✅ 从 {law_name} 学习到 {len(provisions)} 条法律条文")
            
        except Exception as e:
            print(f"❌ 学习失败: {file_path} - {str(e)}")
        
        return provisions
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取，实际需要使用NLP
        important_words = [
            '违反', '处罚', '罚款', '责令', '限期',
            '情节严重', '从轻', '从重', '减轻',
            '超标', '非法', '擅自', '拒不', '故意'
        ]
        
        keywords = [word for word in important_words if word in text]
        return keywords[:5]  # 返回前5个关键词
    
    def _categorize(self, law_name: str) -> str:
        """分类"""
        if '水污染' in law_name:
            return '水污染防治'
        elif '大气' in law_name:
            return '大气污染防治'
        elif '固体' in law_name or '固废' in law_name:
            return '固体废物管理'
        elif '噪声' in law_name:
            return '噪声污染防治'
        elif '土壤' in law_name:
            return '土壤污染防治'
        elif '评查' in law_name or '裁量' in law_name:
            return '执法规范'
        elif '处罚' in law_name or '文书' in law_name:
            return '文书范本'
        else:
            return '其他'
    
    def analyze_case(self, case_content: str, case_type: str = "行政处罚") -> CaseAnalysis:
        """分析案卷"""
        print(f"🔍 正在分析案卷类型: {case_type}")
        
        # 1. 检索相关法条
        relevant_provisions = self._retrieve_relevant_provisions(case_content)
        
        # 2. 发现法律问题
        legal_issues = self._identify_legal_issues(case_content, relevant_provisions)
        
        # 3. 生成处理建议
        suggestions = self._generate_suggestions(legal_issues, relevant_provisions)
        
        # 4. 推理过程
        reasoning = self._generate_reasoning(case_content, relevant_provisions)
        
        return CaseAnalysis(
            case_id=f"case_{hash(case_content) % 10000}",
            relevant_provisions=relevant_provisions,
            legal_issues=legal_issues,
            suggestions=suggestions,
            reasoning=reasoning
        )
    
    def _retrieve_relevant_provisions(self, case_content: str) -> List[LegalProvision]:
        """检索相关法条"""
        # 简单的关键词匹配，实际需要使用向量检索
        relevant = []
        
        keywords = self._extract_keywords(case_content)
        
        for provision in self.provisions:
            # 检查关键词匹配
            if any(kw in provision.content for kw in keywords):
                relevant.append(provision)
        
        return relevant[:10]  # 返回最相关的10条
    
    def _identify_legal_issues(self, case_content: str, provisions: List[LegalProvision]) -> List[str]:
        """识别法律问题"""
        issues = []
        
        # 1. 检查是否违反程序
        if '未告知' in case_content or '未听取' in case_content:
            issues.append("可能违反法定程序（未告知当事人陈述申辩权）")
        
        # 2. 检查证据问题
        if '证据不足' in case_content or '缺少' in case_content:
            issues.append("可能存在证据不足问题")
        
        # 3. 检查裁量问题
        if '超标' in case_content:
            issues.append("需要根据裁量基准确定罚款金额")
        
        # 4. 检查主体问题
        if '主体' in case_content and ('错误' in case_content or '不清' in case_content):
            issues.append("处罚主体可能存在认定问题")
        
        return issues
    
    def _generate_suggestions(self, issues: List[str], provisions: List[LegalProvision]) -> List[str]:
        """生成建议"""
        suggestions = []
        
        for issue in issues:
            if '程序' in issue:
                suggestions.append("建议补充告知程序，确保当事人行使陈述申辩权")
            if '证据' in issue:
                suggestions.append("建议补充关键证据，完善证据链")
            if '裁量' in issue:
                suggestions.append("建议参照裁量基准，综合考虑违法情节")
            if '主体' in issue:
                suggestions.append("建议核实处罚对象，确保主体正确")
        
        if not suggestions:
            suggestions.append("案卷基本规范，建议继续完善细节")
        
        return suggestions
    
    def _generate_reasoning(self, case_content: str, provisions: List[LegalProvision]) -> str:
        """生成推理过程"""
        reasoning = f"""
## 法律推理过程

### 1. 事实认定
根据案卷内容，初步认定违法行为类型。

### 2. 法律检索
检索到 {len(provisions)} 条相关法律条文：
"""
        
        for i, prov in enumerate(provisions[:3], 1):
            reasoning += f"\n{i}. **{prov.law_name}** - {prov.article}"
            reasoning += f"\n   {prov.content[:200]}..."
        
        reasoning += f"""

### 3. 法律适用
根据相关法律规定，本案需要适用以下条款进行审查。

### 4. 裁量分析
结合违法情节，参照裁量基准确定处罚标准。

### 5. 结论
综合以上分析，形成最终评查结论。
"""
        
        return reasoning
    
    def think(self, question: str, context: str = "") -> str:
        """
        思考能力 - 让智能体能像法律专家一样思考
        
        思考框架：
        1. 问题理解 - 理解要解决的问题
        2. 知识检索 - 检索相关法律知识
        3. 规则应用 - 应用法律规则
        4. 逻辑推理 - 进行逻辑推理
        5. 结论形成 - 形成最终结论
        """
        
        thinking_process = f"""
# 法律思维分析

## 🤔 问题理解
{question}

{ "## 📋 背景信息\n" + context if context else "" }

## 🧠 思考过程

### 第一步：问题拆解
将问题拆解为若干子问题：
1. 本案涉及哪些法律关系？
2. 适用哪些法律条文？
3. 如何进行裁量？

### 第二步：知识检索
从知识库检索相关法律条文：
"""
        
        # 检索相关知识
        relevant = self._retrieve_relevant_provisions(question)
        for i, prov in enumerate(relevant[:5], 1):
            thinking_process += f"\n{i}. **{prov.law_name}** {prov.article}"
        
        thinking_process += """

### 第三步：法律分析
根据检索到的法律条文进行分析：

#### 法律规定分析
- 该行为违反了哪条规定？
- 法律责任是什么？
- 有哪些从轻、从重情节？

#### 裁量标准分析
- 违法情节严重程度？
- 超标倍数或违法所得？
- 是否及时纠正？

### 第四步：逻辑推理

**大前提**：法律规定...
**小前提**：本案事实...
**结论**：应当...

### 第五步：形成结论

基于以上分析，本案应当：
1. 认定违法事实
2. 确定适用法律
3. 计算罚款金额
4. 说明裁量理由

---
*此分析基于法律知识和推理得出，仅供参考*
"""
        
        return thinking_process


def main():
    """主函数 - 测试知识系统"""
    print("="*70)
    print("🧠 智能体知识学习系统测试")
    print("="*70)
    
    # 初始化系统
    system = AgentKnowledgeSystem()
    
    # 加载知识库
    doc_count = system.load_knowledge_base()
    
    # 学习法律条文
    md_files = list(system.knowledge_base_path.glob("**/*.md"))
    for md_file in md_files[:3]:  # 先学习前3个文件
        provisions = system.learn_legal_provisions(str(md_file))
        system.provisions.extend(provisions)
    
    print(f"\n📊 共学习 {len(system.provisions)} 条法律条文")
    
    # 测试思考能力
    print("\n" + "="*70)
    print("🧠 测试思考能力")
    print("="*70)
    
    test_question = "某企业超标排放水污染物，应当如何处罚？"
    result = system.think(test_question)
    print(result)
    
    # 测试案卷分析
    print("\n" + "="*70)
    print("📋 测试案卷分析")
    print("="*70)
    
    test_case = "某企业2024年3月排放口废水COD浓度为520mg/L，超过排放标准500mg/L，超标倍数为0.04倍..."
    analysis = system.analyze_case(test_case)
    
    print(f"\n📌 案卷ID: {analysis.case_id}")
    print(f"📚 相关法条: {len(analysis.relevant_provisions)} 条")
    print(f"⚠️ 法律问题: {len(analysis.legal_issues)} 个")
    print(f"💡 建议: {len(analysis.suggestions)} 条")
    
    print("\n" + "="*70)
    print("✅ 测试完成！")
    print("="*70)


if __name__ == "__main__":
    main()
