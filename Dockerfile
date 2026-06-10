# ──────────────────────────────────────────────
# LILA Lab — Multi-stage Dockerfile
# Language Intelligence for Low-resource Applications
# ──────────────────────────────────────────────

FROM python:3.11-slim AS builder

# Install build dependencies for compiling Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy only dependency files first for Docker layer caching
COPY pyproject.toml README.md ./

# Install all Python dependencies (core + llm + dev)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e ".[all]"

# ──────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL maintainer="LILA Lab <lila.lab0x@gmail.com>"
LABEL description="Language Intelligence for Low-resource Applications — reproducible NLP pipeline execution"

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Default command: interactive Python shell
CMD ["python3"]
