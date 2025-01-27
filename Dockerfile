# syntax=docker/dockerfile:1.4
FROM python:3.12-slim AS builder

# Set build arguments and environment variables
ARG POETRY_VERSION=2.0.1
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_HOME="/opt/poetry" \
    PATH="/opt/poetry/bin:$PATH"

# Install system dependencies and Poetry
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        libc6-dev \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION} \
    && poetry --version

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock README.md ./

# Configure poetry and install dependencies
RUN poetry install --only main --no-root --compile

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
    PYTHONPATH=/app/src

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && mkdir -p /app /app/.local \
    && chown -R appuser:appuser /app

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder --chown=appuser:appuser /app/dist/*.whl ./
COPY --from=builder --chown=appuser:appuser /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Install the wheel package
RUN pip install --no-cache-dir *.whl \
    && rm -f *.whl \
    && pip cache purge

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Use exec form of CMD with explicit path to binaries
CMD ["/usr/local/bin/uvicorn", "friday.api.app:app", \
     "--host", "0.0.0.0", \
     "--port", "8080", \
     "--workers", "4", \
     "--limit-concurrency", "1000", \
     "--backlog", "2048", \
     "--proxy-headers", \
     "--log-level", "info"]