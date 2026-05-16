# 生态环境案卷评查系统 Code Wiki

## 项目概述

本文档为生态环境案卷评查系统提供全面的代码架构参考,涵盖项目结构、主要模块职责、核心类与函数、依赖关系及运行方式等关键信息。该系统基于HERMES Agent框架开发,支持合法性评查、规范性评分、裁量基准计算等功能,适用于生态环境行政处罚案卷的智能评查。

## 1 项目整体架构

### 1.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户交互层                                 │
│         CLI / API / 飞书 / 钉钉 / Telegram / Web UI             │
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
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │合法性评查    │  │规范性评查    │  │裁量基准      │            │
│  │智能体        │  │智能体        │  │智能体        │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │证据链智能体  │  │文书完整性    │  │综合分析      │            │
│  │              │  │智能体        │  │智能体        │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    HERMES 技能库 & 记忆库                         │
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

### 1.2 项目目录结构

```
hermes-case-review/
├── src/                          # Python后端源代码
│   ├── __init__.py              # 包初始化
│   ├── main.py                  # CLI命令行入口
│   ├── api/                     # API服务模块
│   │   ├── __init__.py
│   │   └── routes.py            # FastAPI路由定义
│   ├── config/                  # 配置模块
│   │   ├── __init__.py
│   │   └── settings.py          # 系统配置
│   ├── engine/                  # 核心评分引擎
│   │   ├── __init__.py
│   │   ├── scoring_engine.py    # 评分引擎核心
│   │   ├── ai_analyzer.py      # AI分析器
│   │   ├── discretion_calculator.py  # 裁量基准计算
│   │   ├── evidence_analyzer.py      # 证据链分析
│   │   └── self_learning.py          # 自我学习模块
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic数据模型
│   ├── skills/                  # HERMES技能定义
│   │   ├── legality_review.yaml      # 合法性评查技能
│   │   ├── normative_scoring.yaml    # 规范性评分技能
│   │   └── comprehensive_analysis.yaml  # 综合分析技能
│   └── utils/                   # 工具函数
│       ├── file_parser.py       # 文件解析
│       ├── message_gateway.py   # 消息网关
│       └── report_generator.py  # 报告生成
├── frontend/                     # Vue.js前端
│   ├── src/
│   │   ├── main.ts             # 前端入口
│   │   ├── App.vue             # 根组件
│   │   ├── router/             # 路由配置
│   │   ├── stores/             # 状态管理
│   │   ├── views/              # 页面组件
│   │   └── style.css           # 全局样式
│   ├── package.json            # 前端依赖
│   ├── vite.config.ts         # Vite配置
│   └── tsconfig.json           # TypeScript配置
├── templates/                    # Agent模板
│   ├── agent_memory_template.md
│   ├── agent_rules_template.md
│   ├── agent_skills_template.md
│   ├── agent_soul_template.md
│   └── agent_tools_template.md
├── tests/                        # 测试用例
│   ├── __init__.py
│   └── test_engine.py          # 引擎单元测试
├── test_data/                   # 测试数据
│   └── test_case_001.json
├── requirements.txt             # Python依赖
├── README.md                    # 项目说明
├── GETTING_STARTED.md          # 快速开始指南
├── MULTI_AGENT_DESIGN.md       # 多智能体设计文档
├── AGENT_CONFIGURATION_GUIDE.md  # Agent配置指南
└── FRONTEND_DESIGN.md          # 前端设计文档
```

### 1.3 技术栈概览

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| 后端框架 | FastAPI | 高性能异步API框架 |
| 数据验证 | Pydantic | 数据模型定义与验证 |
| AI模型 | OpenAI/DeepSeek/Claude | 大语言模型集成 |
| 任务队列 | Celery + Redis | 异步任务处理 |
| 前端框架 | Vue 3 + TypeScript | 渐进式前端框架 |
| 状态管理 | Pinia | Vue状态管理 |
| UI组件 | Element Plus | Vue 3 UI组件库 |
| 构建工具 | Vite | 现代前端构建工具 |
| 文档格式 | YAML | 技能配置文件 |

## 2 主要模块职责

### 2.1 CLI入口模块

**文件位置**: `src/main.py`

**核心功能**: 提供命令行界面,支持案卷评查、合法性检查、评分标准查看等操作。

**主要命令**:

