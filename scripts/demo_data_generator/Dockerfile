# Multi-stage Dockerfile for ResonaAI Demo Data Generator
FROM node:18-alpine AS frontend-builder

# Set working directory for frontend
WORKDIR /app/frontend

# Copy frontend package files
COPY ../../apps/frontend/package*.json ./
RUN npm ci --only=production

# Copy frontend source
COPY ../../apps/frontend/ ./

# Build frontend (optional - can be done at runtime)
# RUN npm run build

# Python stage
FROM python:3.11-slim AS python-base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (for frontend launching)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy Python requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy demo data generator source
COPY . ./demo_data_generator/

# Copy frontend from builder stage
COPY --from=frontend-builder /app/frontend ./apps/frontend/

# Create data directory
RUN mkdir -p demo_data && chown -R appuser:appuser /app

# Switch to app user
USER appuser

# Expose ports
EXPOSE 3000 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from demo_data_generator.config import DemoConfig; print('OK')" || exit 1

# Default command
CMD ["python", "-m", "demo_data_generator", "launch", "--preset", "quick", "--no-browser"]

# Labels
LABEL maintainer="ResonaAI Team <dev@resonaai.com>" \
      version="1.0.0" \
      description="ResonaAI Demo Data Generator Container" \
      org.opencontainers.image.title="ResonaAI Demo Data Generator" \
      org.opencontainers.image.description="Containerized demo data generator for ResonaAI platform" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.vendor="ResonaAI" \
      org.opencontainers.image.licenses="MIT"