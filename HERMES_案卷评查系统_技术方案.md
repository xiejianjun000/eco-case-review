
# HERMES + 生态环境案卷评查系统 整合方案

**版本**：V1.0
**日期**：2026-05-15
**说明**：基于HERMES Agent基座开发的生态环境行政处罚案卷评查智能系统

---

## 一、方案概述

### 1.1 项目背景

本方案将现有的**生态环境案卷评查系统（V4）**与**HERMES Agent**智能体框架深度整合，打造一个具备自我学习、多平台接入、完全自托管的专业案卷评查AI系统。

### 1.2 整合优势

| 特性 | 说明 |
|------|------|
| 🧠 **自我学习** | 从评查实践中自动沉淀专业技能，持续优化评查质量 |
| 🌐 **多平台接入** | 一套系统同时支持微信企业版、飞书、钉钉、Telegram等14+平台 |
| 🔒 **数据安全** | 完全自托管，案卷数据不出门，符合政务数据安全要求 |
| 🤖 **模型无关** | 支持GPT-4o、Claude 3.5、DeepSeek、GLM-4等200+模型 |
| 🔌 **MCP协议** | 既可作为MCP服务器被IDE调用，也可消费外部工具 |
| 🛠️ **47+内置工具** | 网页搜索、文件处理、代码执行等开箱即用 |

---

## 二、系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户交互层                                 │
│  Telegram  Discord  Slack  飞书  钉钉  微信企业版  API  WebUI   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   HERMES Agent 网关层                            │
│                 统一消息处理、会话管理、权限控制                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│               HERMES Agent 核心层（6个专业智能体）                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │合法性评查    │  │规范性评查    │  │裁量基准      │          │
│  │智能体        │  │智能体        │  │智能体        │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │证据链智能体  │  │文书完整性    │  │综合分析      │          │
│  │              │  │智能体        │  │智能体        │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    HERMES 技能库 &amp; 记忆库                         │
│  ┌─────────────────┐  ┌─────────────────┐                       │
│  │ 评查专业技能    │  │ 案卷知识记忆    │                       │
│  │ （自动沉淀）    │  │ （用户画像）    │                       │
│  └─────────────────┘  └─────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        基础设施层                                 │
│  文件存储  PostgreSQL  Redis  OCR引擎  模型API                   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 智能体映射关系

| 原V4系统智能体 | HERMES技能/Agent | 说明 |
|--------------|-----------------|------|
| 1. 合法性评查智能体 | `legality_review` 技能 | 一票否决制，25项检查 |
| 2. 规范性评查智能体 | `normative_scoring` 技能 | 文书评分，扣分制 |
| 3. 裁量基准智能体 | `discretion_calculation` 技能 | 罚款金额计算 |
| 4. 证据链智能体 | `evidence_chain` 技能 | 三性分析 |
| 5. 文书完整性智能体 | `document_completeness` 技能 | 14项文书检查 |
| 6. 综合分析智能体 | `comprehensive_analysis` 技能 | 汇总评分、报告生成 |

---

## 三、快速开始

### 3.1 安装HERMES Agent

```bash
# 克隆项目
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 验证安装
hermes doctor
```

### 3.2 配置项目

```bash
# 1. 运行初始化向导
hermes setup

# 2. 选择模型（推荐：DeepSeek-V3 或 GLM-4）
hermes model

# 3. 配置API Key
hermes config set DEEPSEEK_API_KEY your_key_here
# 或
hermes config set ZHIPUAI_API_KEY your_key_here

# 4. 创建项目目录
mkdir -p ~/.hermes/skills/case_review
mkdir -p ~/.hermes/data/cases
mkdir -p ~/.hermes/templates
```

### 3.3 导入案卷评查技能

```bash
# 复制技能文件到HERMES技能目录
cp hermes_skills/*.yaml ~/.hermes/skills/

# 验证技能已加载
hermes skills list
```

---

## 四、核心技能设计

### 4.1 技能目录结构

```
~/.hermes/skills/
├── case_review/
│   ├── legality_review.yaml          # 合法性评查
│   ├── normative_scoring.yaml        # 规范性评分
│   ├── discretion_calculation.yaml   # 裁量基准计算
│   ├── evidence_chain.yaml           # 证据链分析
│   ├── document_completeness.yaml    # 文书完整性检查
│   └── comprehensive_analysis.yaml   # 综合分析
└── utils/
    ├── pdf_parser.yaml               # PDF解析
    ├── ocr_helper.yaml               # OCR辅助
    └── report_generator.yaml         # 报告生成
```

### 4.2 核心技能示例

#### 技能1：合法性评查（legality_review.yaml）

