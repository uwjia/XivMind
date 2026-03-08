#!/bin/bash
set -e

echo "=========================================="
echo "  XivMind Docker Container"
echo "=========================================="

echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"

if command -v nvidia-smi &> /dev/null; then
    echo "GPU detected:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    export EMBEDDING_DEVICE=cuda
else
    echo "No GPU detected, running in CPU mode"
    export EMBEDDING_DEVICE=cpu
fi

mkdir -p /app/data/lancedb
mkdir -p /app/data/downloads
mkdir -p /app/models

if [ ! -f /app/.env ]; then
    echo "No .env file found, creating from example..."
    cp /app/.env.example /app/.env
fi

export DATABASE_TYPE=${DATABASE_TYPE:-lancedb}
export LANCEDB_PATH=${LANCEDB_PATH:-/app/data/lancedb}
export DOWNLOAD_DIR=${DOWNLOAD_DIR:-/app/data/downloads}
export XIVMIND_MODELS_CACHE=${XIVMIND_MODELS_CACHE:-/app/models}

echo "Database: $DATABASE_TYPE"
echo "LanceDB path: $LANCEDB_PATH"
echo "Download dir: $DOWNLOAD_DIR"
echo "Models cache: $XIVMIND_MODELS_CACHE"

if [ "${PRELOAD_MODELS:-false}" = "true" ]; then
    echo "Pre-loading embedding model: ${LOCAL_EMBEDDING_MODEL:-BAAI/bge-m3}"
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('${LOCAL_EMBEDDING_MODEL:-BAAI/bge-m3}')"
fi

echo "Starting XivMind..."
echo "=========================================="

exec "$@"
