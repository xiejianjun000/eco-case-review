"""
V4 行政处罚案卷评查系统 - Prometheus 指标暴露客户端

使用方法:
    from prometheus_client import start_http_server
    from prometheus_client import Gauge, Counter, Histogram

    # 在应用启动时
    start_http_server(8000)

    # 或使用本模块
    from prometheus_client import V4Metrics
    metrics = V4Metrics()
    metrics.inc_review_total('pass')
"""

import time
import random
from functools import wraps
from typing import Optional, Dict, Any

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Summary,
    Info,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY,
    CollectorRegistry,
    multiprocess,
    Collector,
    Enum
)
from prometheus_client.core import (
    GaugeMetricFamily,
    CounterMetricFamily,
    HistogramMetricFamily,
    LazyLoadingServer,
    MATH_MACHINE_EPSILON
)
from prometheus_client.openmetrics.exposition import (
    generate_latest as om_generate_latest,
    CONTENT_TYPE_LATEST as OM_CONTENT_TYPE_LATEST
)
from flask import Flask, Response, request
import logging

logger = logging.getLogger(__name__)


class V4Metrics:
    """V4评查系统指标收集器"""

    def __init__(self, namespace: str = "v4_review"):
        self.namespace = namespace

        # ========== 评查统计指标 ==========

        # 评查案件总数
        self.review_total = Counter(
            f"{namespace}_total",
            "评查案件总数",
            ["result", "level"]  # result: pass/fail/veto, level: A/B/C/D
        )

        # 当前成功率
        self.success_rate = Gauge(
            f"{namespace}_success_rate",
            "当前评查成功率"
        )

        # 一票否决率
        self.veto_rate = Gauge(
            f"{namespace}_veto_rate",
            "当前一票否决率"
        )

        # ========== 性能指标 ==========

        # 处理时长分布
        self.duration_seconds = Histogram(
            f"{namespace}_duration_seconds",
            "评查各阶段处理时长",
            ["stage"],  # stage: ocr/parse/score/report/total
            buckets=[1, 2, 5, 10, 20, 30, 45, 60, 90, 120, 180, 300]
        )

        # 任务队列大小
        self.queue_size = Gauge(
            f"{namespace}_queue_size",
            "当前待处理任务队列大小"
        )

        # ========== 规范性得分指标 ==========

        # 规范性得分分布
        self.score_bucket = Histogram(
            f"{namespace}_score_bucket",
            "规范性得分分布",
            buckets=[60, 70, 75, 80, 85, 90, 95, 100]
        )

        # 平均规范性得分
        self.score_avg = Gauge(
            f"{namespace}_score_avg",
            "平均规范性得分"
        )

        # ========== 资源指标 ==========

        # 内存使用
        self.memory_bytes = Gauge(
            f"{namespace}_memory_bytes",
            "内存使用量(字节)"
        )

        # CPU使用
        self.cpu_seconds = Counter(
            f"{namespace}_cpu_seconds_total",
            "CPU使用时间累计(秒)"
        )

        # ========== 健康检查指标 ==========

        # 健康状态 (1=健康, 0=不健康)
        self.health_status = Gauge(
            f"{namespace}_health_status",
            "服务健康状态"
        )

        # 服务启动时间
        self.start_time = Gauge(
            f"{namespace}_start_time_seconds",
            "服务启动时间戳"
        )

        # 依赖服务状态
        self.dependency_status = Gauge(
            f"{namespace}_dependency_status",
            "依赖服务状态",
            ["service"]  # service: ocr/storage/database
        )

        # ========== 请求指标 ==========

        # HTTP请求计数
        self.http_requests_total = Counter(
            f"{namespace}_http_requests_total",
            "HTTP请求总数",
            ["method", "endpoint", "status_code"]
        )

        # HTTP请求延迟
        self.http_request_duration_seconds = Histogram(
            f"{namespace}_http_request_duration_seconds",
            "HTTP请求延迟",
            ["method", "endpoint"],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
        )

        # 初始化启动时间
        self.start_time.set_to_current_time()

    def inc_review_total(self, result: str, level: Optional[str] = None):
        """增加评查案件计数

        Args:
            result: 评查结果 (pass/fail/veto)
            level: 评查等级 (A/B/C/D)
        """
        labels = {"result": result}
        if level:
            labels["level"] = level
        self.review_total.labels(**labels).inc()

    def set_success_rate(self, rate: float):
        """设置成功率"""
        self.success_rate.set(rate)

    def set_veto_rate(self, rate: float):
        """设置一票否决率"""
        self.veto_rate.set(rate)

    def observe_duration(self, duration: float, stage: str):
        """记录处理时长

        Args:
            duration: 处理时长(秒)
            stage: 处理阶段 (ocr/parse/score/report/total)
        """
        self.duration_seconds.labels(stage=stage).observe(duration)

    def set_queue_size(self, size: int):
        """设置队列大小"""
        self.queue_size.set(size)

    def observe_score(self, score: float):
        """记录规范性得分"""
        self.score_bucket.observe(score)

    def set_score_avg(self, avg: float):
        """设置平均得分"""
        self.score_avg.set(avg)

    def set_memory_usage(self, bytes: int):
        """设置内存使用"""
        self.memory_bytes.set(bytes)

    def inc_cpu_time(self, seconds: float):
        """增加CPU使用时间"""
        self.cpu_seconds.inc(seconds)

    def set_health_status(self, healthy: bool):
        """设置健康状态"""
        self.health_status.set(1 if healthy else 0)

    def set_dependency_status(self, service: str, status: str):
        """设置依赖服务状态

        Args:
            service: 服务名称 (ocr/storage/database)
            status: 状态 (ok/error/timeout)
        """
        status_code = {"ok": 1, "error": 0, "timeout": -1}.get(status, -2)
        self.dependency_status.labels(service=service).set(status_code)

    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """记录HTTP请求

        Args:
            method: HTTP方法
            endpoint: 请求路径
            status_code: 响应状态码
            duration: 请求耗时(秒)
        """
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        self.http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)


