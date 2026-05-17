#!/usr/bin/env python3
"""
从WPS知识库下载文件到本地知识库目录
"""
import json
import subprocess
import base64
import os
from pathlib import Path

# 知识库文件信息
FILES_TO_DOWNLOAD = [
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

def run_mcporter_call(tool_name, args):
    """执行mcporter调用"""
    cmd = [
        "mcporter", "call", f"kwiki.{tool_name}",
        "--args", json.dumps(args)
    ]
    
    env = os.environ.copy()
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env
    )
    
    if result.returncode != 0:
        print(f"❌ 命令执行失败: {result.stderr}")
        return None
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"❌ JSON解析失败: {result.stdout[:200]}")
        return None

def download_file(kuid, filename, category):
    """下载单个文件"""
    print(f"\n📥 下载: {filename}")
    print(f"   分类: {category}")
    print(f"   KUID: {kuid}")
    
    # 获取下载链接
    response = run_mcporter_call("download_file", {
        "kuid": kuid,
        "response_type": "download_link"
    })
    
    if not response or response.get("code") != 0:
        print(f"   ⚠️ 获取下载链接失败，尝试base64方式")
        
        # 尝试base64方式
        response = run_mcporter_call("download_file", {
            "kuid": kuid,
            "response_type": "file_base64"
        })
        
        if response and response.get("code") == 0:
            file_data = response.get("data", {}).get("file_base64")
            if file_data:
                # 解码并保存
                target_path = BASE_DIR / category / filename
                with open(target_path, "wb") as f:
                    f.write(base64.b64decode(file_data))
                print(f"   ✅ 下载完成: {target_path}")
                return True
    
    download_url = response.get("data", {}).get("download_url") if response else None
    if download_url:
        print(f"   📎 下载链接: {download_url[:50]}...")
        print(f"   💡 链接方式需要浏览器认证，请手动下载")
    
    return False

def main():
    """主函数"""
    print("=" * 70)
    print("🚀 WPS知识库文件下载工具")
    print("=" * 70)
    
    # 确保目录存在
    for category in ["评查细则", "法律法规", "复函汇编", "部长信箱"]:
        (BASE_DIR / category).mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 目标目录: {BASE_DIR}")
    print(f"📦 待下载文件: {len(FILES_TO_DOWNLOAD)}个")
    
    success_count = 0
    fail_count = 0
    
    for file_info in FILES_TO_DOWNLOAD:
        if download_file(
            file_info["kuid"],
            file_info["filename"],
            file_info["category"]
        ):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 70)
    print("📊 下载结果汇总")
    print("=" * 70)
    print(f"   ✅ 成功: {success_count}")
    print(f"   ❌ 失败: {fail_count}")
    print(f"   📁 目录: {BASE_DIR}")
    
    # 列出已下载的文件
    print("\n📂 目录结构:")
    for category in ["评查细则", "法律法规", "复函汇编", "部长信箱"]:
        category_path = BASE_DIR / category
        files = list(category_path.glob("*"))
        if files:
            print(f"   📁 {category}/")
            for f in files:
                size = f.stat().st_size / (1024 * 1024)
                print(f"      📄 {f.name} ({size:.2f}MB)")
        else:
            print(f"   📁 {category}/ (空)")
    
    print("=" * 70)
    
    if fail_count > 0:
        print("\n💡 提示: 部分文件下载失败，需要浏览器认证")
        print("   请访问以下链接手动下载:")
        print("   https://www.kdocs.cn/wiki/l/canh6YdbT2rK")
    
    return 0

if __name__ == "__main__":
    exit(main())
