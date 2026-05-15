# ============================================================
# V4 行政处罚案卷评查系统 - 生产级 Dockerfile
# 多阶段构建，优化镜像大小 < 500MB
# ============================================================

# ---------- 第一阶段: 依赖构建 ----------
FROM python:3.11-slim AS builder

WORKDIR /build

# 安装构建依赖（编译 C 扩展用）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libjpeg-dev \
        zlib1g-dev \
        libffi-dev \
        cargo \
    && rm -rf /var/lib/apt/lists/*

# 先复制依赖文件，利用 Docker 层缓存
COPY requirements.txt .

# 将依赖安装到指定目录，便于后续拷贝
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- 第二阶段: 运行时镜像 ----------
FROM python:3.11-slim AS runtime

LABEL maintainer="chatlaw-team"
LABEL version="4.0.0"
LABEL description="V4 行政处罚案卷评查系统"

# 安装运行时系统依赖（OCR 等需要）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        libjpeg62-turbo \
        zlib1g \
        tesseract-ocr \
        tesseract-ocr-chi-sim \
        poppler-utils \
        libgl1-mesa-glx \
        libglib2.0-0 \
        dumb-init \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove

# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# 从 builder 阶段拷贝已安装的 Python 依赖
COPY --from=builder /install /usr/local

# 设置工作目录
WORKDIR /app

# 拷贝应用代码
COPY --chown=appuser:appuser . .

# 创建数据目录
RUN mkdir -p /app/data /app/logs && chown -R appuser:appuser /app

# 切换到非 root 用户
USER appuser

# 暴露端口
EXPOSE 8000

# 环境变量默认值
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    OCR_ENGINE=local \
    MAX_PDF_SIZE=50 \
    MAX_PAGES=500 \
    LOG_LEVEL=INFO \
    REDIS_URL=redis://localhost:6379/0 \
    TZ=Asia/Shanghai

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 使用 dumb-init 作为 PID 1，正确处理信号转发
ENTRYPOINT ["dumb-init", "--"]

# 启动命令：使用 gunicorn 生产服务器，支持优雅停机
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--threads", "2", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--graceful-timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "INFO", \
     "app.main:app"]
