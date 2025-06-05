FROM python:3.12-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Install system dependencies and uv
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    pip install uv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user with home directory
RUN groupadd -r -g 1000 appuser && \
    useradd -r -u 1000 -g appuser -m appuser

WORKDIR /app

# Copy dependency files and install dependencies
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen

# Copy application code
COPY . .
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE ${PORT}

# Start the application
CMD ["uv", "run", "uvicorn", "friday.api.app:app", "--host", "0.0.0.0", "--port", "8080"]