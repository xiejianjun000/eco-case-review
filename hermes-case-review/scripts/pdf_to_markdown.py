#!/usr/bin/env python3
"""
PDF转Markdown转换器
"""
import os
import sys
from pathlib import Path
from pdfminer.high_level import extract_text
from markdownify import markdownify as md
import re


def clean_markdown(text):
    """清理Markdown文本"""
    # 移除多余空白
    text = re.sub(r'\n{3,}', '\n\n', text)
    # 规范化空格
    text = re.sub(r'[ \t]+', ' ', text)
    # 移除特殊字符
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    return text.strip()


def pdf_to_markdown(pdf_path, output_path):
    """将PDF转换为Markdown"""
    try:
        print(f"📄 正在转换: {pdf_path.name}")
        
        # 提取PDF文本
        text = extract_text(str(pdf_path))
        
        # 转换为Markdown
        markdown = md(text)
        
        # 清理文本
        markdown = clean_markdown(markdown)
        
        # 保存Markdown文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        size = os.path.getsize(output_path) / 1024
        print(f"✅ 转换完成: {output_path.name} ({size:.1f}KB)")
        return True
        
    except Exception as e:
        print(f"❌ 转换失败: {pdf_path.name} - {str(e)}")
        return False


def main():
    """主函数"""
    knowledge_dir = Path("/workspace/hermes-case-review/knowledge")
    
    # 定义转换任务
    conversions = [
        ("评查细则/生态环境行政执法案卷评查细则（2024年版）.pdf", 
         "评查细则/生态环境行政执法案卷评查细则（2024年版）.md"),
        ("法律法规/生态环境保护法律法规汇编（2026.5）.pdf", 
         "法律法规/生态环境保护法律法规汇编（2026.5）.md"),
        ("复函汇编/生态环境部复函汇编（2026.3）.pdf", 
         "复函汇编/生态环境部复函汇编（2026.3）.md"),
        ("部长信箱/生态环境部部长信箱回复汇编（2026.1）.pdf", 
         "部长信箱/生态环境部部长信箱回复汇编（2026.1）.md"),
        ("湖南省资料/湖南省生态环境保护行政处罚裁量权基准规定（2021版）.pdf", 
         "湖南省资料/湖南省生态环境保护行政处罚裁量权基准规定（2021版）.md"),
        ("湖南省资料/湖南省生态环境行政处罚相关文书范本（2024年版）.pdf", 
         "湖南省资料/湖南省生态环境行政处罚相关文书范本（2024年版）.md"),
    ]
    
    print("="*70)
    print("📚 PDF转Markdown批量转换工具")
    print("="*70)
    
    success_count = 0
    total_count = len(conversions)
    
    for pdf_rel, md_rel in conversions:
        pdf_path = knowledge_dir / pdf_rel
        md_path = knowledge_dir / md_rel
        
        if pdf_path.exists():
            if pdf_to_markdown(pdf_path, md_path):
                success_count += 1
        else:
            print(f"⚠️ 文件不存在: {pdf_path}")
    
    print("\n" + "="*70)
    print(f"📊 转换结果: {success_count}/{total_count} 成功")
    print("="*70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