```python
# 评查案卷
python -m src.main review <case_file> [options]

# 检查合法性标准
python -m src.main legality-check

# 显示评分标准
python -m src.main standards

# 计算等级
python -m src.main calculate-grade <score>

# 显示当前配置
python -m src.main config
```

**支持的案件类型**:

- 一般行政处罚
- 不予行政处罚
- 按日连续处罚
- 查封扣押
- 移送拘留
- 移送涉嫌环境污染犯罪

### 2.2 API服务模块

**文件位置**: `src/api/routes.py`

**核心功能**: 提供RESTful API接口,支持案卷上传、评查执行、结果查询等操作。

**主要端点**:

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | API根路径,返回服务状态 |
| `/health` | GET | 健康检查接口 |
| `/api/v1/review` | POST | 案卷评查接口 |
| `/api/v1/review/upload` | POST | 文件上传评查 |
| `/api/v1/standards/legality` | GET | 获取合法性标准 |
| `/api/v1/standards/normative` | GET | 获取规范性标准 |
| `/api/v1/calculate` | GET | 评分计算接口 |

**启动方式**:

```bash
python -m src.api.routes
# 访问 http://localhost:8000/docs 查看API文档
```

### 2.3 评分引擎模块

**文件位置**: `src/engine/scoring_engine.py`

**核心功能**: 实现案卷评分的核心逻辑,包括规范性评分计算、综合得分计算、等级判定等功能。

**包含组件**:

- **ScoringEngine**: 评分引擎主类
- **VetoChecker**: 否决条件检查器

### 2.4 数据模型模块

**文件位置**: `src/models/schemas.py`

**核心功能**: 定义系统使用的数据结构和枚举类型,使用Pydantic进行数据验证。

**主要枚举**:

- CaseType: 案件类型枚举
- VetoCategory: 否决类别枚举
- ReviewGrade: 评查等级枚举

### 2.5 配置模块

**文件位置**: `src/config/settings.py`

**核心功能**: 管理系统配置,包括应用设置、HERMES模型配置、文件路径配置、评分阈值配置等。

## 3 关键类与函数说明

### 3.1 ScoringEngine类

**位置**: `src/engine/scoring_engine.py`

**功能描述**: 评分引擎核心类,负责规范性评分计算、综合得分计算和等级判定。

**类属性**:

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| legality_pass_score | int | 50 | 合法性通过分数 |
| legality_fail_score | int | 0 | 合法性失败分数 |
| normative_max_score | int | 50 | 规范性最高分 |
| comprehensive_max_score | int | 100 | 综合最高分 |
| grade_thresholds | dict | 见下方 | 等级阈值配置 |

**等级阈值配置**:

```python
self.grade_thresholds = {
    ReviewGrade.EXCELLENT: 90.0,   # 优秀: ≥90分
    ReviewGrade.GOOD: 80.0,       # 良好: 80-89分
    ReviewGrade.QUALIFIED: 60.0   # 合格: 60-79分
}
```

**核心方法**:

#### calculate_normative_score()

**功能**: 计算规范性评分

**参数**:

- `document_score`: float - 文书实际得分
- `document_standard`: float - 文书标准分
- `basic_deduction`: float - 基本要素扣分

**返回**: float - 规范性评分（0-50）

**计算公式**:

```
规范性得分 = 50 × (文书得分 / 标准分) - 基本要素扣分
```

**实现逻辑**:

```python
def calculate_normative_score(self, document_score, document_standard, basic_deduction):
    if document_standard == 0:
        return 0.0
    ratio = document_score / document_standard
    normative_score = 50 * ratio - basic_deduction
    return max(0.0, min(self.normative_max_score, normative_score))
```

#### calculate_comprehensive_score()

**功能**: 计算综合得分

**参数**:

- `legality_score`: int - 合法性评分（0或50）
- `normative_score`: float - 规范性评分（0-50）

**返回**: float - 综合得分（0-100）

**计算公式**:

```
综合得分 = 合法性得分 + 规范性得分
```

#### determine_grade()

**功能**: 根据综合得分确定评查等级

**参数**:

- `comprehensive_score`: float - 综合得分

**返回**: ReviewGrade - 评查等级

**等级判定规则**:

| 综合得分 | 等级 |
|---------|------|
| ≥90分 | 优秀 |
| 80-89分 | 良好 |
| 60-79分 | 合格 |
| <60分 | 不合格 |

#### determine_pass()

**功能**: 判断案卷是否通过评查

