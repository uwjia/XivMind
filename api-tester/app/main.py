from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routers import proxy, schema

app = FastAPI(
    title="XivMind API Tester",
    description="API Testing Interface for XivMind",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(proxy.router)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    return """
    <html>
        <head><title>XivMind API Tester</title></head>
        <body>
            <h1>XivMind API Tester</h1>
            <p>Template not found. Please ensure templates/index.html exists.</p>
        </body>
    </html>
    """


@app.get("/api/schema")
async def get_api_schema():
    try:
        raw_schema = await schema.fetch_openapi_schema()
        endpoints = schema.parse_endpoints(raw_schema)
        grouped = schema.group_by_tags(endpoints)
        return {
            "schema": raw_schema,
            "endpoints": endpoints,
            "grouped": grouped,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
