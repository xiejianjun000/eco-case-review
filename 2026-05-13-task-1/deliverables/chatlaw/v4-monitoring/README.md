# V4 行政处罚案卷评查系统 - 监控部署说明

## 概述

本文档描述V4行政处罚案卷评查系统的监控部署方案，包括Prometheus、Grafana、Alertmanager和ELK日志收集的完整配置。

## 架构图

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  V4 Review  │────▶│ Prometheus  │────▶│  Grafana    │
│   System    │     │             │     │             │
└─────────────┘     └──────┬──────┘     └─────────────┘
      │                    │
      │                    ▼
      │             ┌─────────────┐
      │             │ Alertmanager │
      │             └──────┬──────┘
      │                    │
      ▼                    ▼
┌─────────────┐     ┌─────────────┐
│  Filebeat   │────▶│ Elasticsearch│
│   (Logs)    │     │             │
└─────────────┘     └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Kibana    │
                    └─────────────┘
```

## 监控指标清单

### 业务指标

| 指标名称 | 类型 | 说明 |
|---------|------|------|
| `v4_review_total` | Counter | 评查案件总数 |
| `v4_review_success_rate` | Gauge | 当前成功率 |
| `v4_review_veto_rate` | Gauge | 一票否决率 |
| `v4_review_duration_seconds` | Histogram | 各阶段处理时长 |
| `v4_review_queue_size` | Gauge | 任务队列大小 |
| `v4_review_score_bucket` | Histogram | 规范性得分分布 |
| `v4_review_score_avg` | Gauge | 平均规范性得分 |

### 资源指标

| 指标名称 | 类型 | 说明 |
|---------|------|------|
| `v4_review_memory_bytes` | Gauge | 内存使用量 |
| `v4_review_cpu_seconds_total` | Counter | CPU使用时间 |

### 健康指标

| 指标名称 | 类型 | 说明 |
|---------|------|------|
| `v4_review_health_status` | Gauge | 健康状态 |
| `v4_review_start_time_seconds` | Gauge | 启动时间 |
| `v4_review_dependency_status` | Gauge | 依赖服务状态 |

## 告警规则

### 关键告警指标

| 告警名称 | 阈值 | 严重程度 | 说明 |
|----------|------|----------|------|
| 系统不可用 | /health失败>30s | Critical | 服务宕机 |
| 成功率低 | <50%持续5分钟 | Warning | 评查失败率高 |
| 处理超时 | >60s持续5分钟 | Warning | OCR或处理慢 |
| 一票否决率高 | >80% | Warning | 案卷质量异常 |
| 磁盘空间不足 | <10% | Critical | 存储告警 |
| 内存使用率高 | >90% | Warning | 资源告警 |

### 告警等级定义

- **Critical**: 需要立即处理，可能导致服务中断
- **Warning**: 需要关注，可能影响服务质量
- **Info**: 仅供参考

## 部署步骤

### 1. Docker Compose 配置

创建 `docker-compose.monitoring.yml`:

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: v4-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./alerts.yml:/etc/prometheus/alerts.yml
      - ./data/prometheus:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: v4-grafana
    ports:
      - "3000:3000"
    volumes:
      - ./data/grafana:/var/lib/grafana
      - ./grafana-dashboard.json:/etc/grafana/provisioning/dashboards/v4-dashboard.json
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    restart: unless-stopped

  alertmanager:
    image: prom/alertmanager:latest
    container_name: v4-alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter:latest
    container_name: v4-node-exporter
    ports:
      - "9100:9100"
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--path.rootfs=/rootfs'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: v4-elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - ./data/elasticsearch:/usr/share/elasticsearch/data
    restart: unless-stopped

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: v4-kibana
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch
    restart: unless-stopped

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.11.0
    container_name: v4-filebeat
    user: root
    volumes:
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - ./data/filebeat:/usr/share/filebeat/data
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      - elasticsearch
    restart: unless-stopped
```

### 2. 启动监控服务

```bash
# 启动所有监控组件
docker-compose -f docker-compose.monitoring.yml up -d

# 查看服务状态
docker-compose -f docker-compose.monitoring.yml ps

# 查看日志
docker-compose -f docker-compose.monitoring.yml logs -f prometheus
```

### 3. 导入Grafana仪表盘

1. 访问 Grafana: http://localhost:3000
2. 登录 (默认: admin/admin)
3. 导入仪表盘: Dashboard → Import → 上传 `grafana-dashboard.json`

### 4. 配置Alertmanager

创建 `alertmanager.yml`:

```yaml
global:
  resolve_timeout: 5m
  smtp_smarthost: 'smtp.example.com:587'
  smtp_from: 'alertmanager@example.com'

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'
      continue: true
    - match:
        severity: warning
      receiver: 'warning-alerts'

receivers:
  - name: 'default'
    webhook_configs:
      - url: 'http://v4-review:8000/webhooks/alerts'
  - name: 'critical-alerts'
    webhook_configs:
      - url: 'http://v4-review:8000/webhooks/alerts'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'
  - name: 'warning-alerts'
    email_configs:
      - to: 'team@example.com'
        headers:
          subject: 'V4评查系统告警'
```

### 5. 配置ELK日志收集

```bash
# 创建日志目录
mkdir -p /app/logs

# 设置权限
chmod 755 /app/logs
```

## 健康检查接口

### /health

返回服务健康状态:

```json
{
  "status": "healthy",
  "uptime": 12345,
  "version": "v4.1.0",
  "memory_percent": 45.2,
  "cpu_percent": 12.5
}
```

### /ready

返回服务就绪状态:

```json
{
  "ready": true,
  "dependencies": {
    "ocr": "ok",
    "storage": "ok",
    "database": "ok"
  }
}
```

### /metrics

返回Prometheus格式的指标数据。

## Grafana仪表盘

仪表盘包含以下面板:

1. **系统概览**
   - 当前成功率
   - 一票否决率
   - P95处理时长
   - 评查案件总数

2. **评查统计**
   - 评查结果趋势（每小时）
   - 评查结果分布（日）

3. **处理性能**
   - 各阶段处理时长分布
   - 任务队列大小

4. **规范性得分**
   - 得分分布直方图
   - 各等级占比饼图

5. **资源监控**
   - CPU与内存使用
   - 磁盘空间

## 故障排查

### Prometheus 无法抓取指标

```bash
# 检查目标状态
curl http://localhost:9090/api/v1/targets

# 查看Prometheus日志
docker-compose logs prometheus
```

### Grafana 仪表盘无数据

1. 检查数据源配置: Configuration → Data Sources → Prometheus
2. 验证Prometheus URL: http://prometheus:9090
3. 检查指标是否存在: Graph → Metrics → v4_review_total

### Alertmanager 告警未发送

1. 检查告警规则: http://localhost:9093/#/alerts
2. 验证receiver配置
3. 查看Alertmanager日志

## SLO/SLA

| 指标 | 目标 | 告警阈值 |
|------|------|----------|
| 成功率 | ≥95% | <90% |
| P95处理时长 | ≤30s | >60s |
| 可用性 | ≥99.9% | N/A |

## 联系方式

- 值班电话: 400-XXX-XXXX
- 告警邮件: alerts@example.com
- 技术支持: support@example.com
