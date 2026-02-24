# XivMind

**English** | [中文](README_CN.md)

Built by AI, motivated by humans. The Mind of arXiv.

A modern arXiv paper management application with bookmark, download, and AI assistant features.

## Features

- 📚 Paper browsing with card-based layout
- 🔍 Advanced search and filtering by category and date
- 🔖 Bookmark papers for later reading
- 📥 Download PDFs with progress tracking
- 🕸️ Knowledge Graph visualization for daily papers
  - Discover relationships between papers
  - Identify research clusters and trends
  - Multiple layout options: force-directed, circular, hierarchical
  - Interactive node exploration with similarity filtering
- 🤖 AI Assistant for paper-related questions
  - Multiple LLM providers: OpenAI, Anthropic, GLM (Zhipu AI), Ollama (local)
  - Semantic search across papers
  - Q&A with context from your paper library
  - Dynamic Skills system with customizable tasks
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
- **Storybook** - Component development and documentation

### Backend
- **FastAPI** - Modern Python web framework
- **SQLite** - Lightweight database (default, no Docker required)
- **Milvus** - Vector database (optional, for production)
- **WebSocket** - Real-time download progress updates

## Quick Start

### Prerequisites

#### SQLite Mode (Recommended for Development)
- Node.js 18+
- Python 3.10+
- No Docker required

#### Milvus Mode (Recommended for Production)
- Node.js 18+
- Python 3.10+
- Docker & Docker Compose

### Option 1: SQLite Mode (No Docker Required)

SQLite mode is perfect for development, testing, or standalone use.

**1. Configure Backend**

```bash
cd backend
cp .env.example .env
```

Edit `.env` file:

```env
DATABASE_TYPE=sqlite
SQLITE_DB_PATH=./data/xivmind.db
DOWNLOAD_DIR=./downloads
```

**2. Start Backend Service**

**Windows:**
```cmd
start.bat install         # First time only
start.bat dev             # Development mode
```

**Linux/Mac:**
```bash
./start.sh install        # First time only
./start.sh dev            # Development mode
```

**3. Start Frontend**

```bash
npm install
npm run dev
```

### Option 2: Milvus Mode (Production)

Milvus mode provides better scalability and vector search capabilities.

**1. Start Milvus Database**

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

**2. Configure and Start Backend**

```bash
cd backend
cp .env.example .env
```

Edit `.env` file:

```env
DATABASE_TYPE=milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
DATABASE_NAME=xivmind
DOWNLOAD_DIR=./downloads
```

**Windows:**
```cmd
start.bat install         # First time only
start.bat start           # Start service
```

**Linux/Mac:**
```bash
./start.sh install        # First time only
./start.sh start          # Start service
```

**3. Start Frontend**

```bash
npm install
npm run dev
```

The application will be available at `http://localhost:5173`

## AI Assistant Configuration

The AI Assistant supports multiple LLM providers. Configure in **Settings** page or `.env` file:

### OpenAI

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your-api-key
```

### Anthropic

```env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-haiku-20240307
ANTHROPIC_API_KEY=your-api-key
```

### GLM (Zhipu AI)

```env
LLM_PROVIDER=glm
LLM_MODEL=glm-4-plus
GLM_API_KEY=your-zhipu-api-key
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

Get your API key from: https://open.bigmodel.cn

### Ollama (Local LLM)

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

Install Ollama from: https://ollama.ai

```bash
# Install a model
ollama pull llama3
ollama pull mistral
ollama pull qwen2
```

## Database Comparison

| Feature | SQLite | Milvus |
|---------|--------|--------|
| Setup | No setup required | Requires Docker |
| Memory | Minimal | ~1-2GB |
| Vector Search | Not supported | Supported |
| Scalability | Single machine | Distributed |
| Use Case | Development, standalone | Production |

## Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | Vue application |
| API Docs | http://localhost:8000/docs | Swagger UI |
| API Docs | http://localhost:8000/redoc | ReDoc |
| Attu | http://localhost:3000 | Milvus GUI (Milvus mode only) |
| Storybook | http://localhost:6006 | Component documentation |

## Features Overview

### Home Page
- Latest papers from arXiv
- Category and date filters
- Paper cards with bookmark/download actions
- Toggle between detailed and simple card views
- Knowledge Graph view for visualizing paper relationships

