# Multi-stage build for DistroViz API
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION=3.0.0

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set labels
LABEL maintainer="DistroViz Team"
LABEL version="3.0.0"
LABEL description="DistroViz API Service"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r distroviz && useradd -r -g distroviz -u 1001 distroviz

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/distroviz/.local

# Copy application code
COPY --chown=distroviz:distroviz . .

# Create directories for data and logs
RUN mkdir -p /app/data /app/logs \
    && chown -R distroviz:distroviz /app

# Set environment variables
ENV PATH=/home/distroviz/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:///app/data/distroviz.db
ENV PORT=8000
ENV ENVIRONMENT=production

# Switch to non-root user
USER distroviz

# Initialize database on container start
RUN python -c "from shared.database import init_database; init_database()" || echo "Database initialization will happen at runtime"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Start command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

# Alternative start command for development
# CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Create requirements.txt content as comment for reference
# fastapi==0.104.1
# uvicorn[standard]==0.24.0
# sqlalchemy==2.0.23
# pydantic==2.5.0
# python-multipart==0.0.6
# python-dotenv==1.0.0