```yaml
name: legality_review
description: 生态环境行政处罚案卷合法性评查（一票否决制）
version: "4.0"
author: 生态环境案卷评查系统
tags:
  - case_review
  - legality
  - environmental_law

inputs:
  - name: case_file
    type: file
    description: 案卷PDF文件或目录路径
    required: true
  - name: case_type
    type: string
    description: 案件类型（一般处罚/不予处罚/按日连续/查封扣押/移送拘留/移送犯罪）
    default: 一般行政处罚
    required: false

steps:
  - tool: llm
    prompt: |
      你是生态环境行政执法案卷合法性审查专家。
      
      评查依据：
      - 《生态环境行政执法案卷评查细则（2024年版）》
      - 《行政处罚法》（2021修订）
      - 《行政强制法》
      - 《环境保护法》
      
      评查领域（25项重大问题，一票否决）：
      1. 执法主体（2项）
      2. 违法主体（3项）
      3. 违法事实证据（2项）
      4. 法律适用（6项）
      5. 执法程序（12项）
      
      请对案卷进行全面合法性审查，输出：
      - 是否触发一票否决
      - 具体问题清单（含评查细则条款、法律依据、证据页码）
      - 合法性评分（0或50分）

  - tool: terminal
    command: |
      python -c "
      import json
      result = {'has_veto': False, 'veto_items': [], 'score': 50}
      # 在此处实现具体评查逻辑
      print(json.dumps(result, ensure_ascii=False))
      "
    description: 执行合法性评分计算

  - tool: file_write
    path: "${case_file}_legality_report.json"
    content: "${llm_output}"
    description: 保存合法性评查报告

outputs:
  - name: legality_report
    type: file
    description: 合法性评查报告
  - name: has_veto
    type: boolean
    description: 是否触发一票否决
  - name: legality_score
    type: number
    description: 合法性评分（0或50）
```

#### 技能2：规范性评查（normative_scoring.yaml）

```yaml
name: normative_scoring
description: 生态环境行政处罚案卷规范性评分
version: "4.0"
author: 生态环境案卷评查系统
tags:
  - case_review
  - normative
  - scoring

inputs:
  - name: case_file
    type: file
    description: 案卷PDF文件
    required: true
  - name: legality_passed
    type: boolean
    description: 合法性是否通过
    default: true

steps:
  - tool: llm
    prompt: |
      你是生态环境行政执法案卷规范性评分专家。
      
      评分标准：
      1. 卷面基本要素评查（20分，扣分制）
         - 文书基本要素（10分）
         - 笔录基本要素（10分）
      2. 各类型文书评查（100分→折算50分，得分制）
         - 立案审批表（2分）
         - 现场检查笔录（10分）
         - 调查询问笔录（10分）
         - 监测报告（5分）
         - 其他证据（8分）
         - 案件调查报告（8分）
         - 责令改正决定书（10分）
         - 行政处罚事先告知书（10分）
         - 听证通知书（4分）
         - 听证笔录（8分）
         - 行政处罚决定书（15分）
         - 催告书（2分）
         - 强制执行申请书（5分）
         - 结案审批表（3分）
      
      计算公式：
      规范性得分 = 50 × (文书得分 / 标准分) - 基本要素扣分
      
      请输出详细评分明细表。

  - tool: python
    script: |
      # 规范性评分计算逻辑
      document_score = 85  # 示例
      document_standard = 100
      basic_deduction = 3
      
      normative_score = 50 * (document_score / document_standard) - basic_deduction
      
      print(f"规范性得分: {normative_score}")
    description: 计算规范性得分

outputs:
  - name: normative_score
    type: number
    description: 规范性评分（0-50）
  - name: scoring_detail
    type: file
    description: 评分明细表
```

---

## 五、工作流程设计

### 5.1 完整案卷评查流程

```yaml
name: full_case_review
description: 生态环境行政处罚案卷完整评查流程
version: "1.0"

steps:
  # 步骤1：案卷上传与解析
  - name: parse_case
    use: pdf_parser
    inputs:
      file: "${case_pdf}"

  # 步骤2：合法性评查（一票否决）
  - name: legality_check
    use: legality_review
    inputs:
      case_file: "${case_pdf}"

  # 步骤3：如果合法性通过，继续规范性评查
  - name: normative_check
    use: normative_scoring
    inputs:
      case_file: "${case_pdf}"
      legality_passed: "${legality_check.has_veto == false}"
    if: "${legality_check.has_veto == false}"

  # 步骤4：裁量基准计算
  - name: discretion_check
    use: discretion_calculation
    inputs:
      case_file: "${case_pdf}"
    if: "${legality_check.has_veto == false}"

  # 步骤5：证据链分析
  - name: evidence_analysis
    use: evidence_chain
    inputs:
      case_file: "${case_pdf}"
    if: "${legality_check.has_veto == false}"

  # 步骤6：文书完整性检查
  - name: document_check
    use: document_completeness
    inputs:
      case_file: "${case_pdf}"
    if: "${legality_check.has_veto == false}"

  # 步骤7：综合分析与报告生成
  - name: final_analysis
    use: comprehensive_analysis
    inputs:
      legality_result: "${legality_check}"
      normative_result: "${normative_check}"
      discretion_result: "${discretion_check}"
      evidence_result: "${evidence_analysis}"
      document_result: "${document_check}"

  # 步骤8：生成最终报告
  - name: generate_report
    use: report_generator
    inputs:
      analysis_data: "${final_analysis}"
      template: "eco_review_template_v4.docx"
```