**参数**:

- `legality_score`: int - 合法性评分
- `comprehensive_score`: float - 综合得分

**返回**: bool - 是否通过

**判定规则**:

- 触发一票否决（合法性=0）→ 不通过
- 未触发否决且综合得分<60 → 不通过
- 未触发否决且综合得分≥60 → 通过

#### process_full_review()

**功能**: 处理完整评查流程

**参数**:

- `case_data`: dict - 案卷数据字典

**返回**: tuple - (综合得分, 等级, 是否通过, 评查结果详情)

### 3.2 VetoChecker类

**位置**: `src/engine/scoring_engine.py`

**功能描述**: 否决条件检查器,负责检查25项一票否决条件。

**否决项分类**:

| 类别 | 数量 | 编号范围 |
|------|------|----------|
| 执法主体 | 2项 | 1-2 |
| 违法主体 | 3项 | 3-5 |
| 违法事实证据 | 2项 | 6-7 |
| 法律适用 | 6项 | 8-13 |
| 执法程序 | 12项 | 14-25 |

**25项否决条件详情**:

| 编号 | 检查项 | 描述 |
|------|--------|------|
| 1 | 实施机关职权 | 实施机关超出法定职权、管辖范围实施行政处罚或行政强制 |
| 2 | 执法人员资格 | 执法人员不具有行政执法资格,或少于两人 |
| 3 | 违法主体不清 | 案卷中不同文书当事人名称不一致,且无合理解释 |
| 4 | 处罚对象错误 | 行政处罚或行政强制的对象不是证据材料中查明的违法主体 |
| 5 | 事实与证据不符 | 决定书中认定的违法事实与证据材料所指向的违法事实不符 |
| 6 | 证据不足 | 证据材料不足以证明当事人的违法行为而予以处罚 |
| 7 | 未核实主观过错 | 当事人有证据足以证明没有主观过错,未经核实仍予以处罚 |
| 8 | 事实描述不符 | 违法事实认定的描述与适用的法律规定不符 |
| 9 | 无法律依据 | 作出的决定无法律、法规、规章依据 |
| 10 | 未准确引用 | 决定书中未准确引用法律、法规、规章的相应条款 |
| 11 | 兜底条款滥用 | 无法定理由和证据适用法律、法规、规章规定的兜底条款或等外条款 |
| 12 | 加重/减轻处罚错误 | 加重行政处罚或无法定理由减轻行政处罚 |
| 13 | 查封扣押对象错误 | 查封、扣押与违法行为无关的设施、设备、物品、工具或场所 |
| 14 | 未告知程序性权利 | 作出行政处罚决定前未告知程序性权利（陈述、申辩、听证等） |
| 15 | 未对申请作出决定 | 虽告知上述权利但未对回避申请作出决定,拒绝听取陈述申辩,未举行听证 |
| 16 | 查封扣押未告知 | 查封、扣押未当场告知当事人采取行政强制措施的理由、依据及权利 |
| 17 | 未经集体讨论 | 对情节复杂或者重大违法行为给予行政处罚前,未经行政机关负责人集体讨论决定 |
| 18 | 调查人员参与表决 | 集体讨论时,调查人员参与了表决 |
| 19 | 应审核未审核 | 应经法制审核才能作出决定的,未按规定进行法制审核或法制审核未通过即作出决定 |
| 20 | 超过追责期限 | 对超过法定追责期限的违法行为给予行政处罚 |
| 21 | 调查审查人员混同 | 案件调查人员同时作为本案的审查人员 |
| 22 | 未责令改正 | 作出按日连续处罚决定前,没有证据证明已责令当事人改正违法行为 |
| 23 | 未在规定时间复查 | 责令改正之后,作出按日连续处罚决定前,未在规定时间内实施复查 |
| 24 | 处罚决定书时间错误 | 按日连续处罚决定书早于原行政处罚决定书作出或送达 |
| 25 | 查封扣押超期 | 查封、扣押超期未作出解除决定,或者未经批准延长查封、扣押期限 |

**核心方法**:

#### check_veto()

**功能**: 检查是否触发一票否决

**参数**:

- `case_data`: dict - 案卷数据

**返回**: tuple - (是否触发否决, 否决项编号列表, 否决项详情列表)

### 3.3 数据模型类

**位置**: `src/models/schemas.py`

#### CaseType枚举

