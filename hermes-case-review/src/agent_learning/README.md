# 智能体知识学习系统

## 系统概述

这是一个让HERMES智能体能够自动学习、理解、应用法律知识的系统。

## 目录结构

```
agent_learning/
├── knowledge_base/          # 知识库（已转换的MD文件）
│   ├── 评查细则/
│   ├── 法律法规/
│   ├── 复函汇编/
│   ├── 部长信箱/
│   └── 湖南省资料/
├── retrieval/              # 知识检索模块
│   ├── __init__.py
│   ├── vector_store.py     # 向量存储
│   ├── retriever.py       # 检索器
│   └── matcher.py          # 匹配器
├── learning/               # 学习模块
│   ├── __init__.py
│   ├── reader.py           # 知识阅读器
│   ├── analyzer.py         # 分析器
│   └── summarizer.py       # 摘要生成器
├── thinking/               # 思考模块
│   ├── __init__.py
│   ├── framework.py        # 思考框架
│   ├── reasoner.py         # 推理器
│   └── reflector.py        # 反思器
├── integration/            # 集成模块
│   ├── __init__.py
│   ├── agent_knowledge.py  # 智能体知识接口
│   └── case_analyzer.py    # 案卷分析器
└── prompts/                # 提示词模板
    ├── legal_thinking.txt  # 法律思考提示
    ├── case_analysis.txt   # 案卷分析提示
    └── learning_guide.txt  # 学习指南
```

## 核心功能

### 1. 知识检索
- 向量化存储法律条文
- 语义相似度匹配
- 多维度检索

### 2. 学习理解
- 自动阅读理解法律条文
- 提取关键要素
- 建立知识关联

### 3. 思考推理
- 法律适用推理
- 类案对比分析
- 逻辑一致性检验

### 4. 案卷分析
- 对标法律条文
- 发现法律问题
- 提出处理建议
