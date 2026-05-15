import structlog
from datetime import datetime

logger = structlog.get_logger()

AUDIT_EVENTS = {
    "REVIEW_START": "开始评查",
    "REVIEW_COMPLETE": "评查完成",
    "VETO_TRIGGERED": "触发否决",
    "UNAUTHORIZED_ACCESS": "未授权访问"
}

def audit(event: str, user: str = None, case_id: str = None, **kwargs):
    logger.info(
        "audit_event",
        event=event,
        description=AUDIT_EVENTS.get(event, event),
        user=user,
        case_id=case_id,
        timestamp=datetime.utcnow().isoformat(),
        **kwargs
    )