```python
class CaseType(str, Enum):
    GENERAL_PENALTY = "一般行政处罚"
    NO_PENALTY = "不予行政处罚"
    DAILY_PENALTY = "按日连续处罚"
    SEAL_CONFISCATION = "查封扣押"
    TRANSFER_DETENTION = "移送拘留"
    TRANSFER_CRIME = "移送涉嫌环境污染犯罪"
```

#### VetoCategory枚举

```python
class VetoCategory(str, Enum):
    ENFORCEMENT_SUBJECT = "执法主体"
    ILLEGAL_SUBJECT = "违法主体"
    EVIDENCE = "违法事实证据"
    LEGAL_APPLICATION = "法律适用"
    ENFORCEMENT_PROCEDURE = "执法程序"
```

#### ReviewGrade枚举

```python
class ReviewGrade(str, Enum):
    EXCELLENT = "优秀"
    GOOD = "良好"
    QUALIFIED = "合格"
    UNQUALIFIED = "不合格"
```

#### CaseReviewResult模型

**功能**: 案卷评查结果完整模型

**字段**:

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| case_id | str | 是 | 案卷ID |
| case_number | str | 是 | 案号 |
| case_name | str | 是 | 案件名称 |
| case_type | CaseType | 是 | 案件类型 |
| respondent | str | 是 | 违法当事人 |
| organizing_unit | str | 是 | 承办单位 |
| violation | str | 是 | 违法行为 |
| penalty_decision | str | 是 | 处罚决定 |
| filing_date | datetime | 是 | 送卷日期 |
| review_date | datetime | 否 | 评查完成日期 |
| file_pages | int | 是 | 文件页数 |
| legality_review | LegalityReview | 是 | 合法性评查 |
| normative_review | NormativeReview | 是 | 规范性评查 |
| discretion | DiscretionReview | 是 | 裁量基准 |
| evidence_chain | EvidenceChain | 是 | 证据链分析 |
| documents | DocumentCompleteness | 是 | 文书完整性 |
| comprehensive_score | float | 是 | 综合得分（0-100） |
| comprehensive_grade | ReviewGrade | 是 | 评查等级 |
| comprehensive_pass | bool | 是 | 是否通过 |
| report_file | str | 否 | 报告文件路径 |

### 3.4 API路由函数

**位置**: `src/api/routes.py`

#### root()

**功能**: API根路径,返回服务状态信息

**请求**: GET /

**响应**:

```json
{
    "name": "生态环境案卷评查系统",
    "version": "1.0.0",
    "status": "running"
}
```

#### health_check()

**功能**: 健康检查接口

**请求**: GET /health

**响应**:

```json
{
    "status": "healthy"
}
```

#### review_case()

**功能**: 案卷评查接口

**请求**: POST /api/v1/review

**请求体**:

```json
{
    "case_id": "可选的案卷ID",
    "case_data": {
        "document_score": 85,
        "document_standard": 100,
        "basic_deduction": 3,
        "veto_1": false
    },
    "case_type": "一般行政处罚"
}
```

**响应**:

```json
{
    "success": true,
    "case_id": "case_001",
    "comprehensive_score": 89.5,
    "grade": "良好",
    "is_pass": true,
    "legality_score": 50,
    "normative_score": 39.5,
    "veto_items": []
}
```

#### upload_and_review()

**功能**: 上传案卷文件并进行评查

**请求**: POST /api/v1/review/upload

**参数**:

- file: UploadFile - 案卷文件（支持PDF、TXT、JSON）
- case_type: str - 案件类型

**响应**: 同review_case()

#### get_legality_standards()

**功能**: 获取合法性评查标准

**请求**: GET /api/v1/standards/legality

**响应**:

```json
{
    "total_items": 25,
    "categories": {
        "执法主体": [1, 2],
        "违法主体": [3, 4, 5],
        "违法事实证据": [6, 7],
        "法律适用": [8, 9, 10, 11, 12, 13],
        "执法程序": [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
    },
    "items": {...}
}
```

#### get_normative_standards()

**功能**: 获取规范性评分标准

**请求**: GET /api/v1/standards/normative

**响应**:

```json
{
    "basic_elements": {
        "total_score": 20,
        "documents": {...},
        "records": {...}
    },
    "document_scoring": {
        "total_score": 100,
        "convert_to": 50,
        "documents": [...]
    },
    "formula": "规范性得分 = 50 × (文书得分 / 标准分) - 基本要素扣分"
}
```

