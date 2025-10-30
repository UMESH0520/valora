# Multi-stage build for production optimization
FROM python:3.11-slim as builder

# Set build arguments
ARG ENVIRONMENT=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy requirements first for better caching
COPY requirements.txt .

# Create wheels for all dependencies
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production

# Create non-root user
RUN groupadd -g 1000 valora && \
    useradd -r -u 1000 -g valora valora

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy wheels from builder stage
COPY --from=builder /wheels /wheels

# Install Python dependencies from wheels
RUN pip install --no-index --find-links /wheels -r /dev/stdin << EOF
$(cat requirements.txt | grep -v "^#" | grep -v "^$")
EOF

# Copy application code
COPY --chown=valora:valora . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R valora:valora /app/logs /app/data

# Switch to non-root user
USER valora

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]