# ==========================================
# MediFinder Production Multi-Stage Dockerfile
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final runtime image
FROM python:3.11-slim

WORKDIR /app

# Create non-root system user for security
RUN groupadd -r medifinder && useradd -r -g medifinder -d /app -s /sbin/nologin medifinder

# Copy installed wheels from builder
COPY --from=builder /root/.local /home/medifinder/.local

ENV PATH=/home/medifinder/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Copy application source code
COPY backend /app/backend
COPY run.py /app/run.py

# Set proper directory permissions
RUN mkdir -p /app/backend/src/static/uploads && \
    chown -R medifinder:medifinder /app

USER medifinder

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/v1/health').read()" || exit 1

CMD ["python3", "run.py"]