### 3.5 CLI命令函数

**位置**: `src/main.py`

#### cli()

**功能**: CLI主命令组

**用法**:

```bash
python -m src.main [COMMAND]
```

#### review()

**功能**: 案卷评查命令

**用法**:

```bash
python -m src.main review <CASE_FILE> [OPTIONS]
```

**选项**:

- `--type`, `-t`: 案件类型（默认: 一般行政处罚）
- `--output`, `-o`: 输出文件路径（JSON格式）
- `--verbose`, `-v`: 详细输出

**示例**:

```bash
python -m src.main review test_data/test_case_001.json --verbose
```

#### legality_check()

**功能**: 显示25项合法性否决条件

**用法**:

```bash
python -m src.main legality-check
```

#### standards()

**功能**: 显示评分标准

**用法**:

```bash
python -m src.main standards
```

#### calculate_grade()

**功能**: 计算等级

**用法**:

```bash
python -m src.main calculate-grade <SCORE>
```

#### config()

**功能**: 显示当前配置

**用法**:

```bash
python -m src.main config
```

#### parse_case_file()

**功能**: 解析案卷文件

**支持格式**:

- `.json`: JSON格式,直接解析
- `.txt`: 文本格式,简单解析
- `.pdf`: PDF格式（暂未实现）

#### parse_text_content()

**功能**: 解析文本内容,提取否决项标记

**检测的否决项关键词**:

- `veto_14`: 未告知 + 陈述
- `veto_15`: 听证 + 未举行/未告知
- `veto_20`: 超期
- `veto_1`: 超越职权/无权

## 4 依赖关系

### 4.1 Python后端依赖

**文件位置**: `requirements.txt`

#### 核心框架

| 依赖包 | 版本 | 说明 |
|--------|------|------|
| fastapi | 0.104.1 | 高性能异步API框架 |
| uvicorn | 0.24.0 | ASGI服务器 |
| pydantic | 2.5.0 | 数据验证和模型定义 |
| pydantic-settings | 2.1.0 | Pydantic设置管理 |

#### 数据处理

| 依赖包 | 版本 | 说明 |
|--------|------|------|
| PyYAML | 6.0.1 | YAML文件解析 |
| python-multipart | 0.0.6 | 文件上传支持 |
| python-dotenv | 1.0.0 | 环境变量管理 |

#### AI模型集成

| 依赖包 | 版本 | 说明 |
|--------|------|------|
| openai | 1.3.7 | OpenAI API客户端 |
| anthropic | 0.7.8 | Anthropic API客户端 |
| httpx | 0.25.2 | HTTP客户端 |

#### 文档处理

| 依赖包 | 版本 | 说明 |
|--------|------|------|
| PyPDF2 | 3.0.1 | PDF文件处理 |
| PyMuPDF | 1.24.1 | PDF解析增强 |
| pytesseract | 0.3.10 | OCR文字识别 |
| Pillow | 10.2.0 | 图像处理 |
| pdf2image | 1.17.0 | PDF转图片 |
| python-docx | 1.1.0 | Word文档处理 |
| docxtpl | 0.16.4 | Word模板引擎 |
| weasyprint | 60.1 | HTML转PDF |

#### 任务队列

| 依赖包 | 版本 | 说明 |
|--------|------|------|
| redis | 5.0.1 | Redis客户端 |
| celery | 5.3.4 | 分布式任务队列 |

#### 测试

| 依赖包 | 版本 | 说明 |
|--------|------|------|
| pytest | 7.4.3 | 单元测试框架 |
| pytest-asyncio | 0.21.1 | 异步测试支持 |
| pytest-cov | 4.1.0 | 测试覆盖率 |

#### 其他工具

| 依赖包 | 版本 | 说明 |
|--------|------|------|
| jinja2 | 3.1.2 | 模板引擎 |
| aiofiles | 23.2.1 | 异步文件操作 |
| loguru | 0.7.2 | 日志库 |
| python-dateutil | 2.8.2 | 日期工具 |

### 4.2 前端依赖

**文件位置**: `frontend/package.json`

#### 核心框架

| 依赖包 | 版本 | 说明 |
|--------|------|------|
| vue | 3.4.21 | 前端框架 |
| vue-router | 4.3.0 | 路由管理 |
| pinia | 2.1.7 | 状态管理 |

#### UI组件