### Knowledge Graph
- Visualize paper relationships based on semantic similarity
- Identify research clusters and trending topics
- Interactive exploration with node click for details
- Adjustable similarity threshold for edge filtering
- Multiple layout algorithms: force-directed, circular, hierarchical
- Category-based filtering and node coloring
- Statistics panel showing total papers, connections, and top categories

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
- **Search Mode**: Semantic search across your paper library
- **Ask Mode**: Ask questions with context from your papers
- **Skills Mode**: Execute specific tasks on papers
  - Built-in Skills: Paper Summary, Translation, Citation Generator, Related Papers
  - Dynamic Skills: Custom skills loaded from SKILL.md files
  - Create your own skills with customizable prompts
- Message history preserved per mode
- Copy and retry functionality
- Multiple LLM provider support with easy switching in Settings

### Settings Page
- Theme configuration (Dark/Light)
- LLM Provider configuration
  - Select provider and model
  - Configure API keys
  - Test connection status
- Application preferences

### Data Manager Page
- Yearly calendar view with monthly overview
- Monthly detailed view with day-by-day statistics
- Statistics panel showing total stored days, papers, and yearly breakdown
- Fetch papers for specific dates from arXiv
- Clear cache for specific dates
- Visual status indicators (Stored, Fetching, No Papers, Future)
- Navigate to paper list by clicking on stored dates

## Skills System

XivMind features a powerful Skills system that allows you to perform various tasks on papers.

### Built-in Skills
- **Paper Summary**: Generate concise summaries highlighting key contributions
- **Translation**: Translate paper content to multiple languages (Chinese, Japanese, German, French, Spanish)
- **Citation Generator**: Generate citations in APA, MLA, BibTeX, IEEE formats
- **Related Papers**: Find similar papers in your library

### Dynamic Skills
Create custom skills by adding `SKILL.md` files in `backend/skills/` directory:

```markdown
---
name: my-custom-skill
description: My custom skill description
icon: file-text
category: analysis
requires_paper: true
metadata:
  xivmind:
    input_schema:
      type: object
      properties:
        param1:
          type: string
          description: Parameter description
          default: "default_value"
---

# My Custom Skill

Your prompt template here with {paper.title} and {paper.abstract} placeholders.
```

## API Endpoints

### arXiv `/api/arxiv`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/query` | Query papers by date with optional category filter |
| GET | `/paper/{paper_id}` | Get paper by ID |
| POST | `/fetch/{date}` | Fetch papers for a specific date |
| DELETE | `/cache/{date}` | Clear cache for a specific date |
| DELETE | `/cache` | Clear all date index cache |
| GET | `/indexes` | Get all date indexes |
| GET | `/statistics` | Get storage statistics |
| GET | `/search/semantic` | Semantic search across papers |
| POST | `/ask` | Ask question with paper context |
| GET | `/llm/providers` | Get available LLM providers |
| GET | `/llm/ollama/status` | Check Ollama service status |

### Bookmarks `/api/bookmarks`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/` | Add bookmark |
| DELETE | `/{paper_id}` | Remove bookmark |
| GET | `/check/{paper_id}` | Check if bookmarked |
| GET | `/` | Get bookmark list |
| GET | `/search` | Search bookmarks |

### Skills `/api/skills`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Get all available skills |
| GET | `/categories` | Get skills grouped by category |
| GET | `/{skill_id}` | Get a specific skill |
| POST | `/{skill_id}/execute` | Execute a skill with paper IDs |
| POST | `/reload` | Reload all dynamic skills |
| POST | `/reload/{skill_id}` | Reload a specific skill |

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

### Graph `/api/graph`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/{date}` | Get knowledge graph data for a specific date |
| GET | `/similarity/{date}` | Get paper similarity matrix for a date |

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

## Component Development

XivMind uses Storybook for component development and documentation:

```bash
npm run storybook
```

Access at http://localhost:6006

Available component categories:
- **PaperCard** - Paper display components
- **Graph** - KnowledgeGraph, GraphControls, GraphLegend, GraphStatistics components
- **Skills** - SkillCard, SkillForm components
- **UI Components** - Buttons, dialogs, tooltips, etc.

## Schema Upgrades

See [backend/SCHEMA_UPGRADE.md](backend/SCHEMA_UPGRADE.md) for database schema upgrade instructions.

## License

MIT
