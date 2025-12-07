# Adaptive Intelligence Pipeline - Production Dockerfile
# Week 4: Using uv for dependency management

FROM python:3.11-slim

# Copy uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files AND README.md (required by hatchling for build)
COPY pyproject.toml uv.lock* README.md ./

# Create empty app directory for hatchling to find the package
# This allows uv sync to work before copying all source code
RUN mkdir -p app && touch app/__init__.py

# Install dependencies (no-editable means don't install the project itself yet)
RUN uv sync --frozen --no-dev --no-editable || uv sync --no-dev --no-editable

# Now copy all application code
COPY app/ ./app/
COPY data/ ./data/
COPY init-scripts/ ./init-scripts/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with uv
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]