
# 快速开始：HERMES + 案卷评查系统

## 5分钟上手指南

---

## 步骤1：安装 HERMES Agent

```bash
# 克隆项目
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# 创建虚拟环境
python -m venv venv

# Windows 激活
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 验证安装
hermes doctor
```

---

## 步骤2：配置

```bash
# 运行初始化向导
hermes setup

# 选择模型（推荐：DeepSeek 或 GLM-4）
hermes model

# 配置 API Key
hermes config set DEEPSEEK_API_KEY your_key_here
# 或
hermes config set ZHIPUAI_API_KEY your_key_here
```

---

## 步骤3：安装案卷评查技能

```bash
# 进入项目目录
cd c:\Users\Administrator\Desktop\案卷评查

# 复制技能文件
cp hermes_skills/*.yaml ~/.hermes/skills/

# 验证技能
hermes skills list
```

---

## 步骤4：开始评查！

```bash
# 开始对话
hermes

# 或者直接使用技能
hermes -s full_case_review --input case_pdf=./your_case.pdf
```

在对话中说："帮我评查这份行政处罚案卷

---

## 步骤5：配置多平台（可选）

```bash
# 配置网关
hermes gateway setup

# 选择平台（飞书/钉钉/微信企业版/Telegram等）

# 启动网关
hermes gateway start --daemon
```

---

## 下一步

- 阅读完整技术方案：[HERMES_案卷评查系统_技术方案.md](./HERMES_案卷评查系统_技术方案.md)
- 查看 HERMES 官方文档：https://hermes.xaapi.ai/
- 运行原 V4 系统文档：[electric-beacon-einstein.md](./electric-beacon-einstein.md)

---

## 常见问题

### Q: 如何选择模型？

推荐使用：
- **DeepSeek-V3（国产，性价比高）
- **GLM-4（国产，政务友好）
- **GPT-4o（国际，能力强）

### Q: 数据安全吗？

HERMES 完全自托管，案卷数据不上云，符合政务数据安全要求。

### Q: 如何让系统会自己学习吗？

是的！每次评查完成后，HERMES 会自动沉淀专业技能，越用越准。

---

**祝使用愉快！
