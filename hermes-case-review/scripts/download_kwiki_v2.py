#!/usr/bin/env python3
"""
使用正确认证方式从WPS知识库下载文件
"""
import json
import subprocess
import base64
import os
import sys
import time

from pathlib import Path
from typing import Dict, List, Optional
import json
import subprocess
import base64
import os
import sys
import time

# 设置环境变量
os.environ['X_KWIKI_AUTH'] = 'qs37gZbUgpcFdtQ/N8IkwkWRw+nTNSI6WCcDedJamm0G2Yybxo1heYeHbREFfqINGof3yAvwEObqrnl80ycabuPbzYDAjSc4jBossSAZxxQKRimmDz1gJEf8TgsX5v/jIMAibBliNmiOm2HV'

BASE_DIR = Path("/workspace/hermes-case-review/knowledge")

# 知识库文件信息
FILES_TO_DOWNLOAD: List[Dict[str, str]] = [
    {
        "kuid": "0lcanh6YdbT2rK",
        "filename": "生态环境行政执法案卷评查细则（2024年版）.pdf",
        "category": "评查细则"
    },
    {
        "kuid": "0lcilV7Cn4Ovdw",
        "filename": "生态环境保护法律法规汇编（2026.5）.pdf",
        "category": "法律法规"
    },
    {
        "kuid": "0lcoVqctezlpK4",
        "filename": "生态环境部复函汇编（2026.3）.pdf",
        "category": "复函汇编"
    },
    {
        "kuid": "0lcn0h9Q1pbWn0",
        "filename": "生态环境部部长信箱回复汇编（2026.1）.pdf",
        "category": "部长信箱"
    }
]

BASE_DIR = Path("/workspace/hermes-case-review/knowledge")

def download_file_with_retry(kuid, filename, category, max_retries=3):
    """下载文件，带重试"""
    
    target_path = BASE_DIR / category / filename
    
    for attempt in range(max_retries):
        try:
            # 使用mcporter获取文件内容
            result = subprocess.run(
                [
                    'mcporter', 'call', 'kwiki.download_file',
                    '--args', json.dumps({
                        'kuid': kuid,
                        'response_type': 'file_base64'
                    })
                ],
                capture_output=True,
                text=True,
                env={**os.environ}
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data.get('code') == 0:
                    file_content = data.get('data', {}).get('file_base64')
                    if file_content:
                        with open(target_path, 'wb') as f:
                            f.write(base64.b64decode(file_content))
                        
                        size = target_path.stat().st_size / (1024 * 1024)
                        print(f"✅ 成功: {filename} ({size:.2f}MB)")
                        return True
                    else:
                        print(f"⚠️ 尝试 {attempt+1}/{max_retries}: 无文件内容")
                else:
                    print(f"⚠️ 尝试 {attempt+1}/{max_retries}: {data.get('msg', '未知错误')}")
            else:
                print(f"⚠️ 尝试 {attempt+1}/{max_retries}: {result.stderr[:100]}")
                
            if attempt < max_retries - 1:
                time.sleep(1)
                
        except Exception as e:
            print(f"⚠️ 尝试 {attempt+1}/{max_retries}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(1)
    
    return False

def main():
    print("=" * 70)
    print("🚀 WPS知识库文件下载工具 (带重试)")
    print("=" * 70)
    
    # 确保目录存在
    for category in ["评查细则", "法律法规", "复函汇编", "部长信箱"]:
        (BASE_DIR / category).mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 目标目录: {BASE_DIR}")
    print(f"📦 待下载文件: {len(FILES_TO_DOWNLOAD)}个\n")
    
    success_count = 0
    fail_count = 0
    
    for file_info in FILES_TO_DOWNLOAD:
        print(f"\n📥 正在下载: {file_info['filename']}")
        if download_file_with_retry(
            file_info["kuid"],
            file_info["filename"],
            file_info["category"]
        ):
            success_count += 1
        else:
            fail_count += 1
            print(f"❌ 下载失败: {file_info['filename']}")
    
    print("\n" + "=" * 70)
    print("📊 下载结果汇总")
    print("=" * 70)
    print(f"   ✅ 成功: {success_count}/{len(FILES_TO_DOWNLOAD)}")
    print(f"   ❌ 失败: {fail_count}/{len(FILES_TO_DOWNLOAD)}")
    
    # 列出已下载的文件
    print("\n📂 目录结构:")
    for category in ["评查细则", "法律法规", "复函汇编", "部长信箱"]:
        category_path = BASE_DIR / category
        files = list(category_path.glob("*.pdf"))
        if files:
            print(f"   📁 {category}/")
            for f in files:
                size = f.stat().st_size / (1024 * 1024)
                print(f"      📄 {f.name} ({size:.2f}MB)")
        else:
            print(f"   📁 {category}/ (空)")
    
    print("=" * 70)
    return 0

if __name__ == "__main__":
    sys.exit(main())
