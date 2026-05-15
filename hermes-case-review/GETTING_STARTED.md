# HERMES 案卷评查系统 - 快速开始指南

## 🎯 版本信息

- **系统版本**: v1.0.0
- **开发日期**: 2026-05-15
- **基于框架**: HERMES Agent
- **技术栈**: Python 3.8+ / FastAPI / Pydantic

---

## 📦 已创建的文件

### 核心代码

| 文件路径 | 描述 |
|---------|------|
| `src/main.py` | CLI 命令行入口 |
| `src/api/routes.py` | FastAPI REST 接口 |
| `src/engine/scoring_engine.py` | 核心评分引擎 |
| `src/models/schemas.py` | Pydantic 数据模型 |
| `src/config/settings.py` | 配置管理 |

### HERMES 技能

| 文件路径 | 描述 |
|---------|------|
| `src/skills/legality_review.yaml` | 合法性评查技能 |
| `src/skills/normative_scoring.yaml` | 规范性评分技能 |
| `src/skills/comprehensive_analysis.yaml` | 综合分析技能 |

### 配置和测试

| 文件路径 | 描述 |
|---------|------|
| `requirements.txt` | Python 依赖列表 |
| `README.md` | 项目文档 |
| `setup.bat` | Windows 快速部署脚本 |
| `tests/test_engine.py` | 单元测试 |
| `test_data/test_case_001.json` | 测试数据 |

---

## 🚀 快速开始（5分钟）

### 步骤 1：安装 Python

如果还没有安装 Python，请从 https://python.org 下载并安装 Python 3.8 或更高版本。

安装时**务必勾选** "Add Python to PATH"。

### 步骤 2：安装依赖

打开命令提示符（CMD）或 PowerShell，执行：

```bash
cd "c:\Users\Administrator\Desktop\案卷评查\hermes-case-review"

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

或者直接运行自动部署脚本：

```bash
cd "c:\Users\Administrator\Desktop\案卷评查\hermes-case-review"
setup.bat
```

### 步骤 3：配置环境变量

复制环境变量模板：

```bash
copy .env.example .env
```

编辑 `.env` 文件，填入您的 API Key：

```env
# DeepSeek（推荐，性价比高）
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 或者使用 OpenAI
OPENAI_API_KEY=your_openai_api_key_here
```

### 步骤 4：运行测试

```bash
pytest tests/test_engine.py -v
```

### 步骤 5：开始使用！

#### 使用 CLI 评查案卷

```bash
python -m src.main review test_data/test_case_001.json
```

输出示例：

```
🔍 正在评查案卷: test_data/test_case_001.json
📋 案件类型: 一般行政处罚

==================================================
📊 评查结果
==================================================
   合法性评分: 50 分
   规范性评分: 39.50 分
   综合得分: 89.50 分
   评查等级: 良好
   是否通过: 通过 ✅
==================================================
```

#### 启动 API 服务

```bash
python -m src.api.routes
```

然后访问 http://localhost:8000/docs 查看 API 文档。

---

## 📚 使用场景

### 场景 1：使用 CLI

```bash
# 查看合法性标准
python -m src.main legality-check

# 查看评分标准
python -m src.main standards

# 计算等级
python -m src.main calculate-grade 85
```

### 场景 2：调用 API

#### 方式 1：使用 curl

```bash
curl -X POST "http://localhost:8000/api/v1/review" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "test_001",
    "case_data": {
      "document_score": 85,
      "document_standard": 100,
      "basic_deduction": 3
    }
  }'
```

#### 方式 2：使用 Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/review",
    json={
        "case_id": "test_001",
        "case_data": {
            "document_score": 85,
            "document_standard": 100,
            "basic_deduction": 3
        }
    }
)

print(response.json())
```

### 场景 3：集成到 HERMES

```bash
# 复制技能文件
cp src/skills/*.yaml ~/.hermes/skills/

# 使用技能
hermes -s legality_review --input case_file=./case.pdf
```

---

## 🔧 配置选项

在 `.env` 文件中可以配置以下选项：

```env
# 应用配置
APP_NAME=生态环境案卷评查系统
APP_VERSION=1.0.0
DEBUG=False

# 模型配置
HERMES_MODEL_PROVIDER=deepseek
HERMES_MODEL_NAME=deepseek-chat
HERMES_API_KEY=your_api_key_here

# API 配置
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 📊 评分公式

### 规范性评分

```
规范性得分 = 50 × (文书得分 / 标准分) - 基本要素扣分
```

**示例**：
- 文书得分：85
- 标准分：100
- 基本要素扣分：3
- 规范性得分 = 50 × 0.85 - 3 = **39.5**

### 综合得分

```
综合得分 = 合法性得分 + 规范性得分
```

**示例**：
- 合法性得分：50
- 规范性得分：39.5
- 综合得分 = 50 + 39.5 = **89.5**

### 等级判定

| 综合得分 | 等级 |
|---------|------|
| ≥90 分 | 优秀 |
| 80-89 分 | 良好 |
| 60-79 分 | 合格 |
| <60 分 | 不合格 |

---

## 🐛 故障排除

### 问题 1：Python 未找到

**错误信息**：`'python' is not recognized as a name of a cmdlet`

**解决方案**：
1. 确保已安装 Python
2. 将 Python 添加到系统 PATH
3. 重启命令提示符

### 问题 2：模块导入错误

**错误信息**：`ModuleNotFoundError: No module named 'src'`

**解决方案**：
```bash
# 在项目根目录执行
export PYTHONPATH="${PYTHONPATH}:."
python -m src.main review case.json
```

### 问题 3：API 连接失败

**错误信息**：`Connection refused`

**解决方案**：
1. 确保 API 服务已启动
2. 检查端口是否被占用：`netstat -an | findstr 8000`
3. 尝试更换端口

---

## 📖 更多资源

- **项目文档**: [README.md](./README.md)
- **技术方案**: [HERMES_案卷评查系统_技术方案.md](../HERMES_案卷评查系统_技术方案.md)
- **快速开始**: [QUICKSTART.md](../QUICKSTART.md)
- **HERMES 官方文档**: https://hermes.xaapi.ai/

---

## ✅ 下一步

1. ✅ 安装依赖
2. ✅ 配置 API Key
3. ✅ 运行测试
4. ⏳ 开始评查您的案卷！

祝使用愉快！🎉

---

**技术支持**: 如有问题，请查阅上面的故障排除或联系开发团队。
