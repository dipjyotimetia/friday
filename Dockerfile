# syntax=docker/dockerfile:1.4
FROM python:3.12-slim AS builder

# Set build arguments and environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies and uv
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        gcc \
        libc6-dev && \
    pip install uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock README.md ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Copy application code
COPY . .

# Build the package
RUN uv build

# Production stage
FROM python:3.12-slim AS runtime

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    PYTHONPATH=/app/src \
    WORKERS=2 \
    MAX_WORKERS=4 \
    WEB_CONCURRENCY=2

# Create non-root user with explicit UID/GID for better Cloud Run compatibility
RUN groupadd -r -g 1000 appuser && \
    useradd -r -u 1000 -g appuser appuser && \
    mkdir -p /app /app/.local && \
    chown -R appuser:appuser /app

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder --chown=appuser:appuser /app/dist/*.whl ./
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Install the wheel package and clean up
RUN pip install --no-cache-dir *.whl && \
    rm -f *.whl && \
    pip cache purge

# Set PATH to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Use exec form of CMD with auto-scaling worker configuration
CMD ["/bin/sh", "-c", "\
    WORKER_COUNT=$(( ${WORKERS} > ${MAX_WORKERS} ? ${MAX_WORKERS} : ${WORKERS} )) && \
    /usr/local/bin/uvicorn \
    friday.api.app:app \
    --host 0.0.0.0 \
    --port ${PORT} \
    --workers ${WORKER_COUNT} \
    --limit-concurrency 100 \
    --backlog 2048 \
    --proxy-headers \
    --forwarded-allow-ips='*' \
    --log-level info \
    --no-access-log \
    --timeout-keep-alive 75"]