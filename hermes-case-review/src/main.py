"""
生态环境案卷评查系统 - CLI 入口
"""
import click
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from src.engine.scoring_engine import scoring_engine, veto_checker
from src.models.schemas import CaseReviewResult, CaseType, ReviewGrade
from src.config.settings import settings


@click.group()
@click.version_option(version=settings.APP_VERSION)
def cli():
    """生态环境案卷评查系统 CLI"""
    pass


@cli.command()
@click.argument('case_file', type=click.Path(exists=True))
@click.option('--type', '-t', 'case_type', default='一般行政处罚',
              type=click.Choice(['一般行政处罚', '不予行政处罚', '按日连续处罚', 
                               '查封扣押', '移送拘留', '移送涉嫌环境污染犯罪']),
              help='案件类型')
@click.option('--output', '-o', 'output_file', type=click.Path(), 
              help='输出文件路径（JSON格式）')
@click.option('--verbose', '-v', is_flag=True, help='详细输出')
def review(case_file: str, case_type: str, output_file: Optional[str], verbose: bool):
    """
    对案卷进行完整评查
    
    CASE_FILE: 案卷文件路径（支持 PDF、TXT、JSON 格式）
    """
    click.echo(f"🔍 正在评查案卷: {case_file}")
    click.echo(f"📋 案件类型: {case_type}")
    
    try:
        # 解析案卷文件
        case_data = parse_case_file(case_file, verbose)
        
        # 检查否决条件
        has_veto, veto_items, veto_details = veto_checker.check_veto(case_data)
        legality_score = 0 if has_veto else 50
        
        if verbose:
            click.echo(f"\n📊 合法性评查:")
            click.echo(f"   是否触发否决: {'是 ❌' if has_veto else '否 ✅'}")
            if veto_items:
                click.echo(f"   否决项: {', '.join(map(str, veto_items))}")
        
        # 计算规范性得分
        document_score = case_data.get('document_score', 85)
        document_standard = case_data.get('document_standard', 100)
        basic_deduction = case_data.get('basic_deduction', 3)
        
        normative_score = scoring_engine.calculate_normative_score(
            document_score, document_standard, basic_deduction
        )
        
        if verbose:
            click.echo(f"\n📊 规范性评分:")
            click.echo(f"   文书得分: {document_score}/{document_standard}")
            click.echo(f"   基本要素扣分: {basic_deduction}")
            click.echo(f"   规范性得分: {normative_score:.2f}")
        
        # 计算综合得分
        comprehensive_score = scoring_engine.calculate_comprehensive_score(
            legality_score, normative_score
        )
        
        # 确定等级
        grade = scoring_engine.determine_grade(comprehensive_score)
        is_pass = scoring_engine.determine_pass(legality_score, comprehensive_score)
        
        # 显示结果
        click.echo(f"\n{'='*50}")
        click.echo(f"📊 评查结果")
        click.echo(f"{'='*50}")
        click.echo(f"   合法性评分: {legality_score} 分")
        click.echo(f"   规范性评分: {normative_score:.2f} 分")
        click.echo(f"   综合得分: {comprehensive_score:.2f} 分")
        click.echo(f"   评查等级: {grade.value}")
        click.echo(f"   是否通过: {'通过 ✅' if is_pass else '不通过 ❌'}")
        click.echo(f"{'='*50}\n")
        
        # 构建结果
        result = {
            'case_file': case_file,
            'case_type': case_type,
            'legality_score': legality_score,
            'has_veto': has_veto,
            'veto_items': veto_items,
            'normative_score': normative_score,
            'comprehensive_score': comprehensive_score,
            'grade': grade.value,
            'is_pass': is_pass,
            'review_time': datetime.now().isoformat()
        }
        
        # 保存结果
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            click.echo(f"💾 结果已保存至: {output_file}")
        
        # 返回退出码
        sys.exit(0 if is_pass else 1)
        
    except Exception as e:
        click.echo(f"❌ 错误: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
def legality_check():
    """检查合法性否决条件"""
    click.echo("📋 25项合法性否决条件:")
    
    for item_num, item_info in veto_checker.VETO_ITEMS.items():
        category = item_info['category'].value
        name = item_info['name']
        desc = item_info['description']
        
        click.echo(f"\n{item_num}. [{category}] {name}")
        click.echo(f"   {desc}")


@cli.command()
def standards():
    """显示评分标准"""
    click.echo("📊 规范性评分标准:")
    click.echo("\n卷面基本要素（20分，扣分制）:")
    click.echo("  - 文书基本要素: 10分")
    click.echo("  - 笔录基本要素: 10分")
    
    click.echo("\n文书评分（100分→折算50分，得分制）:")
    documents = [
        ("立案审批表", 2),
        ("现场检查笔录", 10),
        ("调查询问笔录", 10),
        ("监测报告", 5),
        ("其他证据", 8),
        ("案件调查报告", 8),
        ("责令改正决定书", 10),
        ("行政处罚事先告知书", 10),
        ("听证通知书", 4),
        ("听证笔录", 8),
        ("行政处罚决定书", 15),
        ("催告书", 2),
        ("强制执行申请书", 5),
        ("结案审批表", 3),
    ]
    
    for doc_name, score in documents:
        click.echo(f"  - {doc_name}: {score}分")


@cli.command()
@click.argument('score', type=float)
def calculate_grade(score: float):
    """计算等级"""
    grade = scoring_engine.determine_grade(score)
    click.echo(f"得分 {score} 分 → 等级: {grade.value}")


@cli.command()
def config():
    """显示当前配置"""
    click.echo(f"应用名称: {settings.APP_NAME}")
    click.echo(f"版本: {settings.APP_VERSION}")
    click.echo(f"模型提供商: {settings.HERMES_MODEL_PROVIDER}")
    click.echo(f"模型名称: {settings.HERMES_MODEL_NAME}")


def parse_case_file(case_file: str, verbose: bool = False) -> dict:
    """
    解析案卷文件
    
    Args:
        case_file: 文件路径
        verbose: 是否详细输出
        
    Returns:
        案卷数据字典
    """
    file_path = Path(case_file)
    suffix = file_path.suffix.lower()
    
    if suffix == '.json':
        # JSON 格式
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    elif suffix == '.txt':
        # TXT 格式 - 简单解析
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return parse_text_content(content)
    
    elif suffix == '.pdf':
        # PDF 格式 - 需要 OCR
        click.echo("⚠️ PDF 文件需要 OCR 解析（暂未实现）")
        click.echo("请使用 JSON 或 TXT 格式，或提供 OCR 服务")
        raise NotImplementedError("PDF 解析暂未实现")
    
    else:
        raise ValueError(f"不支持的文件格式: {suffix}")


def parse_text_content(content: str) -> dict:
    """
    解析文本内容
    
    Args:
        content: 文本内容
        
    Returns:
        案卷数据字典
    """
    # 简单实现 - 实际需要更复杂的解析逻辑
    case_data = {
        'document_score': 85,
        'document_standard': 100,
        'basic_deduction': 3,
    }
    
    # 检查是否有否决项标记
    lines = content.split('\n')
    for line in lines:
        line_lower = line.lower()
        
        # 检查是否包含否决项关键词
        if '未告知' in line and '陈述' in line:
            case_data['veto_14'] = True
        if '听证' in line and ('未举行' in line or '未告知' in line):
            case_data['veto_15'] = True
        if '超期' in line:
            case_data['veto_20'] = True
        if '超越职权' in line or '无权' in line:
            case_data['veto_1'] = True
    
    return case_data


def main():
    """主入口"""
    cli()


if __name__ == '__main__':
    main()
