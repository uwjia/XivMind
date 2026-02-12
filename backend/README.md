# XivMind Backend

[中文文档](README_CN.md)

FastAPI + Milvus backend service for paper bookmark management and download task management.

## Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application entry
│   ├── config.py         # Configuration management
│   ├── models.py         # Pydantic model definitions
│   ├── database.py       # Milvus database service
│   └── routers/
│       ├── __init__.py
│       ├── bookmarks.py  # Bookmark management API
│       └── downloads.py  # Download task API
├── docker-compose.yml    # Milvus standard deployment
├── docker-compose.lite.yml # Milvus lite deployment
├── milvus.sh / milvus.bat # Milvus startup scripts
├── start.sh / start.bat  # Backend startup scripts
├── requirements.txt
├── .env.example
└── README.md
```

## Requirements

- Python 3.10+
- Docker & Docker Compose
- Milvus 2.3.6+

## Quick Start

### 1. Start Milvus

Two deployment modes are available:

| Mode         | Containers                    | Memory | Use Case            |
| ------------ | ----------------------------- | ------ | ------------------- |
| **Standard** | 4 (etcd, MinIO, Milvus, Attu) | ~2GB   | Production          |
| **Lite**     | 2 (Milvus, Attu)              | ~1GB   | Development/Testing |

**Windows:**

```cmd
milvus.bat start          # Standard mode (default)
milvus.bat start lite     # Lite mode (embedded etcd/MinIO)
milvus.bat stop           # Stop services
milvus.bat status         # View status
milvus.bat logs           # View logs
milvus.bat clean          # Clean data (WARNING: deletes all data)
```

**Linux/Mac:**

```bash
chmod +x milvus.sh
./milvus.sh start          # Standard mode (default)
./milvus.sh start lite     # Lite mode (embedded etcd/MinIO)
./milvus.sh stop           # Stop services
./milvus.sh status         # View status
./milvus.sh logs           # View logs
./milvus.sh clean          # Clean data (WARNING: deletes all data)
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` file:

```env
MILVUS_HOST=localhost
MILVUS_PORT=19530
DATABASE_NAME=xivmind
DOWNLOAD_DIR=./downloads
```

### 3. Start Backend Service

**Windows:**

```cmd
start.bat install   # Install dependencies (first time only)
start.bat start     # Start service (background)
start.bat stop      # Stop service
start.bat dev       # Development mode (foreground with hot reload)
```

**Linux/Mac:**

```bash
chmod +x start.sh
./start.sh install   # Install dependencies (first time only)
./start.sh start     # Start service (background)
./start.sh stop      # Stop service
./start.sh restart   # Restart service
./start.sh dev       # Development mode (foreground with hot reload)
./start.sh logs      # View logs
./start.sh status    # Check service status
```

**Manual Start (Alternative):**

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Service Components

### Standard Mode

| Service     | Port      | Description                     |
| ----------- | --------- | ------------------------------- |
| **Milvus**  | 19530     | Vector database                 |
| **Attu**    | 3000      | Milvus GUI management interface |
| **MinIO**   | 9000/9001 | Object storage                  |
| **etcd**    | 2379      | Metadata storage                |
| **FastAPI** | 8000      | Backend API service             |

### Lite Mode

| Service     | Port  | Description                           |
| ----------- | ----- | ------------------------------------- |
| **Milvus**  | 19530 | Vector database (embedded etcd/MinIO) |
| **Attu**    | 3000  | Milvus GUI management interface       |
| **FastAPI** | 8000  | Backend API service                   |

## Access URLs

- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **Milvus**: `localhost:19530`
- **Attu GUI**: http://localhost:3000
- **MinIO Console** (Standard mode only): http://localhost:9001 (Username/Password: minioadmin/minioadmin)

## API Endpoints

### Bookmarks `/api/bookmarks`

| Method | Path                | Description         |
| ------ | ------------------- | ------------------- |
| POST   | `/`                 | Add bookmark        |
| DELETE | `/{paper_id}`       | Remove bookmark     |
| GET    | `/check/{paper_id}` | Check if bookmarked |
| GET    | `/`                 | Get bookmark list   |
| GET    | `/search`           | Search bookmarks    |

### Downloads `/api/downloads`

| Method | Path               | Description          |
| ------ | ------------------ | -------------------- |
| POST   | `/`                | Create download task |
| GET    | `/`                | Get task list        |
| GET    | `/{task_id}`       | Get task details     |
| DELETE | `/{task_id}`       | Delete task          |
| POST   | `/{task_id}/retry` | Retry failed task    |
| POST   | `/{task_id}/cancel`| Cancel task          |
| POST   | `/{task_id}/open`  | Open downloaded file |
| WebSocket | `/ws`           | Real-time progress   |

## Docker Compose Services

### Standard Mode (docker-compose.yml)

```yaml
services:
  etcd:        # Milvus metadata storage
  minio:       # Milvus object storage
  standalone:  # Milvus standalone
  attu:        # Milvus GUI management tool
```

### Lite Mode (docker-compose.lite.yml)

```yaml
services:
  standalone:  # Milvus with embedded etcd/MinIO
  attu:        # Milvus GUI management tool
```

## Development

### Database Initialization

The following collections are automatically created on startup:

- `bookmarks` - Bookmarked papers
- `downloads` - Download tasks

### Download Task Flow

1. Frontend calls `POST /api/downloads` to create task
2. Backend executes download asynchronously (with progress tracking)
3. Frontend polls or uses `GET /api/downloads/{task_id}` for progress
4. File path available after completion

### Error Handling

All APIs return unified error format:

```json
{
  "detail": "Error message"
}
```

## Troubleshooting

### Milvus Connection Failed

Check if Milvus is running:

```bash
curl http://localhost:9091/healthz
```

### Port Conflicts

Modify port mappings in `docker-compose.yml` or `docker-compose.lite.yml` if default ports are occupied.

### Data Persistence

Data is stored in `./volumes` directory. To clean up:

```bash
./milvus.sh clean  # Linux/Mac
milvus.bat clean   # Windows
```
