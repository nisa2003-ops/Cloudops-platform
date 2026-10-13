# Build stage: compile/install wheels
FROM python:3.11-slim AS builder

WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final Runtime stage: minimal and secure
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/cloudops/.local/bin:${PATH}" \
    APP_ENV="production" \
    PORT=8000

# Create dedicated non-root user and group
RUN groupadd -r cloudops && useradd -r -g cloudops -u 10001 -d /home/cloudops -m cloudops

# Copy installed python packages from builder
COPY --from=builder /root/.local /home/cloudops/.local

# Copy application source code
COPY --chown=cloudops:cloudops app/ ./app

# Set non-root user
USER cloudops

EXPOSE 8000

# Container healthcheck using standard Python library (no curl dependency needed)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; sys_exit = 0 if urllib.request.urlopen('http://localhost:8000/health').getcode() == 200 else 1; exit(sys_exit)"

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]