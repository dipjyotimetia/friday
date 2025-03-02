# syntax=docker/dockerfile:1.4
FROM python:3.12-slim AS builder

# Set build arguments and environment variables
ARG POETRY_VERSION=2.1.1
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_HOME="/opt/poetry" \
    PATH="/opt/poetry/bin:$PATH"

# Install system dependencies and Poetry
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        gcc \
        libc6-dev && \
    curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION} && \
    poetry --version

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock README.md ./

# Configure poetry and install dependencies
RUN --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --only main --no-root --compile

# Copy application code
COPY . .

# Build the package
RUN poetry build --format wheel

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
COPY --from=builder --chown=appuser:appuser /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Install the wheel package and clean up
RUN pip install --no-cache-dir *.whl && \
    rm -f *.whl && \
    pip cache purge && \
    # Remove unnecessary files to reduce image size
    find /usr/local/lib/python3.12/site-packages -name "*.pyc" -delete && \
    find /usr/local/lib/python3.12/site-packages -name "__pycache__" -exec rm -r {} +

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