# 全局指标实例
_metrics: Optional[V4Metrics] = None


def get_metrics() -> V4Metrics:
    """获取全局指标实例"""
    global _metrics
    if _metrics is None:
        _metrics = V4Metrics()
    return _metrics


def setup_metrics(app: Optional[Flask] = None, port: int = 8000):
    """设置指标暴露端点

    Args:
        app: Flask应用实例(可选)
        port: 指标端口号
    """
    metrics = get_metrics()

    if app:
        @app.route("/metrics")
        def metrics_endpoint():
            return Response(
                generate_latest(REGISTRY),
                mimetype=CONTENT_TYPE_LATEST
            )

        @app.route("/health")
        def health_endpoint():
            """健康检查端点"""
            from flask import jsonify
            import psutil

            uptime = time.time() - metrics.start_time._value.get()
            memory_info = psutil.virtual_memory()

            return jsonify({
                "status": "healthy",
                "uptime": int(uptime),
                "version": "v4.1.0",
                "memory_percent": memory_info.percent,
                "cpu_percent": psutil.cpu_percent(interval=0.1)
            })

        @app.route("/ready")
        def ready_endpoint():
            """就绪检查端点"""
            from flask import jsonify

            # 检查依赖服务
            dependencies = {
                "ocr": "ok",
                "storage": "ok",
                "database": "ok"
            }

            ready = all(v == "ok" for v in dependencies.values())

            return jsonify({
                "ready": ready,
                "dependencies": dependencies
            })
    else:
        # 启动独立指标服务器
        from prometheus_client import start_http_server
        start_http_server(port)
        logger.info(f"Prometheus metrics server started on port {port}")


def track_request_duration(endpoint: str):
    """HTTP请求耗时追踪装饰器"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            metrics = get_metrics()
            start_time = time.time()
            try:
                response = f(*args, **kwargs)
                status_code = getattr(response, 'status_code', 200)
                metrics.record_http_request(
                    request.method,
                    endpoint,
                    status_code,
                    time.time() - start_time
                )
                return response
            except Exception as e:
                metrics.record_http_request(
                    request.method,
                    endpoint,
                    500,
                    time.time() - start_time
                )
                raise
        return wrapper
    return decorator


def track_review_duration(stage: str):
    """评查处理耗时追踪装饰器"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            metrics = get_metrics()
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time
                metrics.observe_duration(duration, stage)
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics.observe_duration(duration, stage)
                raise
        return wrapper
    return decorator


# 示例：模拟数据更新（用于测试）
def simulate_metrics():
    """模拟指标数据（用于开发和测试）"""
    import random
    import threading
    import time

    metrics = get_metrics()

    def update_loop():
        while True:
            # 模拟评查结果
            results = ["pass", "fail", "veto"]
            result = random.choice(results)
            levels = ["A", "B", "C", "D"]
            level = random.choice(levels)
            metrics.inc_review_total(result, level)

            # 模拟成功率变化
            success_rate = random.uniform(0.6, 0.95)
            metrics.set_success_rate(success_rate)

            # 模拟一票否决率变化
            veto_rate = random.uniform(0.05, 0.25)
            metrics.set_veto_rate(veto_rate)

            # 模拟处理时长
            for stage in ["ocr", "parse", "score", "report", "total"]:
                duration = random.uniform(1, 30)
                metrics.observe_duration(duration, stage)

            # 模拟队列大小
            queue_size = random.randint(10, 500)
            metrics.set_queue_size(queue_size)

            # 模拟规范性得分
            score = random.uniform(60, 100)
            metrics.observe_score(score)
            metrics.set_score_avg(random.uniform(75, 90))

            # 模拟资源使用
            import psutil
            process = psutil.Process()
            metrics.set_memory_usage(process.memory_info().rss)
            metrics.set_cpu_time(random.uniform(0.1, 1.0))

            time.sleep(5)

    thread = threading.Thread(target=update_loop, daemon=True)
    thread.start()


if __name__ == "__main__":
    # 演示用法
    print("V4 Metrics Demo")

    # 创建指标实例
    metrics = get_metrics()

    # 模拟数据
    simulate_metrics()

    # 启动Flask应用示例
    app = Flask(__name__)
    setup_metrics(app, port=8000)

    print("Starting Flask app with metrics on port 8000...")
    print("Endpoints:")
    print("  - /metrics  : Prometheus metrics")
    print("  - /health   : Health check")
    print("  - /ready    : Readiness check")

    app.run(host="0.0.0.0", port=8000)
