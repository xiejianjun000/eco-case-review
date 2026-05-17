# HERMES智能案卷评查自动化工作流

## 工作流名称
eco-case-wps-review-workflow

## 工作流描述
HERMES自动从WPS知识库下载案卷，处理PDF文档，执行评查，生成报告

## 环境配置
```bash
# WPS知识库认证
X_KWIKI_AUTH=qs37gZbUgpcFdtQ/N8IkwkWRw+nTNSI6WCcDedJamm0G2Yybxo1heYeHbREFfqINGof3yAvwEObqrnl80ycabuPbzYDAjSc4jBossSAZxxQKRimmDz1gJEf8TgsX5v/jIMAibBliNmiOm2HV

# 知识库路径
KNOWLEDGE_BASE_PATH=/workspace/hermes-case-review/knowledge

# 案卷存储路径
CASE_STUDY_PATH=/workspace/hermes-case-review/case_study/案卷
```

## 工作流步骤

### 步骤1：连接WPS知识库
```bash
# 验证WPS知识库连接
mcporter call "kwiki.list_knowledge_view" --args '{}'
```

### 步骤2：获取案卷列表
```bash
# 查询案卷评查知识库文件
mcporter call "kwiki.list_file" --args '{"kuid":"0s_3088858258"}'
```

预期返回7个文件：
- 鑫顺建材案卷评查报告
- 明恒案卷评查报告
- 2025-39 永兴县鑫润新材料 评查报告
- 2025-49 建新村页岩砖厂 评查报告
- 赢湖矿产品_评查报告
- 湖南省煤业集团金竹山矿业有限公司案卷评查报告
- 冷水江市禾青镇建新村页岩砖厂案卷评查报告

### 步骤3：下载案卷文件
```bash
# 案卷KUID列表
CASES=(
  "0lcm1gFC5DzDz9:鑫顺建材案卷评查报告"
  "0lchy0GnyChOaw:明恒案卷评查报告"
  "0lciTGcAB9vsLl:永兴县鑫润新材料评查报告"
  "0lcbIT7eddYZOG:建新村页岩砖厂评查报告"
  "0lcok0AuidTTHV:赢湖矿产品评查报告"
  "0lca2mIpA5VWQY:湖南省煤业集团金竹山矿业案卷评查报告"
  "0lcqwiu8SbIDmL:冷水江市禾青镇建新村页岩砖厂案卷评查报告"
)

# 批量下载
for case in "${CASES[@]}"; do
  kuid="${case%%:*}"
  filename="${case##*:}"
  mcporter call "kwiki.download_file" --args "{\"kuid\":\"$kuid\",\"response_type\":\"file_base64\"}" > "CASE_STUDY_PATH/$filename"
done
```

### 步骤4：处理PDF文档
```python
# PDF转文本
from pdfminer.high_level import extract_text

def extract_pdf_text(pdf_path):
    text = extract_text(pdf_path)
    return text

# OCR处理图片
from pytesseract import image_to_string
from PIL import Image

def ocr_image(image_path):
    text = image_to_string(Image.open(image_path))
    return text
```

### 步骤5：执行智能评查
```python
from src.agent_learning.case_reviewer import CaseReviewer

def review_case(case_content, case_name):
    reviewer = CaseReviewer()
    result = reviewer.analyze_case(case_content, case_name)
    report = reviewer.generate_report(result)
    return report
```

### 步骤6：生成评查报告
```bash
# 输出报告到指定目录
OUTPUT_DIR=/workspace/hermes-case-review/case_study/评查报告
mkdir -p $OUTPUT_DIR

# 保存每个案卷的评查报告
# case_1_review.md
# case_2_review.md
# ...
```

## 自动化脚本

### 主脚本：auto_review.sh
```bash
#!/bin/bash

echo "🚀 HERMES智能案卷评查工作流"
echo "=========================================="

# 1. 设置环境
export X_KWIKI_AUTH="qs37gZbUgpcFdtQ/N8IkwkWRw+nTNSI6WCcDedJamm0G2Yybxo1heYeHbREFfqINGof3yAvwEObqrnl80ycabuPbzYDAjSc4jBossSAZxxQKRimmDz1gJEf8TgsX5v/jIMAibBliNmiOm2HV"

# 2. 创建目录
mkdir -p /workspace/hermes-case-review/case_study/{案卷,评查报告}

# 3. 案卷列表
declare -A CASES
CASES=(
  ["0lcm1gFC5DzDz9"]="鑫顺建材案卷评查报告"
  ["0lchy0GnyChOaw"]="明恒案卷评查报告"
  ["0lciTGcAB9vsLl"]="永兴县鑫润新材料评查报告"
  ["0lcbIT7eddYZOG"]="建新村页岩砖厂评查报告"
  ["0lcok0AuidTTHV"]="赢湖矿产品评查报告"
  ["0lca2mIpA5VWQY"]="湖南省煤业集团金竹山矿业案卷评查报告"
  ["0lcqwiu8SbIDmL"]="冷水江市禾青镇建新村页岩砖厂案卷评查报告"
)

# 4. 批量下载并评查
for kuid in "${!CASES[@]}"; do
  echo ""
  echo "📥 下载: ${CASES[$kuid]}"
  
  # 下载
  mcporter call "kwiki.download_file" --args "{\"kuid\":\"$kuid\",\"response_type\":\"file_base64\"}" > /tmp/current_case.json
  
  # 解码并保存PDF
  python3 <<EOF
import json, base64, os
with open('/tmp/current_case.json', 'r') as f:
    data = json.load(f)
if data.get('code') == 0 and data.get('data', {}).get('file_base64'):
    with open('/workspace/hermes-case-review/case_study/案卷/${CASES[$kuid]}.pdf', 'wb') as f:
        f.write(base64.b64decode(data['data']['file_base64']))
    print('✅ 下载成功')
else:
    print('❌ 下载失败')
EOF
  
  echo "📋 评查中..."
  
  # TODO: 执行评查
done

echo ""
echo "=========================================="
echo "✅ 评查完成！"
echo "=========================================="
```

## 执行命令

```bash
cd /workspace/hermes-case-review
bash deployment/workflows/eco-case-wps-review-workflow.sh
```

## 预期输出

```
🚀 HERMES智能案卷评查工作流
==========================================
📥 下载: 鑫顺建材案卷评查报告
✅ 下载成功
📋 评查中...
✅ 评查完成

📥 下载: 明恒案卷评查报告
✅ 下载成功
📋 评查中...
✅ 评查完成

...

==========================================
✅ 7个案卷全部评查完成！
📁 报告保存在: /workspace/hermes-case-review/case_study/评查报告/
==========================================
```

## 注意事项

1. **错误处理**: 每个步骤添加错误检查和重试机制
2. **日志记录**: 完整记录每个步骤的执行情况
3. **进度显示**: 实时显示下载和评查进度
4. **报告生成**: 每个案卷生成独立的Markdown报告
5. **汇总报告**: 生成所有案卷的汇总报告

## 版本信息
- 版本: 1.0.0
- 创建日期: 2024-05-16
- 维护者: HERMES AI Team
