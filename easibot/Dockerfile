# Dockerfile for EASIBot Multi-Agent System
# Optimized for AWS Lambda/ECS deployment

ARG UV_VERSION=latest
ARG PYTHON_VERSION=3.14

# Stage 1: UV installation
FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

# Stage 2: Build stage - Install dependencies
FROM python:${PYTHON_VERSION}-slim AS builder

WORKDIR /app

# Copy uv from the official image
COPY --from=uv /uv /uvx /bin/

# Set Python environment variables
ENV PYTHONDONTWRITEBYTECODE=True \
    PYTHONUNBUFFERED=True \
    UV_LINK_MODE=copy

# Copy dependency files
COPY pyproject.toml ./

# Install runtime dependencies for AWS and LangGraph
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    # For OpenCV and image processing (if needed for document parsing)
    libgl1 libglib2.0-0 \
    # For AWS SDK and cryptography
    gcc \
    libc-dev \
    # Clean up to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (frozen for reproducibility)
RUN uv sync --frozen --no-install-project --no-dev

# Stage 3: Runtime stage - Minimal production image
FROM python:${PYTHON_VERSION}-slim AS runtime

WORKDIR /app

# Set Python environment variables
ENV PYTHONDONTWRITEBYTECODE=True \
    PYTHONUNBUFFERED=True \
    PATH="/app/.venv/bin:$PATH" \
    # AWS Lambda environment compatibility
    AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-west-2}

# Install only runtime dependencies (no build tools)
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    # Runtime libraries for OpenCV/image processing
    libgl1 libglib2.0-0 \
    # CA certificates for HTTPS requests
    ca-certificates \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 easibot \
    && chown -R easibot:easibot /app

USER easibot

# Health check endpoint (customize based on your deployment)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command - can be overridden in ECS task definition or Lambda
CMD ["python", "-m", "easibot.handlers.lambda_handler"]

# Expose port for local testing (not used in Lambda)
EXPOSE 8080

# Labels for container metadata
LABEL maintainer="EASIBot Team" \
    description="EASIBot Multi-Agent Consultant System" \
    version="1.0" \
    project="easibot"
