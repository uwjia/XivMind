# XivMind

Built by AI, motivated by humans. The Mind of arXiv.

一个现代化的 arXiv 论文管理应用，支持收藏、下载和 AI 助手功能。

## 功能特性

- 📚 卡片式论文浏览
- 🔍 按类别和日期高级搜索过滤
- 🔖 收藏论文以便稍后阅读
- 📥 下载 PDF 并跟踪进度
- 🤖 AI 助手解答论文相关问题
- 🌙 深色/浅色主题切换
- 📱 响应式设计
- 🎨 现代化 UI 和流畅动画

## 技术栈

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **Vue Router** - Vue.js 官方路由
- **Pinia** - 状态管理库
- **TypeScript** - 类型安全的 JavaScript
- **Markdown-it** - 支持 LaTeX 的 Markdown 渲染

### 后端
- **FastAPI** - 现代 Python Web 框架
- **SQLite** - 轻量级数据库（默认，无需 Docker）
- **Milvus** - 向量数据库（可选，用于生产环境）
- **WebSocket** - 实时下载进度更新

## 快速开始

### 环境要求

#### SQLite 模式（推荐开发使用）
- Node.js 18+
- Python 3.10+
- 无需 Docker

#### Milvus 模式（推荐生产使用）
- Node.js 18+
- Python 3.10+
- Docker & Docker Compose

### 方式一：SQLite 模式（无需 Docker）

SQLite 模式非常适合开发、测试或独立使用。

**1. 配置后端**

```bash
cd backend
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
start.bat install         # 仅首次安装依赖
start.bat dev             # 开发模式
```

**Linux/Mac:**
```bash
./start.sh install        # 仅首次安装依赖
./start.sh dev            # 开发模式
```

**3. 启动前端**

```bash
npm install
npm run dev
```

### 方式二：Milvus 模式（生产环境）

Milvus 模式提供更好的扩展性和向量搜索能力。

**1. 启动 Milvus 数据库**

**Windows:**
```cmd
cd backend
milvus.bat start          # 标准模式
milvus.bat start lite     # 精简模式（内存占用更少）
```

**Linux/Mac:**
```bash
cd backend
chmod +x milvus.sh
./milvus.sh start         # 标准模式
./milvus.sh start lite    # 精简模式
```

**2. 配置并启动后端**

```bash
cd backend
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

**Windows:**
```cmd
start.bat install         # 仅首次安装依赖
start.bat start           # 启动服务
```

**Linux/Mac:**
```bash
./start.sh install        # 仅首次安装依赖
./start.sh start          # 启动服务
```

**3. 启动前端**

```bash
npm install
npm run dev
```

应用将在 `http://localhost:5173` 可用

## 数据库对比

| 特性 | SQLite | Milvus |
|------|--------|--------|
| 安装配置 | 无需配置 | 需要 Docker |
| 内存占用 | 极小 | ~1-2GB |
| 向量搜索 | 不支持 | 支持 |
| 扩展性 | 单机 | 分布式 |
| 适用场景 | 开发、独立使用 | 生产环境 |

## 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | http://localhost:5173 | Vue 应用 |
| API 文档 | http://localhost:8000/docs | Swagger UI |
| API 文档 | http://localhost:8000/redoc | ReDoc |
| Attu | http://localhost:3000 | Milvus GUI（仅 Milvus 模式） |

## 功能概览

### 首页
- 来自 arXiv 的最新论文
- 类别和日期过滤器
- 论文卡片支持收藏/下载操作
- 详细/简洁卡片视图切换

### 论文详情页
- 完整论文信息，支持 LaTeX 渲染
- 收藏和下载操作
- 下载状态指示器
- 相关论文推荐

### 收藏页面
- 查看所有收藏的论文
- 在收藏中搜索
- 下载或移除收藏
- 下载状态指示器

### 下载页面
- 查看所有下载任务
- 通过 WebSocket 实时跟踪进度
- 打开已下载的文件
- 重试失败的下载

### AI 助手页面
- 询问论文相关问题
- 获取摘要和见解
- LLM 集成占位符

### 设置页面
- 主题配置
- 应用偏好设置

### 数据管理页面
- 年度日历视图，按月展示概览
- 月度详细视图，逐日显示统计
- 统计面板显示总存储天数、论文数及年度分布
- 从 arXiv 获取指定日期的论文
- 清除指定日期的缓存
- 可视化状态指示器（已存储、获取中、无论文、未来日期）
- 点击已存储日期跳转到论文列表

## API 接口

### arXiv `/api/arxiv`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/query` | 按日期查询论文，支持类别过滤 |
| GET | `/paper/{paper_id}` | 按 ID 获取论文 |
| POST | `/fetch/{date}` | 获取指定日期的论文 |
| DELETE | `/cache/{date}` | 清除指定日期的缓存 |
| DELETE | `/cache` | 清除所有日期索引缓存 |
| GET | `/indexes` | 获取所有日期索引 |
| GET | `/statistics` | 获取存储统计 |

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

## 开发

### 前端

```bash
npm run dev          # 开发服务器
npm run build        # 生产构建
npm run preview      # 预览生产构建
npm run storybook    # 组件开发
```

### 后端

```bash
cd backend
start.bat dev        # Windows - 开发模式
./start.sh dev       # Linux/Mac - 开发模式
```

## Schema 升级

查看 [backend/SCHEMA_UPGRADE.md](backend/SCHEMA_UPGRADE.md) 了解数据库 schema 升级说明。

## 许可证

MIT
