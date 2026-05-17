#!/usr/bin/env python3
"""
批量下载WPS知识库中的案卷文件
"""
import json
import subprocess
import base64
import os
import time
from pathlib import Path

# 设置环境变量
os.environ['X_KWIKI_AUTH'] = 'qs37gZbUgpcFdtQ/N8IkwkWRw+nTNSI6WCcDedJamm0G2Yybxo1heYeHbREFfqINGof3yAvwEObqrnl80ycabuPbzYDAjSc4jBossSAZxxQKRimmDz1gJEf8TgsX5v/jIMAibBliNmiOm2HV'

# 案卷文件列表
CASES = [
    {"kuid": "0lcm1gFC5DzDz9", "name": "鑫顺建材案卷评查报告.pdf"},
    {"kuid": "0lchy0GnyChOaw", "name": "明恒案卷评查报告.pdf"},
    {"kuid": "0lciTGcAB9vsLl", "name": "2025-39永兴县鑫润新材料评查报告.pdf"},
    {"kuid": "0lcbIT7eddYZOG", "name": "2025-49建新村页岩砖厂评查报告.pdf"},
    {"kuid": "0lcok0AuidTTHV", "name": "赢湖矿产品评查报告.pdf"},
    {"kuid": "0lca2mIpA5VWQY", "name": "湖南省煤业集团金竹山矿业案卷评查报告.pdf"},
    {"kuid": "0lcqwiu8SbIDmL", "name": "冷水江市禾青镇建新村页岩砖厂案卷评查报告.pdf"},
]

OUTPUT_DIR = Path("/workspace/hermes-case-review/case_study/案卷")

def download_case(case_info, retry=3):
    """下载单个案卷文件"""
    kuid = case_info["kuid"]
    name = case_info["name"]
    output_path = OUTPUT_DIR / name
    
    for attempt in range(retry):
        try:
            print(f"📥 正在下载: {name} (尝试 {attempt+1}/{retry})")
            
            # 执行mcporter下载
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
                env=os.environ.copy(),
                timeout=60  # 60秒超时
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data.get('code') == 0:
                    file_content = data.get('data', {}).get('file_base64')
                    if file_content:
                        # 解码并保存
                        with open(output_path, 'wb') as f:
                            f.write(base64.b64decode(file_content))
                        
                        size = output_path.stat().st_size / 1024
                        print(f"✅ 成功: {name} ({size:.1f}KB)")
                        return True
            
            if attempt < retry - 1:
                print(f"⚠️ 尝试 {attempt+1} 失败，5秒后重试...")
                time.sleep(5)
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            if attempt < retry - 1:
                time.sleep(5)
    
    print(f"❌ 下载失败: {name}")
    return False

def main():
    print("="*70)
    print("📥 批量下载案卷文件")
    print("="*70)
    
    # 确保目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    fail_count = 0
    
    for case in CASES:
        if download_case(case):
            success_count += 1
        else:
            fail_count += 1
        time.sleep(1)  # 避免请求过快
    
    print("\n" + "="*70)
    print(f"📊 下载结果: 成功 {success_count}/{len(CASES)}, 失败 {fail_count}/{len(CASES)}")
    print("="*70)
    
    # 列出已下载的文件
    if success_count > 0:
        print("\n📂 已下载的文件:")
        for f in OUTPUT_DIR.glob("*.pdf"):
            size = f.stat().st_size / 1024
            print(f"   📄 {f.name} ({size:.1f}KB)")
    
    return success_count > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