### 5.2 对话式使用示例

```
用户：帮我评查这份行政处罚案卷

[HERMES自动调用 full_case_review 技能]

HERMES：收到！正在进行案卷评查...

[执行合法性评查...]
HERMES：📋 合法性评查完成
  ✓ 未触发一票否决
  ✓ 合法性得分：50分

[执行规范性评查...]
HERMES：📊 规范性评分完成
  ✓ 文书得分：85/100
  ✓ 基本要素扣分：3分
  ✓ 规范性得分：39.5分

[执行裁量基准检查...]
[执行证据链分析...]
[执行文书完整性检查...]

HERMES：✅ 评查完成！
  综合得分：89.5分
  等级：良好
  详细报告已生成：report_20260515.docx
```

---

## 六、多平台接入配置

### 6.1 飞书/钉钉配置

```bash
# 配置网关
hermes gateway setup

# 选择平台
? 选择要配置的平台：
❯ 飞书（Feishu）
  钉钉（DingTalk）
  微信企业版（WeCom）
  Telegram
  ...

# 按照向导完成配置后启动网关
hermes gateway start --daemon
```

### 6.2 平台使用示例

**飞书群聊中：**
```
@评查机器人 帮我评查这份案卷[上传PDF]
```

**Telegram中：**
```
/start
/upload_case [案卷PDF]
/review
```

---

## 七、MCP服务器集成

### 7.1 作为MCP服务器被IDE调用

HERMES可以作为MCP服务器，被Cursor、VS Code、Claude Desktop等IDE调用，提供案卷评查能力。

配置文件 `~/.hermes/mcp_config.yaml`：

```yaml
mcp_servers:
  - name: case_review
    command: hermes
    args:
      - mcp
      - --skill
      - case_review
```

### 7.2 在IDE中使用

```
用户（在Cursor中）：帮我对当前目录下的案卷进行评查

[HERMES MCP服务器自动响应，调用案卷评查技能]
```

---

## 八、记忆与学习机制

### 8.1 专业知识记忆

HERMES会自动学习：
- 常见问题类型
- 评查标准细节
- 用户偏好设置
- 历史评查案例

### 8.2 技能自动沉淀

每次评查完成后，HERMES会自动：
```
✓ 发现可复用评查模式
✓ 询问是否保存为新技能
✓ 更新技能库
✓ 下次直接调用，越用越准
```

---

## 九、部署方案

### 9.1 Docker部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  hermes-case-review:
    image: hermes-agent:latest
    volumes:
      - ./skills:/root/.hermes/skills
      - ./data:/root/.hermes/data
      - ./cases:/app/cases
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - HERMES_CONFIG=/root/.hermes/config.yaml
    ports:
      - "8080:8080"
    restart: unless-stopped
```

### 9.2 Kubernetes部署

参见原V4系统的K8s配置：
[deploy/k8s/](file:///c:\Users\Administrator\Desktop\案卷评查\2026-05-13-task-1\deliverables\chatlaw\v4-docker-deployment\k8s)

---

## 十、监控与安全

### 10.1 监控告警

沿用V4系统的Prometheus + Grafana方案：
- [v4-monitoring/](file:///c:\Users\Administrator\Desktop\案卷评查\2026-05-13-task-1\deliverables\chatlaw\v4-monitoring)

### 10.2 安全加固

- 敏感信息脱敏
- RBAC权限控制
- 审计日志
- 参见：[v4-security/](file:///c:\Users\Administrator\Desktop\案卷评查\2026-05-13-task-1\deliverables\chatlaw\v4-security)

---

## 十一、测试与验证

使用原V4系统的测试套件：

```bash
# 运行自动化测试
cd deliverables/chatlaw
pytest v4-test-suite.py -v
```

---

## 十二、下一步行动

1. ✅ 安装HERMES Agent
2. ✅ 配置模型API Key
3. ✅ 导入案卷评查技能
4. ✅ 测试单个技能
5. ✅ 配置消息平台网关
6. ✅ 部署到生产环境
7. ✅ 开始评查实践，让HERMES自动学习沉淀技能

---

## 附录

### A. 参考资源

- HERMES Agent 官方文档：https://hermes.xaapi.ai/
- HERMES Agent GitHub：https://github.com/NousResearch/hermes-agent
- 原V4案卷评查系统文档：[electric-beacon-einstein.md](file:///c:\Users\Administrator\Desktop\案卷评查\electric-beacon-einstein.md)
- 合法性评查规则：[v4-legality-review-rules.md](file:///c:\Users\Administrator\Desktop\案卷评查\2026-05-13-task-1\deliverables\chatlaw\v4-legality-review-rules.md)

### B. 联系方式

- 生态环境案卷评查系统团队
- HERMES Agent社区

---

**文档结束**
