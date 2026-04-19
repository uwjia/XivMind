# XivMind API Tester

A standalone API testing system for testing all endpoints of the XivMind project.

## Features

- Automatically load all API endpoints from XivMind project
- Display endpoints grouped by modules
- Support GET, POST, PUT, DELETE, PATCH methods
- Support Query, Path, Body parameter input
- JSON Body editor
- Response syntax highlighting
- Copy response content
- Search and filter endpoints

## Running

### Prerequisites
Ensure the XivMind main application is running (default port 8000)

### Start the Testing System

```bash
cd api-tester
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Then visit http://localhost:8001

## Project Structure

```
api-tester/
├── app/
│   ├── main.py              # Main entry
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── proxy.py        # Proxy original project endpoints
│   │   └── schema.py       # Load original project OpenAPI schema
│   └── templates/
│       └── index.html      # Testing interface
├── requirements.txt
├── pyproject.toml
└── README.md
```
