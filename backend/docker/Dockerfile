# ============================================
# XivMind CPU Version - with LanceDB
# ============================================
FROM python:3.12-slim

LABEL maintainer="XivMind"
LABEL description="XivMind - arXiv Paper Management System (CPU)"
LABEL version="0.3.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    XIVMIND_DOCKER=true

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY skills ./skills
COPY subagents ./subagents
COPY main_standalone.py .
COPY .env.example .env.example
COPY static ./static

RUN mkdir -p /app/data/lancedb /app/data/downloads /app/models

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

COPY docker/docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python", "main_standalone.py"]
