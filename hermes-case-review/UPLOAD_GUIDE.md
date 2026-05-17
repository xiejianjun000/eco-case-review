# HERMES 案卷评查系统 - 资料上传指南

## 📁 资料上传位置

系统已配置以下目录用于存放资料：

| 目录名称 | 路径 | 用途 |
|---------|------|------|
| `uploads` | `./uploads/` | 用户上传的案卷文件 |
| `reports` | `./reports/` | 生成的评查报告 |
| `standards` | `./config/standards/` | 评查标准文件 |
| `knowledge` | `./knowledge/` | 知识库文件（法律法规等） |

---

## 📤 如何上传资料

### 方式一：前端界面上传（推荐）

#### 1. 上传案卷文件
```
路径：案卷管理 → 点击"上传案卷"按钮
支持格式：PDF、TXT、JSON
```

#### 2. 上传参考资料（知识库）
```
路径：知识库 → 上传文档
支持格式：PDF、TXT、MD
```

#### 3. 审查时上传
```
路径：审查交流页面 → 点击📎图标上传
支持在对话中分享参考资料给智能体
```

---

### 方式二：直接上传到目录

将文件直接复制到对应目录：

#### 上传案卷文件
```bash
# 将案卷PDF复制到上传目录
cp /path/to/your/case.pdf ./uploads/

# 或使用JSON格式
cp /path/to/case.json ./uploads/
```

#### 上传知识库文件
```bash
# 创建知识库目录
mkdir -p ./knowledge

# 上传法律法规文件
cp /path/to/laws.pdf ./knowledge/
cp /path/to/regulations.pdf ./knowledge/

# 上传评查标准
cp /path/to/review_standards.pdf ./config/standards/
```

---

### 方式三：API上传

```bash
# 上传案卷文件
curl -X POST "http://localhost:8000/api/v1/review/upload" \
  -F "file=@case.pdf" \
  -F "case_type=一般行政处罚"

# 上传JSON格式
curl -X POST "http://localhost:8000/api/v1/review/upload" \
  -F "file=@case.json" \
  -F "case_type=一般行政处罚"
```

---

## 📋 推荐上传的资料类型

### 1. 评查标准文件
- 生态环境行政处罚案卷评查细则
- 行政处罚案卷评查办法
- 各省市裁量基准文件

### 2. 法律法规文件
- 《行政处罚法》及释义
- 《环境保护法》
- 各污染防治单行法
- 生态环境部规章

### 3. 典型案例文件
- 各省市优秀案卷示例
- 典型案例汇编
- 问题案卷示例

### 4. 裁量基准文件
- 水污染防治法裁量基准
- 大气污染防治法裁量基准
- 固废法裁量基准
- 噪声污染防治法裁量基准

---

## 📂 建议的目录结构

```
hermes-case-review/
├── uploads/                      # 用户上传的案卷
│   ├── cases/
│   ├── reports/
│   └── temp/
├── knowledge/                    # 知识库
│   ├── laws/                    # 法律法规
│   │   ├── 行政处罚法.pdf
│   │   ├── 环境保护法.pdf
│   │   └── 水污染防治法.pdf
│   ├── standards/               # 评查标准
│   │   ├── 案卷评查细则.pdf
│   │   └── 裁量基准.pdf
│   └── cases/                   # 典型案例
│       ├── 优秀案例/
│       └── 问题案例/
└── config/
    └── standards/               # 配置文件
```

---

## ⚠️ 注意事项

1. **文件格式**
   - 推荐使用：PDF、TXT、JSON、MD
   - 系统会自动解析内容

2. **文件大小**
   - 建议单个文件不超过50MB
   - 大文件建议分批上传

3. **命名规范**
   - 建议使用有意义的文件名
   - 格式：`YYYYMMDD_案件类型_简要描述.pdf`

4. **安全建议**
   - 上传前检查文件安全性
   - 敏感信息建议脱敏处理

---

## 🔧 创建目录结构

如果您想要创建标准的目录结构，可以运行：

```bash
# 创建目录结构
mkdir -p uploads/{cases,reports,temp}
mkdir -p knowledge/{laws,standards,cases}
mkdir -p config/standards
mkdir -p reports/{pdf,html,json}

# 设置权限
chmod -R 755 uploads knowledge reports
```

---

**如需进一步帮助，请参考项目文档或联系技术支持。**
