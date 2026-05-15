from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time

# 业务指标
review_total = Counter('v4_review_total', 'Total reviews', ['result'])  # pass/fail/veto
review_duration = Histogram('v4_review_duration_seconds', 'Review duration', ['stage'])
processing_queue = Gauge('v4_review_queue_size', 'Processing queue size')

# 系统指标
memory_usage = Gauge('v4_review_memory_bytes', 'Memory usage')
cpu_usage = Gauge('v4_review_cpu_seconds_total', 'CPU usage')

def get_metrics():
    return generate_latest(), CONTENT_TYPE_LATEST
