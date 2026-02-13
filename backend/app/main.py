from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.staticfiles import StaticFiles
from app.routers import bookmarks, downloads
from app.database import milvus_service, download_service
from app.download_manager import download_manager
from contextlib import asynccontextmanager
import os
import logging
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logging.getLogger("pymilvus").setLevel(logging.WARNING)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting application lifespan...")
    try:
        logging.info("Creating Milvus collections...")
        milvus_service.create_collections()
        logging.info("Milvus collections created successfully")
    except ConnectionError as e:
        logging.error(f"Failed to start application: {e}")
        logging.error("Exiting...")
        import os
        os._exit(1)
    except Exception as e:
        logging.error(f"Unexpected error during startup: {e}")
        import os
        os._exit(1)
    logging.info("Resetting incomplete download tasks...")
    reset_count = download_service.reset_incomplete_tasks()
    if reset_count > 0:
        logging.info(f"Reset {reset_count} incomplete download tasks to failed status")
    logging.info("Application startup complete")
    yield


app = FastAPI(
    title="XivMind API",
    description="Backend API for XivMind - Paper Management System",
    version="1.0.0",
    lifespan=lifespan,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(bookmarks.router, prefix="/api")
app.include_router(downloads.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "XivMind API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )
