# ============================================================
# HERMES Case Review System - Production Dockerfile
# Multi-stage build for optimized image size < 500MB
# ============================================================

# ---------- Stage 1: Builder ----------
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libjpeg-dev \
        zlib1g-dev \
        libffi-dev \
        cargo \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements-prod.txt .

# Install Python dependencies to separate directory
RUN pip install --no-cache-dir --prefix=/install -r requirements-prod.txt

# ---------- Stage 2: Runtime ----------
FROM python:3.11-slim AS runtime

LABEL maintainer="hermes-case-review-team"
LABEL version="1.0.0"
LABEL description="HERMES Case Review System - Production"

# Install runtime system dependencies
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

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Copy pre-installed Python packages from builder
COPY --from=builder /install /usr/local

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser templates/ ./templates/
COPY --chown=appuser:appuser tests/ ./tests/
COPY --chown=appuser:appuser test_data/ ./test_data/

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/uploads /app/reports && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    OCR_ENGINE=local \
    MAX_PDF_SIZE=50 \
    MAX_PAGES=500 \
    LOG_LEVEL=INFO \
    REDIS_URL=redis://redis:6379/0 \
    TZ=Asia/Shanghai

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use dumb-init for proper signal handling
ENTRYPOINT ["dumb-init", "--"]

# Production server with Gunicorn
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--threads", "2", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--graceful-timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "src.api.routes:app"]
