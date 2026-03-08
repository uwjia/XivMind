# XivMind Docker Deployment

This directory contains all Docker-related files for deploying XivMind.

## Directory Structure

```
docker/
├── .dockerignore          # Files to exclude from Docker build context
├── Dockerfile             # XivMind CPU image (Python 3.12-slim)
├── Dockerfile.gpu         # XivMind GPU image (CUDA 12.8)
├── docker-entrypoint.sh   # Container startup script
├── compose/
│   ├── xivmind.yml        # XivMind CPU with LanceDB
│   ├── xivmind.gpu.yml    # XivMind GPU with LanceDB + CUDA
│   ├── milvus.yml         # Milvus full stack (etcd + minio + standalone + attu)
│   └── milvus.lite.yml    # Milvus lite (embedded mode)
└── README.md              # This file
```

## Quick Start

### Option 1: XivMind with LanceDB (Recommended)

**CPU Version:**
```bash
cd backend/docker
docker-compose -f compose/xivmind.yml up -d
```

**GPU Version (CUDA 12.8):**
```bash
cd backend/docker
docker-compose -f compose/xivmind.gpu.yml up -d
```

### Option 2: XivMind with Milvus

First, start Milvus:
```bash
cd backend/docker
docker-compose -f compose/milvus.lite.yml up -d  # Lite mode
# or
docker-compose -f compose/milvus.yml up -d       # Full stack
```

Then run XivMind locally:
```bash
cd backend
DATABASE_TYPE=milvus python main_standalone.py
```

## Image Variants

| Image | Base | Size | Use Case |
|-------|------|------|----------|
| `xivmind:latest` | python:3.12-slim | ~8.7GB | CPU-only deployment |
| `xivmind:gpu` | pytorch:2.8.0-cuda12.8 | ~8.8GB | GPU acceleration |

## Environment Variables

Key environment variables (can be set in `.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `XIVMIND_PORT` | 8000 | Web server port |
| `DATABASE_TYPE` | lancedb | Database type (lancedb/milvus) |
| `USE_LOCAL_EMBEDDING` | true | Use local embedding model |
| `LOCAL_EMBEDDING_MODEL` | BAAI/bge-m3 | Embedding model name |
| `EMBEDDING_DEVICE` | cpu/cuda | Device for embedding |
| `HF_ENDPOINT` | https://hf-mirror.com | HuggingFace mirror |

## Volumes

| Volume | Path | Description |
|--------|------|-------------|
| `xivmind_data` | /app/data | Database and downloads |
| `xivmind_models` | /app/models | Cached embedding models |

## Building Images

```bash
# CPU image
docker build -t xivmind:latest -f docker/Dockerfile ..

# GPU image
docker build -t xivmind:gpu -f docker/Dockerfile.gpu ..
```

## Milvus Services

### Full Stack (milvus.yml)
- **etcd**: Metadata storage
- **minio**: Object storage (ports 9000, 9001)
- **standalone**: Milvus server (port 19530)
- **attu**: Web UI (port 3000)

### Lite Mode (milvus.lite.yml)
- **standalone**: Embedded Milvus with built-in etcd and minio
- **attu**: Web UI (port 3000)

## Health Checks

All services include health checks. Check status:
```bash
docker-compose -f compose/xivmind.yml ps
```

## Logs

View logs:
```bash
docker-compose -f compose/xivmind.yml logs -f xivmind
```

## Troubleshooting

### Model Download Issues
Set HuggingFace mirror:
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### Database Connection Issues
Check if the database service is healthy:
```bash
docker-compose -f compose/milvus.lite.yml ps
```
