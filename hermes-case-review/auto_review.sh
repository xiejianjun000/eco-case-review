#!/bin/bash
# HERMES智能案卷评查自动化脚本
# 让HERMES系统自动从WPS知识库下载案卷并执行评查

set -e  # 遇到错误立即退出

echo "🚀🚀🚀 HERMES智能案卷评查系统 🚀🚀🚀"
echo "=========================================="
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

# 设置WPS知识库认证
export X_KWIKI_AUTH="qs37gZbUgpcFdtQ/N8IkwkWRw+nTNSI6WCcDedJamm0G2Yybxo1heYeHbREFfqINGof3yAvwEObqrnl80ycabuPbzYDAjSc4jBossSAZxxQKRimmDz1gJEf8TgsX5v/jIMAibBliNmiOm2HV"

# 创建工作目录
WORK_DIR="/workspace/hermes-case-review/case_study"
REPORT_DIR="$WORK_DIR/评查报告"
mkdir -p "$WORK_DIR/案卷" "$REPORT_DIR"

echo "📁 工作目录: $WORK_DIR"
echo "📋 报告目录: $REPORT_DIR"
echo ""

# 案卷列表 (KUID: 文件名)
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

total=${#CASES[@]}
current=0
success=0
failed=0

echo "📋 待处理案卷数量: $total"
echo ""

# 遍历所有案卷
for kuid in "${!CASES[@]}"; do
  ((current++))
  filename="${CASES[$kuid]}"
  
  echo "┌─────────────────────────────────────────────"
  echo "│ [$current/$total] 处理: $filename"
  echo "└─────────────────────────────────────────────"
  
  # 步骤1: 下载
  echo "  📥 步骤1: 下载PDF文件..."
  temp_file="/tmp/hermes_case_${current}.json"
  
  # 使用mcporter下载
  mcporter call "kwiki.download_file" --args "{\"kuid\":\"$kuid\",\"response_type\":\"file_base64\"}" > "$temp_file" 2>&1
  
  # 检查下载结果
  if grep -q '"code":0' "$temp_file"; then
    echo "  ✅ 下载完成"
    
    # 步骤2: 解码并保存
    echo "  📄 步骤2: 处理PDF文件..."
    
    python3 <<PYEOF
import json
import base64
import os

try:
    with open('$temp_file', 'r') as f:
        data = json.load(f)
    
    if data.get('code') == 0 and data.get('data', {}).get('file_base64'):
        pdf_content = data['data']['file_base64']
        pdf_path = '$WORK_DIR/案卷/${filename}.pdf'
        
        with open(pdf_path, 'wb') as f:
            f.write(base64.b64decode(pdf_content))
        
        size = os.path.getsize(pdf_path) / 1024
        print(f'  ✅ PDF保存成功 ({size:.1f}KB)')
        
        # 步骤3: 提取文本
        print('  🔍 步骤3: 提取文本内容...')
        
        try:
            from pdfminer.high_level import extract_text
            text = extract_text(pdf_path)
            
            # 保存文本
            txt_path = '$WORK_DIR/案卷/${filename}.txt'
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            print(f'  ✅ 文本提取成功 ({len(text)}字符)')
            
            # 步骤4: 执行评查
            print('  ⚖️ 步骤4: 执行智能评查...')
            
            # 导入评查系统
            import sys
            sys.path.insert(0, '/workspace/hermes-case-review')
            from src.agent_learning.case_reviewer import CaseReviewer
            
            reviewer = CaseReviewer()
            result = reviewer.analyze_case(text, '$filename')
            report = reviewer.generate_report(result)
            
            # 保存报告
            report_path = '$REPORT_DIR/${filename}_评查报告.md'
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f'  ✅ 评查完成！')
            print(f'  📊 评分: {result[\"comprehensive_score\"]:.1f}分 ({result[\"conclusion\"][\"grade\"]})')
            print(f'  📁 报告: {report_path}')
            
            # 清理临时文件
            os.remove('$temp_file')
            
        except Exception as e:
            print(f'  ⚠️ 文本处理: {str(e)}')
            
    else:
        print(f'  ❌ 下载失败')
        
except Exception as e:
    print(f'  ❌ 处理失败: {str(e)}')
PYEOF
    
  else
    echo "  ❌ 下载失败: 业务异常"
    ((failed++))
  fi
  
  echo ""
done

# 生成汇总报告
echo "=========================================="
echo "📊 评查汇总"
echo "=========================================="
echo "总案卷数: $total"
echo "成功: $success"
echo "失败: $failed"
echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo "✅ HERMES智能评查系统运行完成！"
echo "=========================================="

# 列出生成的报告
echo ""
echo "📁 生成的评查报告:"
ls -lh "$REPORT_DIR"/*.md 2>/dev/null || echo "暂无报告"

exit 0
