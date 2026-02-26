# XivMind Backend 中文文档

[English](README.md)

FastAPI 后端服务，用于论文收藏管理和下载任务管理。支持 Milvus（向量数据库）和 SQLite（轻量级数据库）两种数据库模式。

## 环境要求

### SQLite 模式（推荐开发使用）
- Python 3.10+
- 无需 Docker

### Milvus 模式（推荐生产使用）
- Python 3.10+
- Docker & Docker Compose
- Milvus 2.6.4+

## 快速开始

### 方式一：SQLite 模式（无需 Docker）

SQLite 模式非常适合开发、测试或独立使用，无需外部数据库配置。

**1. 配置环境变量**

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
DATABASE_TYPE=sqlite
SQLITE_DB_PATH=./data/xivmind.db
DOWNLOAD_DIR=./downloads
```

**2. 启动后端服务**

**Windows:**

```cmd
start.bat install   # 安装依赖（首次运行）
start.bat dev       # 开发模式（前台运行，支持热重载）
```

**Linux/Mac:**

```bash
chmod +x start.sh
./start.sh install   # 安装依赖（首次运行）
./start.sh dev       # 开发模式（前台运行，支持热重载）
```

### 方式二：Milvus 模式（生产环境）

Milvus 模式提供更好的扩展性和向量搜索能力，适合生产环境使用。

**1. 启动 Milvus**

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

**2. 配置环境变量**

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
DATABASE_TYPE=milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
DATABASE_NAME=xivmind
DOWNLOAD_DIR=./downloads
```

**3. 启动后端服务**

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

## 数据库对比

| 特性 | SQLite | Milvus |
|------|--------|--------|
| 安装配置 | 无需配置 | 需要 Docker |
| 内存占用 | 极小 | ~1-2GB |
| 向量搜索 | 不支持 | 支持 |
| 扩展性 | 单机 | 分布式 |
| 适用场景 | 开发、独立使用 | 生产环境 |

## 服务组件

### SQLite 模式

| 服务 | 端口 | 说明 |
|------|------|------|
| **FastAPI** | 8000 | 后端 API 服务 |

### Milvus 标准模式

| 服务 | 端口 | 说明 |
|------|------|------|
| **Milvus** | 19530 | 向量数据库 |
| **Attu** | 3000 | Milvus GUI 管理界面 |
| **MinIO** | 9000/9001 | 对象存储 |
| **etcd** | 2379 | 元数据存储 |
| **FastAPI** | 8000 | 后端 API 服务 |

### Milvus 精简模式

| 服务 | 端口 | 说明 |
|------|------|------|
| **Milvus** | 19530 | 向量数据库（内嵌 etcd/MinIO） |
| **Attu** | 3000 | Milvus GUI 管理界面 |
| **FastAPI** | 8000 | 后端 API 服务 |

## 访问地址

- **API 文档 (Swagger)**: http://localhost:8000/docs
- **API 文档 (ReDoc)**: http://localhost:8000/redoc
- **Milvus**（仅 Milvus 模式）: `localhost:19530`
- **Attu GUI**（仅 Milvus 模式）: http://localhost:3000
- **MinIO Console**（仅 Milvus 标准模式）: http://localhost:9001 (用户名/密码: minioadmin/minioadmin)

## API 接口

### arXiv `/api/arxiv`

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/query` | 按日期查询论文，可选分类筛选 |
| GET | `/paper/{paper_id}` | 按 ID 获取论文 |
| POST | `/fetch/{date}` | 获取特定日期的论文 |
| DELETE | `/cache/{date}` | 清除特定日期的缓存 |
| DELETE | `/cache` | 清除所有日期索引缓存 |
| GET | `/indexes` | 获取所有日期索引 |
| GET | `/statistics` | 获取存储统计 |
| GET | `/search/semantic` | 论文语义搜索 |
| POST | `/ask` | 基于论文内容提问 |
| GET | `/llm/providers` | 获取可用的 LLM 提供商 |
| GET | `/llm/ollama/status` | 检查 Ollama 服务状态 |

### 收藏管理 `/api/bookmarks`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/` | 添加收藏 |
| DELETE | `/{paper_id}` | 删除收藏 |
| GET | `/check/{paper_id}` | 检查是否已收藏 |
| GET | `/` | 获取收藏列表 |
| GET | `/search` | 搜索收藏 |

### 技能 `/api/skills`

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/` | 获取所有可用技能 |
| GET | `/categories` | 按类别获取技能 |
| GET | `/{skill_id}` | 获取特定技能 |
| POST | `/{skill_id}/execute` | 执行技能 |
| POST | `/reload` | 重载所有动态技能 |
| POST | `/reload/{skill_id}` | 重载特定技能 |

### SubAgents `/api/subagents`

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/` | 获取所有可用的 SubAgents |
| GET | `/{agent_id}` | 获取特定 SubAgent |
| GET | `/{agent_id}/raw` | 获取原始 AGENT.md 内容 |
| POST | `/{agent_id}/execute` | 执行 SubAgent 任务 |
| POST | `/{agent_id}/reload` | 重载特定 SubAgent |
| POST | `/reload` | 重载所有动态 SubAgents |
| POST | `/` | 创建新的动态 SubAgent |
| PUT | `/{agent_id}` | 更新 SubAgent 的 AGENT.md |
| DELETE | `/{agent_id}` | 删除动态 SubAgent |

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

### 图谱 `/api/graph`

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/{date}` | 获取指定日期的知识图谱数据 |
| GET | `/similarity/{date}` | 获取指定日期的论文相似度矩阵 |

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

- **SQLite**: 数据库文件和表会在启动时自动创建
- **Milvus**: 应用启动时会自动创建以下集合：
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

### Milvus 连接失败（仅 Milvus 模式）

检查 Milvus 服务是否正常运行：

```bash
curl http://localhost:9091/healthz
```

### 端口冲突

如果默认端口被占用，可以修改 `docker-compose.yml` 或 `docker-compose.lite.yml` 中的端口映射。

### 数据持久化

- **SQLite**: 数据存储在 `SQLITE_DB_PATH` 指定的文件中（默认：`./data/xivmind.db`）
- **Milvus**: 数据存储在 `./volumes` 目录下，删除容器不会丢失数据。如需清理：

```bash
./milvus.sh clean  # Linux/Mac
milvus.bat clean   # Windows
```
