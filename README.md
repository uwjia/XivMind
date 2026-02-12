# XivMind

Built by AI, motivated by humans. The Mind of arXiv.

A modern arXiv paper management application with bookmark, download, and AI assistant features.

## Features

- 📚 Paper browsing with card-based layout
- 🔍 Advanced search and filtering by category and date
- 🔖 Bookmark papers for later reading
- 📥 Download PDFs with progress tracking
- 🤖 AI Assistant for paper-related questions
- 🌙 Dark/Light theme toggle
- 📱 Responsive design
- 🎨 Modern UI with smooth animations

## Tech Stack

### Frontend
- **Vue 3** - Progressive JavaScript framework
- **Vite** - Next generation frontend tooling
- **Vue Router** - Official router for Vue.js
- **Pinia** - State management library
- **TypeScript** - Type-safe JavaScript
- **Markdown-it** - Markdown rendering with LaTeX support

### Backend
- **FastAPI** - Modern Python web framework
- **Milvus** - Vector database for data storage
- **WebSocket** - Real-time download progress updates

## Project Structure

```
XivMind/
├── src/                      # Frontend source
│   ├── components/           # Reusable components
│   │   ├── Header.vue
│   │   ├── Sidebar.vue
│   │   ├── PaperCard.vue
│   │   ├── CategoryPicker.vue
│   │   └── Toast.vue
│   ├── views/               # Page components
│   │   ├── Home.vue
│   │   ├── Search.vue
│   │   ├── PaperDetail.vue
│   │   ├── Bookmarks.vue
│   │   ├── Downloads.vue
│   │   ├── Assistant.vue
│   │   └── Settings.vue
│   ├── stores/              # Pinia stores
│   │   ├── paper-store.ts
│   │   ├── bookmark-store.ts
│   │   ├── download-store.ts
│   │   └── theme-store.ts
│   ├── services/            # API services
│   │   └── api.ts
│   ├── utils/               # Utility functions
│   │   └── categoryColors.ts
│   └── router/              # Vue Router configuration
│       └── index.ts
├── backend/                 # Backend source
│   ├── app/
│   │   ├── main.py          # FastAPI entry
│   │   ├── config.py        # Configuration
│   │   ├── models.py        # Pydantic models
│   │   ├── database.py      # Milvus service
│   │   ├── download_manager.py
│   │   └── routers/
│   │       ├── bookmarks.py
│   │       └── downloads.py
│   ├── downloads/           # Downloaded PDFs
│   ├── logs/               # Application logs
│   ├── docker-compose.yml  # Milvus standard
│   ├── docker-compose.lite.yml  # Milvus lite
│   └── requirements.txt
└── package.json
```

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- Docker & Docker Compose

### 1. Start Milvus Database

**Windows:**
```cmd
cd backend
milvus.bat start          # Standard mode
milvus.bat start lite     # Lite mode (less memory)
```

**Linux/Mac:**
```bash
cd backend
chmod +x milvus.sh
./milvus.sh start         # Standard mode
./milvus.sh start lite    # Lite mode
```

### 2. Start Backend Service

**Windows:**
```cmd
cd backend
start.bat install         # First time only
start.bat start           # Start service
```

**Linux/Mac:**
```bash
cd backend
./start.sh install        # First time only
./start.sh start          # Start service
```

### 3. Start Frontend

```bash
npm install
npm run dev
```

The application will be available at `http://localhost:5173`

## Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | Vue application |
| API Docs | http://localhost:8000/docs | Swagger UI |
| API Docs | http://localhost:8000/redoc | ReDoc |
| Attu | http://localhost:3000 | Milvus GUI |

## Features Overview

### Home Page
- Latest papers from arXiv
- Category and date filters
- Paper cards with bookmark/download actions
- Toggle between detailed and simple card views

### Paper Detail Page
- Full paper information with LaTeX rendering
- Bookmark and download actions
- Download status indicator
- Related papers section

### Bookmarks Page
- View all bookmarked papers
- Search within bookmarks
- Download or remove bookmarks
- Download status indicators

### Downloads Page
- View all download tasks
- Real-time progress tracking via WebSocket
- Open downloaded files
- Retry failed downloads

### AI Assistant Page
- Ask questions about papers
- Get summaries and insights
- Placeholder for LLM integration

### Settings Page
- Theme configuration
- Application preferences

## API Endpoints

### Bookmarks `/api/bookmarks`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/` | Add bookmark |
| DELETE | `/{paper_id}` | Remove bookmark |
| GET | `/check/{paper_id}` | Check if bookmarked |
| GET | `/` | Get bookmark list |
| GET | `/search` | Search bookmarks |

### Downloads `/api/downloads`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/` | Create download task |
| GET | `/` | Get task list |
| GET | `/{task_id}` | Get task details |
| DELETE | `/{task_id}` | Delete task |
| POST | `/{task_id}/retry` | Retry failed task |
| POST | `/{task_id}/cancel` | Cancel task |
| POST | `/{task_id}/open` | Open downloaded file |
| WebSocket | `/ws` | Real-time progress |

## Development

### Frontend

```bash
npm run dev          # Development server
npm run build        # Production build
npm run preview      # Preview production build
npm run storybook    # Component development
```

### Backend

```bash
cd backend
start.bat dev        # Windows - Development mode
./start.sh dev       # Linux/Mac - Development mode
```

## Schema Upgrades

See [backend/SCHEMA_UPGRADE.md](backend/SCHEMA_UPGRADE.md) for database schema upgrade instructions.

## License

MIT