| 依赖包 | 版本 | 说明 |
|--------|------|------|
| element-plus | 2.6.1 | Vue 3 UI组件库 |
| @vueuse/core | 10.9.0 | Vue组合式API工具集 |

#### 工具库

| 依赖包 | 版本 | 说明 |
|--------|------|------|
| axios | 1.6.8 | HTTP客户端 |
| markdown-it | 14.1.0 | Markdown解析 |
| highlight.js | 11.9.0 | 代码高亮 |
| chart.js | 4.4.2 | 图表库 |
| vue-chartjs | 5.3.1 | Vue图表封装 |

#### 构建工具

| 依赖包 | 版本 | 说明 |
|--------|------|------|
| vite | 5.2.10 | 构建工具 |
| vue-tsc | 2.0.11 | TypeScript类型检查 |
| typescript | 5.4.5 | TypeScript编译器 |
| tailwindcss | 3.4.3 | CSS框架 |
| autoprefixer | 10.4.19 | CSS前缀处理 |
| postcss | 8.4.38 | CSS处理 |
| eslint | 8.57.0 | 代码检查 |
| @vitejs/plugin-vue | 5.0.4 | Vue插件 |

### 4.3 模块依赖关系图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户交互层                               │
│         ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│         │ CLI (main.py)│  │API(routes) │  │ Web (Vue)   │       │
│         └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │
└────────────────┼───────────────┼───────────────┼───────────────┘
                 │               │               │
                 ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                       引擎层                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  ScoringEngine                             │ │
│  │  - calculate_normative_score()                              │ │
│  │  - calculate_comprehensive_score()                          │ │
│  │  - determine_grade()                                        │ │
│  │  - determine_pass()                                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  VetoChecker                                │ │
│  │  - check_veto()                                             │ │
│  │  - _check_single_item()                                    │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       模型层                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  schemas.py (Pydantic)                       │ │
│  │  - CaseReviewRequest / CaseReviewResult                    │ │
│  │  - CaseType / VetoCategory / ReviewGrade                    │ │
│  │  - LegalityReview / NormativeReview / DiscretionReview     │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       配置层                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  settings.py                                │ │
│  │  - HERMES模型配置                                           │ │
│  │  - 文件路径配置                                             │ │
│  │  - 评分阈值配置                                             │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 5 项目运行方式

### 5.1 环境准备

#### Python环境要求

- Python版本: 3.8+
- 推荐使用虚拟环境

#### 安装依赖

```bash
# 进入项目目录
cd hermes-case-review

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
```

### 5.2 配置环境变量

创建`.env`文件:

```env
# 应用配置
APP_NAME=生态环境案卷评查系统
APP_VERSION=1.0.0
DEBUG=False

# HERMES模型配置
HERMES_MODEL_PROVIDER=deepseek
HERMES_MODEL_NAME=deepseek-chat
HERMES_API_KEY=your_api_key_here
HERMES_API_BASE=

# 文件路径配置
UPLOAD_DIR=./uploads
REPORT_DIR=./reports
TEMPLATE_DIR=./config/templates
STANDARDS_DIR=./config/standards

# API配置
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

### 5.3 运行后端服务

#### 方式一: CLI命令行

```bash
# 评查案卷
python -m src.main review test_data/test_case_001.json --verbose

# 查看合法性标准
python -m src.main legality-check

# 查看评分标准
python -m src.main standards

# 计算等级
python -m src.main calculate-grade 85

# 显示配置
python -m src.main config
```

#### 方式二: API服务

```bash
# 启动API服务
python -m src.api.routes

# 或使用uvicorn
uvicorn src.api.routes:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后:

- API地址: http://localhost:8000
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

### 5.4 运行前端服务

```bash
cd frontend

# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

### 5.5 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_engine.py -v

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html
```

### 5.6 Docker部署

#### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY templates/ ./templates/
COPY .env.example .env

