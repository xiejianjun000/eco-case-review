from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """系统配置"""
    
    # 应用信息
    APP_NAME: str = "生态环境案卷评查系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # HERMES 配置
    HERMES_MODEL_PROVIDER: str = "deepseek"  # deepseek/openai/anthropic
    HERMES_MODEL_NAME: str = "deepseek-chat"
    HERMES_API_KEY: Optional[str] = None
    HERMES_API_BASE: Optional[str] = None
    
    # 文件配置
    UPLOAD_DIR: str = "./uploads"
    REPORT_DIR: str = "./reports"
    TEMPLATE_DIR: str = "./config/templates"
    STANDARDS_DIR: str = "./config/standards"
    
    # 评分配置
    LEGALITY_SCORE_PASS: int = 50
    LEGALITY_SCORE_FAIL: int = 0
    NORMATIVE_MAX_SCORE: int = 50
    COMPREHENSIVE_MAX_SCORE: int = 100
    
    # 等级阈值
    GRADE_EXCELLENT: float = 90.0
    GRADE_GOOD: float = 80.0
    GRADE_QUALIFIED: float = 60.0
    
    # API配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).parent.parent


def ensure_directories():
    """确保必要的目录存在"""
    dirs = [
        settings.UPLOAD_DIR,
        settings.REPORT_DIR,
        settings.LOG_FILE.rsplit('/', 1)[0] if '/' in settings.LOG_FILE else './logs',
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
