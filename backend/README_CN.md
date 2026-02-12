# XivMind Backend 中文文档

[English](README.md)

FastAPI + Milvus 后端服务，用于论文收藏管理和下载任务管理。

## 目录结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI 应用入口
│   ├── config.py         # 配置管理
│   ├── models.py         # Pydantic 模型定义
│   ├── database.py       # Milvus 数据库服务
│   └── routers/
│       ├── __init__.py
│       ├── bookmarks.py  # 收藏管理 API
│       └── downloads.py  # 下载任务 API
├── docker-compose.yml    # Milvus 标准部署
├── docker-compose.lite.yml # Milvus 精简部署
├── milvus.sh / milvus.bat # Milvus 启动脚本
├── start.sh / start.bat  # 后端启动脚本
├── requirements.txt
├── .env.example
└── README.md
```

## 环境要求

- Python 3.10+
- Docker & Docker Compose
- Milvus 2.3.6+

## 快速开始

### 1. 启动 Milvus

提供两种部署模式：

| 模式 | 容器数量 | 内存占用 | 适用场景 |
|------|---------|---------|---------|
| **标准模式** | 4个 (etcd, MinIO, Milvus, Attu) | ~2GB | 生产环境 |
| **精简模式** | 2个 (Milvus, Attu) | ~1GB | 开发测试 |

**Windows:**
```cmd
milvus.bat start          # 标准模式（默认）
milvus.bat start lite     # 精简模式（内嵌 etcd/MinIO）
milvus.bat stop           # 停止服务
milvus.bat status         # 查看状态
milvus.bat logs           # 查看日志
milvus.bat clean          # 清理数据（警告：会删除所有数据）
```

**Linux/Mac:**
```bash
chmod +x milvus.sh
./milvus.sh start          # 标准模式（默认）
./milvus.sh start lite     # 精简模式（内嵌 etcd/MinIO）
./milvus.sh stop           # 停止服务
./milvus.sh status         # 查看状态
./milvus.sh logs           # 查看日志
./milvus.sh clean          # 清理数据（警告：会删除所有数据）
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```env
MILVUS_HOST=localhost
MILVUS_PORT=19530
DATABASE_NAME=xivmind
DOWNLOAD_DIR=./downloads
```

### 3. 启动后端服务

**Windows:**
```cmd
start.bat install   # 安装依赖（首次运行）
start.bat start     # 启动服务（后台运行）
start.bat stop      # 停止服务
start.bat dev       # 开发模式（前台运行，支持热重载）
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh install   # 安装依赖（首次运行）
./start.sh start     # 启动服务（后台运行）
./start.sh stop      # 停止服务
./start.sh restart   # 重启服务
./start.sh dev       # 开发模式（前台运行，支持热重载）
./start.sh logs      # 查看日志
./start.sh status    # 查看服务状态
```

**手动启动（备选方案）：**
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## 服务组件

### 标准模式

| 服务 | 端口 | 说明 |
|------|------|------|
| **Milvus** | 19530 | 向量数据库 |
| **Attu** | 3000 | Milvus GUI 管理界面 |
| **MinIO** | 9000/9001 | 对象存储 |
| **etcd** | 2379 | 元数据存储 |
| **FastAPI** | 8000 | 后端 API 服务 |

### 精简模式

| 服务 | 端口 | 说明 |
|------|------|------|
| **Milvus** | 19530 | 向量数据库（内嵌 etcd/MinIO） |
| **Attu** | 3000 | Milvus GUI 管理界面 |
| **FastAPI** | 8000 | 后端 API 服务 |

## 访问地址

- **API 文档 (Swagger)**: http://localhost:8000/docs
- **API 文档 (ReDoc)**: http://localhost:8000/redoc
- **Milvus**: `localhost:19530`
- **Attu GUI**: http://localhost:3000
- **MinIO Console**（仅标准模式）: http://localhost:9001 (用户名/密码: minioadmin/minioadmin)

## API 接口

### 收藏管理 `/api/bookmarks`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/` | 添加收藏 |
| DELETE | `/{paper_id}` | 删除收藏 |
| GET | `/check/{paper_id}` | 检查是否已收藏 |
| GET | `/` | 获取收藏列表 |
| GET | `/search` | 搜索收藏 |

### 下载管理 `/api/downloads`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/` | 创建下载任务 |
| GET | `/` | 获取任务列表 |
| GET | `/{task_id}` | 获取任务详情 |
| DELETE | `/{task_id}` | 删除任务 |
| POST | `/{task_id}/retry` | 重试失败任务 |
| POST | `/{task_id}/cancel` | 取消任务 |
| POST | `/{task_id}/open` | 打开已下载文件 |
| WebSocket | `/ws` | 实时进度更新 |

## Docker Compose 服务说明

### 标准模式 (docker-compose.yml)

```yaml
services:
  etcd:        # Milvus 元数据存储
  minio:       # Milvus 对象存储
  standalone:  # Milvus 单机版
  attu:        # Milvus GUI 管理工具
```

### 精简模式 (docker-compose.lite.yml)

```yaml
services:
  standalone:  # Milvus（内嵌 etcd/MinIO）
  attu:        # Milvus GUI 管理工具
```

## 开发说明

### 数据库初始化

应用启动时会自动创建以下集合：
- `bookmarks` - 收藏的论文
- `downloads` - 下载任务

### 下载任务流程

1. 前端调用 `POST /api/downloads` 创建任务
2. 后台异步执行下载（支持进度跟踪）
3. 前端轮询或通过 `GET /api/downloads/{task_id}` 获取进度
4. 下载完成后可获取文件路径

### 错误处理

所有 API 返回统一的错误格式：
```json
{
  "detail": "错误信息"
}
```

## 常见问题

### Milvus 连接失败

检查 Milvus 服务是否正常运行：
```bash
curl http://localhost:9091/healthz
```

### 端口冲突

如果默认端口被占用，可以修改 `docker-compose.yml` 或 `docker-compose.lite.yml` 中的端口映射。

### 数据持久化

数据存储在 `./volumes` 目录下，删除容器不会丢失数据。如需清理：
```bash
./milvus.sh clean  # Linux/Mac
milvus.bat clean   # Windows
```
