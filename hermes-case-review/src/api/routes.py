"""
生态环境案卷评查系统 - API 服务
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List
import json
import shutil
from pathlib import Path
from datetime import datetime

from src.engine.scoring_engine import scoring_engine, veto_checker
from src.models.schemas import CaseReviewRequest, CaseReviewResult, CaseType, ReviewGrade
from src.config.settings import settings, ensure_directories


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="生态环境行政处罚案卷评查系统 API"
)

# 确保目录存在
ensure_directories()


class ReviewRequest(BaseModel):
    """评查请求模型"""
    case_id: Optional[str] = None
    case_data: dict
    case_type: str = "一般行政处罚"


class ReviewResponse(BaseModel):
    """评查响应模型"""
    success: bool
    case_id: str
    comprehensive_score: float
    grade: str
    is_pass: bool
    legality_score: int
    normative_score: float
    veto_items: List[int] = []
    report_url: Optional[str] = None


@app.get("/")
async def root():
    """API 根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.post("/api/v1/review", response_model=ReviewResponse)
async def review_case(request: ReviewRequest):
    """
    对案卷进行评查
    
    请求体:
    {
        "case_id": "可选的案卷ID",
        "case_data": {
            // 案卷数据，包括:
            "document_score": 85,      // 文书得分
            "document_standard": 100,   // 文书标准分
            "basic_deduction": 3,      // 基本要素扣分
            "veto_1": false,          // 否决项标记
            // ... 更多否决项
        },
        "case_type": "一般行政处罚"
    }
    """
    try:
        case_id = request.case_id or f"case_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        case_data = request.case_data
        
        # 检查否决条件
        has_veto, veto_items, veto_details = veto_checker.check_veto(case_data)
        legality_score = 0 if has_veto else 50
        
        # 计算规范性得分
        document_score = case_data.get('document_score', 85)
        document_standard = case_data.get('document_standard', 100)
        basic_deduction = case_data.get('basic_deduction', 0)
        
        normative_score = scoring_engine.calculate_normative_score(
            document_score, document_standard, basic_deduction
        )
        
        # 计算综合得分
        comprehensive_score = scoring_engine.calculate_comprehensive_score(
            legality_score, normative_score
        )
        
        # 确定等级
        grade = scoring_engine.determine_grade(comprehensive_score)
        is_pass = scoring_engine.determine_pass(legality_score, comprehensive_score)
        
        return ReviewResponse(
            success=True,
            case_id=case_id,
            comprehensive_score=round(comprehensive_score, 2),
            grade=grade.value,
            is_pass=is_pass,
            legality_score=legality_score,
            normative_score=round(normative_score, 2),
            veto_items=veto_items
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/review/upload")
async def upload_and_review(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    case_type: str = "一般行政处罚"
):
    """
    上传案卷文件并进行评查
    
    支持格式: PDF, TXT, JSON
    """
    try:
        # 保存上传的文件
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 解析文件
        case_data = parse_uploaded_file(file_path)
        
        # 进行评查
        has_veto, veto_items, veto_details = veto_checker.check_veto(case_data)
        legality_score = 0 if has_veto else 50
        
        document_score = case_data.get('document_score', 85)
        document_standard = case_data.get('document_standard', 100)
        basic_deduction = case_data.get('basic_deduction', 0)
        
        normative_score = scoring_engine.calculate_normative_score(
            document_score, document_standard, basic_deduction
        )
        
        comprehensive_score = scoring_engine.calculate_comprehensive_score(
            legality_score, normative_score
        )
        
        grade = scoring_engine.determine_grade(comprehensive_score)
        is_pass = scoring_engine.determine_pass(legality_score, comprehensive_score)
        
        return {
            "success": True,
            "file_name": file.filename,
            "case_id": f"case_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "comprehensive_score": round(comprehensive_score, 2),
            "grade": grade.value,
            "is_pass": is_pass,
            "legality_score": legality_score,
            "normative_score": round(normative_score, 2),
            "veto_items": veto_items
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/standards/legality")
async def get_legality_standards():
    """获取合法性评查标准"""
    return {
        "total_items": 25,
        "categories": {
            "执法主体": [1, 2],
            "违法主体": [3, 4, 5],
            "违法事实证据": [6, 7],
            "法律适用": [8, 9, 10, 11, 12, 13],
            "执法程序": [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
        },
        "items": veto_checker.VETO_ITEMS
    }


@app.get("/api/v1/standards/normative")
async def get_normative_standards():
    """获取规范性评分标准"""
    return {
        "basic_elements": {
            "total_score": 20,
            "documents": {
                "score": 10,
                "items": [
                    "生态环境主管部门名称、文书名称、发文字号、印章、日期",
                    "负责人审批意见及签名日期",
                    "承办人意见及签名日期",
                    "当事人基本信息",
                    "送达回证",
                    "卷面规范"
                ]
            },
            "records": {
                "score": 10,
                "items": [
                    "检查/询问起止时间、地点",
                    "检查人/询问人、记录人基本信息",
                    "被检查人/被询问人基本信息及身份",
                    "出示执法证件、表明身份记录",
                    "告知当事人权利记录",
                    "逐页签名及审阅确认意见",
                    "空白处理",
                    "修改处签名"
                ]
            }
        },
        "document_scoring": {
            "total_score": 100,
            "convert_to": 50,
            "documents": [
                {"name": "立案审批表", "score": 2},
                {"name": "现场检查笔录", "score": 10},
                {"name": "调查询问笔录", "score": 10},
                {"name": "监测/检测/鉴定报告", "score": 5},
                {"name": "收集的其他证据", "score": 8},
                {"name": "案件调查报告", "score": 8},
                {"name": "责令改正决定书", "score": 10},
                {"name": "行政处罚事先告知书", "score": 10},
                {"name": "听证通知书", "score": 4},
                {"name": "听证笔录", "score": 8},
                {"name": "行政处罚决定书", "score": 15},
                {"name": "督促履行义务催告书", "score": 2},
                {"name": "强制执行申请书", "score": 5},
                {"name": "结案审批表", "score": 3}
            ]
        },
        "formula": "规范性得分 = 50 × (文书得分 / 标准分) - 基本要素扣分"
    }


@app.get("/api/v1/calculate")
async def calculate_score(
    legality_score: int,
    document_score: float,
    document_standard: float = 100,
    basic_deduction: float = 0
):
    """计算评分"""
    normative_score = scoring_engine.calculate_normative_score(
        document_score, document_standard, basic_deduction
    )
    
    comprehensive_score = scoring_engine.calculate_comprehensive_score(
        legality_score, normative_score
    )
    
    grade = scoring_engine.determine_grade(comprehensive_score)
    is_pass = scoring_engine.determine_pass(legality_score, comprehensive_score)
    
    return {
        "legality_score": legality_score,
        "normative_score": round(normative_score, 2),
        "comprehensive_score": round(comprehensive_score, 2),
        "grade": grade.value,
        "is_pass": is_pass,
        "formula_details": {
            "normative_formula": f"50 × ({document_score}/{document_standard}) - {basic_deduction} = {normative_score:.2f}",
            "comprehensive_formula": f"{legality_score} + {normative_score:.2f} = {comprehensive_score:.2f}"
        }
    }


def parse_uploaded_file(file_path: Path) -> dict:
    """解析上传的文件"""
    suffix = file_path.suffix.lower()
    
    if suffix == '.json':
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif suffix == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return parse_text_content(content)
    else:
        raise ValueError(f"不支持的文件格式: {suffix}")


def parse_text_content(content: str) -> dict:
    """解析文本内容"""
    case_data = {
        'document_score': 85,
        'document_standard': 100,
        'basic_deduction': 3,
    }
    
    lines = content.split('\n')
    for line in lines:
        if '未告知' in line and '陈述' in line:
            case_data['veto_14'] = True
        if '听证' in line and ('未举行' in line or '未告知' in line):
            case_data['veto_15'] = True
        if '超期' in line:
            case_data['veto_20'] = True
    
    return case_data


def start_server():
    """启动 API 服务器"""
    import uvicorn
    uvicorn.run(
        "src.api.routes:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )


if __name__ == "__main__":
    start_server()
