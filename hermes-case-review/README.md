# 生态环境案卷评查系统

基于 HERMES Agent 框架的智能案卷评查系统，支持合法性评查、规范性评分、裁量基准计算等功能。

## 功能特性

- 🔍 **合法性评查**：25项一票否决检查
- 📊 **规范性评分**：卷面要素+文书质量评分
- ⚖️ **裁量基准**：罚款金额计算验证
- 📋 **证据链分析**：证据三性分析
- 🤖 **智能报告**：自动生成评查报告
- 🌐 **多平台支持**：CLI / API / 飞书 / 钉钉

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入 API Key
```

### 3. 使用 CLI

```bash
# 评查案卷
python -m src.main review ./case.json

# 查看合法性标准
python -m src.main legality-check

# 查看评分标准
python -m src.main standards

# 计算等级
python -m src.main calculate-grade 85
```

### 4. 启动 API

```bash
python -m src.api.routes
# 访问 http://localhost:8000/docs 查看 API 文档
```

## API 接口

### POST /api/v1/review

评查案卷

```json
{
  "case_id": "case_001",
  "case_data": {
    "document_score": 85,
    "document_standard": 100,
    "basic_deduction": 3
  },
  "case_type": "一般行政处罚"
}
```

响应：

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

### GET /api/v1/standards/legality

获取合法性评查标准

### GET /api/v1/standards/normative

获取规范性评分标准

## 评分公式

### 规范性评分

```
规范性得分 = 50 × (文书得分 / 标准分) - 基本要素扣分
```

### 综合得分

```
综合得分 = 合法性得分 + 规范性得分
```

### 等级判定

- 优秀：≥90分
- 良好：80-89分
- 合格：60-79分
- 不合格：<60分

## 项目结构

```
hermes-case-review/
├── src/
│   ├── main.py              # CLI 入口
│   ├── api/routes.py        # API 服务
│   ├── engine/              # 评分引擎
│   │   └── scoring_engine.py
│   ├── models/              # 数据模型
│   │   └── schemas.py
│   ├── skills/              # HERMES 技能
│   │   ├── legality_review.yaml
│   │   └── normative_scoring.yaml
│   └── config/             # 配置
│       └── settings.py
├── tests/                   # 测试用例
├── config/                  # 配置文件
│   └── templates/           # 报告模板
└── requirements.txt
```

## HERMES 技能

### 安装技能

```bash
cp src/skills/*.yaml ~/.hermes/skills/
```

### 使用技能

```bash
hermes -s legality_review --input case_file=./case.pdf
```

## 开发指南

### 运行测试

```bash
pytest tests/ -v
```

### 代码格式

```bash
black src/
flake8 src/
```

## 文档

- [技术方案](../HERMES_案卷评查系统_技术方案.md)
- [快速开始](../QUICKSTART.md)
- [HERMES 官方文档](https://hermes.xaapi.ai/)

## 许可证

MIT License

## 版本

v1.0.0
