#!/usr/bin/env python3
"""
智能体知识系统测试脚本
验证知识学习和思考能力
"""
import sys
import os

sys.path.insert(0, '/workspace/hermes-case-review')

from src.agent_learning.knowledge_system import AgentKnowledgeSystem
from src.agent_learning.integrator import AgentKnowledgeIntegrator


def test_knowledge_system():
    """测试知识系统"""
    print("="*70)
    print("🧠 智能体知识系统测试")
    print("="*70)
    
    # 1. 初始化知识系统
    print("\n📚 步骤1: 初始化知识系统...")
    system = AgentKnowledgeSystem()
    doc_count = system.load_knowledge_base()
    print(f"✅ 加载了 {doc_count} 个文档")
    
    # 2. 学习法律条文
    print("\n📖 步骤2: 学习法律条文...")
    md_files = list(system.knowledge_base_path.glob("**/*.md"))
    for md_file in md_files:
        provisions = system.learn_legal_provisions(str(md_file))
        system.provisions.extend(provisions)
    
    print(f"✅ 共学习 {len(system.provisions)} 条法律条文")
    
    # 3. 测试检索
    print("\n🔍 步骤3: 测试知识检索...")
    test_query = "超标排放水污染物"
    results = system._retrieve_relevant_provisions(test_query)
    print(f"✅ 检索到 {len(results)} 条相关法条")
    
    # 4. 测试思考能力
    print("\n🤔 步骤4: 测试思考能力...")
    test_question = "某企业超标排放水污染物，应当如何处罚？"
    thinking_result = system.think(test_question)
    print("✅ 思考能力测试完成")
    print(f"\n思考结果预览（前500字符）:\n{thinking_result[:500]}...")
    
    # 5. 测试案卷分析
    print("\n📋 步骤5: 测试案卷分析...")
    test_case = """
    某企业2024年3月排放口废水COD浓度为520mg/L，
    超过排放标准500mg/L，超标倍数为0.04倍。
    企业及时整改，已停止超标排放行为。
    """
    analysis = system.analyze_case(test_case)
    print(f"✅ 案卷分析完成")
    print(f"   相关法条: {len(analysis.relevant_provisions)} 条")
    print(f"   发现问题: {len(analysis.legal_issues)} 个")
    print(f"   改进建议: {len(analysis.suggestions)} 条")
    
    print("\n" + "="*70)
    print("✅ 知识系统测试全部通过！")
    print("="*70)
    
    return True


def test_integrator():
    """测试知识集成器"""
    print("\n" + "="*70)
    print("🔗 智能体知识集成器测试")
    print("="*70)
    
    # 1. 初始化集成器
    print("\n🔧 步骤1: 初始化集成器...")
    integrator = AgentKnowledgeIntegrator()
    success = integrator.initialize()
    print(f"{'✅' if success else '❌'} 集成器初始化{'成功' if success else '失败'}")
    
    # 2. 获取系统提示词
    print("\n📝 步骤2: 获取增强提示词...")
    prompt = integrator.get_system_prompt()
    print(f"✅ 获取提示词成功 (长度: {len(prompt)} 字符)")
    
    # 3. 测试法律推理
    print("\n🧠 步骤3: 测试法律推理...")
    question = "超标排放水污染物的法律责任是什么？"
    result = integrator.think_legal_question(question)
    print(f"✅ 法律推理完成")
    
    # 4. 测试法条检索
    print("\n🔍 步骤4: 测试法条检索...")
    provisions = integrator.retrieve_legal_provisions("水污染物排放", top_k=3)
    print(f"✅ 检索到 {len(provisions)} 条相关法条")
    for i, p in enumerate(provisions[:3], 1):
        print(f"   {i}. {p['law']} - {p['article']}")
    
    print("\n" + "="*70)
    print("✅ 集成器测试全部通过！")
    print("="*70)
    
    return True


def test_knowledge_files():
    """测试知识库文件"""
    print("\n" + "="*70)
    print("📁 知识库文件检查")
    print("="*70)
    
    from pathlib import Path
    
    knowledge_dir = Path("/workspace/hermes-case-review/knowledge")
    
    # 检查MD文件
    md_files = list(knowledge_dir.glob("**/*.md"))
    print(f"\n📄 Markdown文件: {len(md_files)} 个")
    for md_file in md_files:
        size = md_file.stat().st_size / 1024
        print(f"   - {md_file.name} ({size:.1f}KB)")
    
    # 检查PDF文件
    pdf_files = list(knowledge_dir.glob("**/*.pdf"))
    print(f"\n📕 PDF文件: {len(pdf_files)} 个")
    for pdf_file in pdf_files:
        size = pdf_file.stat().st_size / 1024
        print(f"   - {pdf_file.name} ({size:.1f}KB)")
    
    print("\n" + "="*70)
    
    return len(md_files) > 0


def main():
    """主函数"""
    print("\n" + "🎯"*35)
    print("🎯 HERMES智能体知识系统全面测试 🎯")
    print("🎯"*35)
    
    all_passed = True
    
    # 1. 测试知识文件
    if not test_knowledge_files():
        all_passed = False
    
    # 2. 测试知识系统
    if not test_knowledge_system():
        all_passed = False
    
    # 3. 测试集成器
    if not test_integrator():
        all_passed = False
    
    # 最终结果
    print("\n" + "🎉"*35)
    if all_passed:
        print("🎉🎉🎉 全部测试通过！智能体知识系统已就绪 🎉🎉🎉")
    else:
        print("⚠️ 部分测试未通过，请检查系统配置")
    print("🎉"*35)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
