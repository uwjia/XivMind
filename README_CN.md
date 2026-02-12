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
- **Milvus** - 向量数据库用于数据存储
- **WebSocket** - 实时下载进度更新

## 项目结构

```
XivMind/
├── src/                      # 前端源码
│   ├── components/           # 可复用组件
│   │   ├── Header.vue
│   │   ├── Sidebar.vue
│   │   ├── PaperCard.vue
│   │   ├── CategoryPicker.vue
│   │   └── Toast.vue
│   ├── views/               # 页面组件
│   │   ├── Home.vue
│   │   ├── Search.vue
│   │   ├── PaperDetail.vue
│   │   ├── Bookmarks.vue
│   │   ├── Downloads.vue
│   │   ├── Assistant.vue
│   │   └── Settings.vue
│   ├── stores/              # Pinia 状态管理
│   │   ├── paper-store.ts
│   │   ├── bookmark-store.ts
│   │   ├── download-store.ts
│   │   └── theme-store.ts
│   ├── services/            # API 服务
│   │   └── api.ts
│   ├── utils/               # 工具函数
│   │   └── categoryColors.ts
│   └── router/              # Vue Router 配置
│       └── index.ts
├── backend/                 # 后端源码
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── config.py        # 配置管理
│   │   ├── models.py        # Pydantic 模型
│   │   ├── database.py      # Milvus 服务
│   │   ├── download_manager.py
│   │   └── routers/
│   │       ├── bookmarks.py
│   │       └── downloads.py
│   ├── downloads/           # 下载的 PDF
│   ├── logs/               # 应用日志
│   ├── docker-compose.yml  # Milvus 标准部署
│   ├── docker-compose.lite.yml  # Milvus 精简部署
│   └── requirements.txt
└── package.json
```

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.10+
- Docker & Docker Compose

### 1. 启动 Milvus 数据库

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

### 2. 启动后端服务

**Windows:**
```cmd
cd backend
start.bat install         # 仅首次安装依赖
start.bat start           # 启动服务
```

**Linux/Mac:**
```bash
cd backend
./start.sh install        # 仅首次安装依赖
./start.sh start          # 启动服务
```

### 3. 启动前端

```bash
npm install
npm run dev
```

应用将在 `http://localhost:5173` 可用

## 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | http://localhost:5173 | Vue 应用 |
| API 文档 | http://localhost:8000/docs | Swagger UI |
| API 文档 | http://localhost:8000/redoc | ReDoc |
| Attu | http://localhost:3000 | Milvus GUI |

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
