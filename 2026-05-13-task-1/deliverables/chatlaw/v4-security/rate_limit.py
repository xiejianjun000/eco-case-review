# -*- coding: utf-8 -*-
"""
API限流配置模块
用于V4行政处罚案卷评查系统的API访问限流和熔断保护
"""

from typing import Callable, Optional, Dict, Any
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request, HTTPException, status
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# 全局限流器实例
limiter = Limiter(key_func=get_remote_address)

# 限流配置
RATE_LIMIT_CONFIG: Dict[str, Dict[str, Any]] = {
    "anonymous": {
        "limit": "20/minute",
        "description": "未认证用户限流",
    },
    "user": {
        "limit": "100/minute",
        "description": "普通用户限流",
    },
    "reviewer": {
        "limit": "500/minute",
        "description": "评查员限流",
    },
    "auditor": {
        "limit": "500/minute",
        "description": "审计员限流",
    },
    "admin": {
        "limit": "1000/minute",
        "description": "管理员限流",
    },
}

# 熔断配置
CIRCUIT_BREAKER_CONFIG: Dict[str, Any] = {
    "failure_threshold": 50,       # 失败次数阈值
    "recovery_timeout": 60,        # 恢复超时时间(秒)
    "half_open_max_calls": 3,       # 半开状态最大调用次数
    "expected_exception": "RateLimitExceeded",
}

# 每日请求限制
DAILY_LIMIT_CONFIG: Dict[str, int] = {
    "anonymous": 100,
    "user": 5000,
    "reviewer": 20000,
    "auditor": 10000,
    "admin": 100000,
}


class RateLimitManager:
    """限流管理器"""

    def __init__(self):
        self._user_limits: Dict[str, str] = {}

    def get_user_limit(self, user_role: str) -> str:
        """获取用户角色的限流配置"""
        config = RATE_LIMIT_CONFIG.get(user_role.lower(), RATE_LIMIT_CONFIG["user"])
        return config["limit"]

    def set_user_limit(self, user_id: str, limit: str) -> None:
        """设置用户自定义限流"""
        self._user_limits[user_id] = limit

    def check_rate_limit(self, user_id: Optional[str], user_role: str) -> str:
        """检查并返回适用的限流配置"""
        if user_id and user_id in self._user_limits:
            return self._user_limits[user_id]
        return self.get_user_limit(user_role)


# 全局限流管理器
rate_limit_manager = RateLimitManager()


def rate_limit(limit_string: str):
    """
    限流装饰器

    Usage:
        @rate_limit("100/minute")
        async def some_endpoint(request: Request):
            ...

        @rate_limit("10/second")
        async def another_endpoint(request: Request):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                request = kwargs.get("request")

            if request:
                return await limiter.limit(limit_string)(func)(request, *args, **kwargs)
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def user_rate_limit(user_role: str):
    """
    基于用户角色的限流装饰器

    Usage:
        @user_rate_limit("user")
        async def user_endpoint(request: Request):
            ...

        @user_rate_limit("admin")
        async def admin_endpoint(request: Request):
            ...
    """
    def decorator(func: Callable):
        limit_string = rate_limit_manager.get_user_limit(user_role)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                request = kwargs.get("request")

            if request:
                return await limiter.limit(limit_string)(func)(request, *args, **kwargs)
            return await func(*args, **kwargs)

        return wrapper
    return decorator


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    限流超限处理器

    返回友好的限流提示信息
    """
    logger.warning(f"Rate limit exceeded for {request.client.host}")

    return {
        "error": "rate_limit_exceeded",
        "message": "请求过于频繁，请稍后再试",
        "detail": str(exc.detail),
        "retry_after": exc.detail,
    }


class CircuitBreaker:
    """简单熔断器实现"""

    def __init__(
        self,
        failure_threshold: int = 50,
        recovery_timeout: int = 60,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half_open

    def record_success(self):
        """记录成功调用"""
        if self.state == "half_open":
            self.state = "closed"
            self.failure_count = 0
        elif self.failure_count > 0:
            self.failure_count -= 1

    def record_failure(self):
        """记录失败调用"""
        import time
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

    def can_execute(self) -> bool:
        """检查是否可以执行"""
        import time

        if self.state == "closed":
            return True

        if self.state == "open":
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed >= self.recovery_timeout:
                    self.state = "half_open"
                    logger.info("Circuit breaker entering half-open state")
                    return True
            return False

        # half_open state
        return True

    def get_state(self) -> Dict[str, Any]:
        """获取熔断器状态"""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
        }


# 全局熔断器
circuit_breaker = CircuitBreaker(
    failure_threshold=CIRCUIT_BREAKER_CONFIG["failure_threshold"],
    recovery_timeout=CIRCUIT_BREAKER_CONFIG["recovery_timeout"],
)


def circuit_breaker_protect():
    """
    熔断保护装饰器

    Usage:
        @circuit_breaker_protect()
        async def unreliable_service():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not circuit_breaker.can_execute():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="服务暂时不可用，请稍后再试"
                )

            try:
                result = await func(*args, **kwargs)
                circuit_breaker.record_success()
                return result
            except Exception as e:
                circuit_breaker.record_failure()
                raise

        return wrapper
    return decorator


# 预定义的限流端点装饰器
def create_rate_limited_endpoint(limit_string: str):
    """
    创建限流端点的工厂函数

    Usage:
        limited_endpoint = create_rate_limited_endpoint("100/minute")(endpoint_func)
    """
    return limiter.limit(limit_string)


# 常见限流装饰器快捷方式
def per_minute(limit: int):
    """每分钟限流装饰器"""
    return limiter.limit(f"{limit}/minute")


def per_second(limit: int):
    """每秒限流装饰器"""
    return limiter.limit(f"{limit}/second")


def per_hour(limit: int):
    """每小时限流装饰器"""
    return limiter.limit(f"{limit}/hour")


def per_day(limit: int):
    """每天限流装饰器"""
    return limiter.limit(f"{limit}/day")


# 限流中间件配置
MIDDLEWARE_SETTINGS = {
    "default_limits": ["100/minute"],
    "exempt_paths": [
        "/health",
        "/ready",
        "/metrics",
    ],
    "key_prefix": "v4_rate_limit",
}


if __name__ == "__main__":
    print("=== Rate Limit Configuration ===")
    for role, config in RATE_LIMIT_CONFIG.items():
        print(f"{role}: {config['limit']} - {config['description']}")

    print("\n=== Circuit Breaker Configuration ===")
    print(f"Failure threshold: {CIRCUIT_BREAKER_CONFIG['failure_threshold']}")
    print(f"Recovery timeout: {CIRCUIT_BREAKER_CONFIG['recovery_timeout']}s")

    print("\n=== Circuit Breaker Test ===")
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
    print(f"Initial state: {cb.get_state()}")

    cb.record_failure()
    print(f"After 1 failure: {cb.get_state()}")

    cb.record_failure()
    cb.record_failure()
    print(f"After 3 failures: {cb.get_state()}")

    import asyncio
    async def test_circuit():
        @circuit_breaker_protect()
        async def test_func():
            return "success"

        cb2 = CircuitBreaker(failure_threshold=2)
        try:
            result = await test_func()
            print(f"Result: {result}")
        except HTTPException as e:
            print(f"Circuit breaker triggered: {e.detail}")

    asyncio.run(test_circuit())
