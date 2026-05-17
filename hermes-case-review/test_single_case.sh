#!/bin/bash
# HERMES自动下载并评查第一份案卷

echo "🚀🚀🚀 HERMES案卷评查测试 🚀🚀🚀"
echo "=========================================="

# 设置认证
export X_KWIKI_AUTH="qs37gZbUgpcFdtQ/N8IkwkWRw+nTNSI6WCcDedJamm0G2Yybxo1heYeHbREFfqINGof3yAvwEObqrnl80ycabuPbzYDAjSc4jBossSAZxxQKRimmDz1gJEf8TgsX5v/jIMAibBliNmiOm2HV"

# 创建目录
mkdir -p /workspace/hermes-case-review/case_study/案卷
mkdir -p /workspace/hermes-case-review/case_study/评查报告

# 案卷1信息
KUID="0lcm1gFC5DzDz9"
FILENAME="鑫顺建材案卷评查报告"
PDF_PATH="/workspace/hermes-case-review/case_study/案卷/${FILENAME}.pdf"
TXT_PATH="/workspace/hermes-case-review/case_study/案卷/${FILENAME}.txt"
REPORT_PATH="/workspace/hermes-case-review/case_study/评查报告/${FILENAME}_评查报告.md"

echo "📥 案卷: $FILENAME"
echo "📥 KUID: $KUID"
echo ""

# 步骤1: 下载
echo "🔽 步骤1: 下载PDF文件..."
mcporter call "kwiki.download_file" --args "{\"kuid\":\"$KUID\",\"response_type\":\"file_base64\"}" > /tmp/case1_download.json 2>&1

# 检查结果
if grep -q '"code":0' /tmp/case1_download.json; then
    echo "✅ 下载成功"
    
    # 步骤2: 解码保存
    echo "🔄 步骤2: 处理PDF文件..."
    python3 <<'PYEOF'
import json, base64, os

try:
    with open('/tmp/case1_download.json', 'r') as f:
        data = json.load(f)
    
    if data.get('code') == 0 and data.get('data', {}).get('file_base64'):
        pdf_content = data['data']['file_base64']
        
        # 保存PDF
        with open('/workspace/hermes-case-review/case_study/案卷/鑫顺建材案卷评查报告.pdf', 'wb') as f:
            f.write(base64.b64decode(pdf_content))
        print('✅ PDF保存成功')
        
        # 提取文本
        try:
            from pdfminer.high_level import extract_text
            text = extract_text('/workspace/hermes-case-review/case_study/案卷/鑫顺建材案卷评查报告.pdf')
            
            # 保存文本
            with open('/workspace/hermes-case-review/case_study/案卷/鑫顺建材案卷评查报告.txt', 'w', encoding='utf-8') as f:
                f.write(text)
            print(f'✅ 文本提取成功 ({len(text)}字符)')
            
            # 评查
            print('⚖️ 执行智能评查...')
            import sys
            sys.path.insert(0, '/workspace/hermes-case-review')
            from src.agent_learning.case_reviewer import CaseReviewer
            
            reviewer = CaseReviewer()
            result = reviewer.analyze_case(text, '鑫顺建材案卷评查报告')
            report = reviewer.generate_report(result)
            
            # 保存报告
            with open('/workspace/hermes-case-review/case_study/评查报告/鑫顺建材案卷评查报告_评查报告.md', 'w', encoding='utf-8') as f:
                f.write(report)
            
            print('✅ 评查完成!')
            print(f'📊 综合评分: {result["comprehensive_score"]:.1f}分')
            print(f'📋 评定等级: {result["conclusion"]["grade"]}')
            
        except ImportError:
            print('⚠️ PDF处理模块未安装，跳过评查')
            
    else:
        print('❌ 下载失败')
        
except Exception as e:
    print(f'❌ 处理失败: {e}')
PYEOF
    
else
    echo "❌ 下载失败: 业务异常"
fi

echo ""
echo "=========================================="
echo "✅ 测试完成"
echo "=========================================="

# 显示结果
echo ""
echo "📁 生成的文件:"
ls -lh /workspace/hermes-case-review/case_study/案卷/
ls -lh /workspace/hermes-case-review/case_study/评查报告/