CMD ["python", "-m", "src.api.routes"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
      - ./reports:/app/reports
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  redis:
    image: redis:latest
    ports:
      - "6379:6379"

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - app
```

## 6 HERMES技能配置

### 6.1 技能文件位置

```
src/skills/
├── legality_review.yaml          # 合法性评查技能
├── normative_scoring.yaml        # 规范性评分技能
└── comprehensive_analysis.yaml   # 综合分析技能
```

### 6.2 安装HERMES技能

```bash
# 复制技能文件到HERMES技能目录
cp src/skills/*.yaml ~/.hermes/skills/

# 验证技能已加载
hermes skills list
```

### 6.3 使用HERMES进行评查

```bash
# 使用合法性评查技能
hermes -s legality_review --input case_file=./case.pdf

# 使用规范性评分技能
hermes -s normative_scoring --input case_file=./case.pdf

# 使用完整评查工作流
hermes -s full_case_review --input case_file=./case.pdf
```

## 7 评分公式详解

### 7.1 规范性评分公式

```
规范性得分 = 50 × (文书得分 / 标准分) - 基本要素扣分
```

**示例计算**:

- 文书得分: 85
- 标准分: 100
- 基本要素扣分: 3

计算过程:

```
规范性得分 = 50 × (85 / 100) - 3
           = 50 × 0.85 - 3
           = 42.5 - 3
           = 39.5
```

### 7.2 综合得分公式

```
综合得分 = 合法性得分 + 规范性得分
```

**示例计算**:

- 合法性得分: 50（未触发否决）
- 规范性得分: 39.5

计算过程:

```
综合得分 = 50 + 39.5 = 89.5
```

### 7.3 等级判定规则

| 综合得分范围 | 评查等级 | 是否通过 |
|-------------|---------|---------|
| ≥90分 | 优秀 | 通过 |
| 80-89分 | 良好 | 通过 |
| 60-79分 | 合格 | 通过 |
| <60分 | 不合格 | 不通过 |

**特别说明**: 触发一票否决时,无论综合得分多少,直接判定为不合格。

## 8 扩展开发指南

### 8.1 添加新的否决条件

在`VetoChecker.VETO_ITEMS`字典中添加新的否决项:

```python
26: {
    'category': VetoCategory.ENFORCEMENT_PROCEDURE,
    'name': '新否决项名称',
    'description': '新否决项描述'
}
```

### 8.2 添加新的案件类型

在`schemas.py`的`CaseType`枚举中添加:

```python
NEW_TYPE = "新型案件类型"
```

### 8.3 自定义评分规则

继承`ScoringEngine`类并重写相关方法:

```python
class CustomScoringEngine(ScoringEngine):
    def calculate_normative_score(self, document_score, document_standard, basic_deduction):
        # 自定义评分逻辑
        return super().calculate_normative_score(document_score, document_standard, basic_deduction)
```

### 8.4 添加新的API端点

在`src/api/routes.py`中添加新的路由:

```python
@app.get("/api/v1/custom")
async def custom_endpoint():
    return {"message": "自定义端点"}
```

## 9 最佳实践

### 9.1 代码规范

- 使用类型注解提高代码可读性
- Pydantic模型用于API请求和响应
- 遵循PEP 8代码风格
- 编写单元测试覆盖核心逻辑

### 9.2 性能优化

- 使用异步API处理并发请求
- 文件上传使用流式处理
- 合理使用缓存减少重复计算
- 异步任务使用Celery处理

### 9.3 安全建议

- 敏感配置使用环境变量
- API添加认证和授权
- 文件上传进行格式验证
- 定期更新依赖包版本

### 9.4 日志记录

使用Loguru进行日志记录:

```python
from loguru import logger

logger.info("评查开始")
logger.error("评查失败: {error}", error=str(e))
```

## 10 附录

### 10.1 文件格式支持

| 格式 | 读取 | 写入 | 说明 |
|------|------|------|------|
| JSON | ✓ | ✓ | 推荐使用 |
| TXT | ✓ | ✓ | 简单文本 |
| PDF | ✓ | ✗ | 需要OCR |
| DOCX | ✗ | ✓ | 报告生成 |
| YAML | ✓ | ✓ | 配置文件 |

### 10.2 错误代码

| 错误码 | 说明 | 解决方案 |
|--------|------|---------|
| 1001 | 文件解析失败 | 检查文件格式 |
| 1002 | 不支持的文件格式 | 使用JSON/TXT格式 |
| 2001 | 模型API调用失败 | 检查API配置 |
| 2002 | 模型响应超时 | 增加超时时间 |
| 3001 | 数据库连接失败 | 检查Redis配置 |
| 4001 | 文件存储失败 | 检查目录权限 |

### 10.3 联系方式

- 项目文档: README.md
- 技术方案: HERMES_案卷评查系统_技术方案.md
- 快速开始: GETTING_STARTED.md
- HERMES官方: https://hermes.xaapi.ai/
