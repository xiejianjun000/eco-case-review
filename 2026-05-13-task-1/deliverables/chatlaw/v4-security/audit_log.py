"""
V4 行政处罚案卷评查系统 - 审计日志模块
"""

import structlog
import json
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

# 配置structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class AuditEvent(Enum):
    """审计事件枚举"""
    REVIEW_START = "REVIEW_START"           # 开始评查
    REVIEW_COMPLETE = "REVIEW_COMPLETE"     # 评查完成
    VETO_TRIGGERED = "VETO_TRIGGERED"       # 触发否决
    REPORT_EXPORTED = "REPORT_EXPORTED"     # 报告导出
    USER_LOGIN = "USER_LOGIN"               # 用户登录
    USER_LOGOUT = "USER_LOGOUT"             # 用户登出
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"  # 未授权访问
    DATA_EXPORTED = "DATA_EXPORTED"          # 数据导出

# 事件描述映射
EVENT_DESCRIPTIONS = {
    AuditEvent.REVIEW_START: "开始评查",
    AuditEvent.REVIEW_COMPLETE: "评查完成",
    AuditEvent.VETO_TRIGGERED: "触发否决",
    AuditEvent.REPORT_EXPORTED: "报告导出",
    AuditEvent.USER_LOGIN: "用户登录",
    AuditEvent.USER_LOGOUT: "用户登出",
    AuditEvent.UNAUTHORIZED_ACCESS: "未授权访问",
    AuditEvent.DATA_EXPORTED: "数据导出"
}

# 事件级别
EVENT_LEVELS = {
    AuditEvent.REVIEW_START: "info",
    AuditEvent.REVIEW_COMPLETE: "info",
    AuditEvent.VETO_TRIGGERED: "warning",
    AuditEvent.REPORT_EXPORTED: "info",
    AuditEvent.USER_LOGIN: "info",
    AuditEvent.USER_LOGOUT: "info",
    AuditEvent.UNAUTHORIZED_ACCESS: "critical",
    AuditEvent.DATA_EXPORTED: "info"
}

def audit(
    event: AuditEvent,
    user: Optional[str] = None,
    case_id: Optional[str] = None,
    **kwargs: Any
) -> None:
    """
    记录审计日志
    
    Args:
        event: 审计事件
        user: 用户名
        case_id: 案卷ID
        **kwargs: 其他参数
    """
    log_data = {
        "audit_event": event.value,
        "description": EVENT_DESCRIPTIONS.get(event, event.value),
        "level": EVENT_LEVELS.get(event, "info"),
        "user": user,
        "case_id": case_id,
        "timestamp": datetime.utcnow().isoformat(),
        **kwargs
    }
    
    level = EVENT_LEVELS.get(event, "info")
    getattr(logger, level)("audit", **log_data)

def audit_review_start(user: str, case_id: str, case_name: str) -> None:
    """记录评查开始"""
    audit(AuditEvent.REVIEW_START, user=user, case_id=case_id, case_name=case_name)

def audit_review_complete(
    user: str,
    case_id: str,
    score: float,
    grade: str,
    veto_triggered: bool = False
) -> None:
    """记录评查完成"""
    audit(
        AuditEvent.REVIEW_COMPLETE,
        user=user,
        case_id=case_id,
        score=score,
        grade=grade,
        veto_triggered=veto_triggered
    )

def audit_veto_triggered(
    user: str,
    case_id: str,
    veto_item: int,
    veto_reason: str
) -> None:
    """记录触发否决"""
    audit(
        AuditEvent.VETO_TRIGGERED,
        user=user,
        case_id=case_id,
        veto_item=veto_item,
        veto_reason=veto_reason
    )

def audit_unauthorized(
    user: Optional[str],
    resource: str,
    action: str,
    ip_address: Optional[str] = None
) -> None:
    """记录未授权访问"""
    audit(
        AuditEvent.UNAUTHORIZED_ACCESS,
        user=user,
        resource=resource,
        action=action,
        ip_address=ip_address
    )
