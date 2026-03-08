"""
XivMind Standalone Entry Point
Standalone entry file for PyInstaller packaging
Supports both local and Docker environments
"""
import sys
import builtins

class _DummyObj:
    pass

builtins.obj = _DummyObj

import os
from pathlib import Path
import logging
import webbrowser
import threading
import time
import signal

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def is_docker() -> bool:
    """
    Detect if running inside Docker container
    
    Returns:
        True if running in Docker, False otherwise
    """
    return (
        os.path.exists('/.dockerenv') or
        os.path.exists('/run/.containerenv') or
        os.environ.get('XIVMIND_DOCKER', '').lower() == 'true' or
        os.path.exists('/app/.dockerenv')
    )


def resource_path(relative_path: str) -> str:
    """
    Get the real path of resource files, supporting both development and packaged modes
    
    Args:
        relative_path: Relative path
        
    Returns:
        Absolute path
    """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(sys.executable)
        internal_path = os.path.join(base_path, "_internal")
        if os.path.exists(internal_path):
            base_path = internal_path
        else:
            base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def get_data_dir() -> Path:
    """
    Get user data directory
    
    In Docker, uses /app/data by default.
    In local environment, uses platform-specific user data directory.
    
    Returns:
        User data directory path
    """
    if is_docker():
        data_dir = Path(os.environ.get("XIVMIND_DATA_DIR", "/app/data"))
    elif sys.platform == "win32":
        data_dir = Path(os.environ.get("APPDATA", ".")) / "XivMind"
    elif sys.platform == "darwin":
        data_dir = Path.home() / "Library" / "Application Support" / "XivMind"
    else:
        data_dir = Path.home() / ".xivmind"
    
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_models_cache_dir() -> Path:
    """
    Get model cache directory
    
    Returns:
        Model cache directory path
    """
    models_dir = get_data_dir() / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir


def setup_environment():
    """
    Configure environment variables
    
    In Docker, respects existing environment variables.
    In local environment, sets up default paths.
    """
    data_dir = get_data_dir()
    models_dir = get_models_cache_dir()
    
    if is_docker():
        if "DATABASE_TYPE" not in os.environ:
            os.environ["DATABASE_TYPE"] = os.environ.get("DATABASE_TYPE", "lancedb")
        if "LANCEDB_PATH" not in os.environ:
            os.environ["LANCEDB_PATH"] = str(data_dir / "lancedb")
        if "DOWNLOAD_DIR" not in os.environ:
            os.environ["DOWNLOAD_DIR"] = str(data_dir / "downloads")
        if "XIVMIND_MODELS_CACHE" not in os.environ:
            os.environ["XIVMIND_MODELS_CACHE"] = str(models_dir)
        if "SKILLS_DIR" not in os.environ:
            os.environ["SKILLS_DIR"] = os.environ.get("SKILLS_DIR", "/app/skills")
    else:
        os.environ["DATABASE_TYPE"] = "lancedb"
        os.environ["LANCEDB_PATH"] = str(data_dir / "lancedb")
        os.environ["DOWNLOAD_DIR"] = str(data_dir / "downloads")
        os.environ["XIVMIND_MODELS_CACHE"] = str(models_dir)
        os.environ["SKILLS_DIR"] = resource_path("skills")
    
    os.environ["HF_ENDPOINT"] = os.environ.get("HF_ENDPOINT", "https://hf-mirror.com")
    
    os.makedirs(os.environ["LANCEDB_PATH"], exist_ok=True)
    os.makedirs(os.environ["DOWNLOAD_DIR"], exist_ok=True)
    
    logger.info(f"Data directory: {data_dir}")
    logger.info(f"LanceDB path: {os.environ['LANCEDB_PATH']}")
    logger.info(f"Download directory: {os.environ['DOWNLOAD_DIR']}")
    logger.info(f"Models cache: {models_dir}")


def open_browser(url: str, delay: float = 2.0):
    """
    Open browser with delay
    
    Args:
        url: URL to open
        delay: Delay in seconds
    """
    time.sleep(delay)
    logger.info(f"Opening browser: {url}")
    webbrowser.open(url)


class SPAMiddleware:
    """
    Middleware: Provides static file service for SPA applications
    Returns index.html for non-API routes
    """
    
    def __init__(self, app, static_dir: str, index_file: str):
        self.app = app
        self.static_dir = static_dir
        self.index_file = index_file
        self.api_prefixes = ('/api', '/docs', '/openapi', '/health', '/static', '/redoc')
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            path = scope['path']
            
            if not path.startswith(self.api_prefixes):
                file_path = os.path.join(self.static_dir, path.lstrip('/'))
                if os.path.isfile(file_path):
                    from fastapi.responses import FileResponse
                    response = FileResponse(file_path)
                    await response(scope, receive, send)
                    return
                else:
                    if os.path.isfile(self.index_file):
                        from fastapi.responses import FileResponse
                        response = FileResponse(self.index_file)
                        await response(scope, receive, send)
                        return
        
        await self.app(scope, receive, send)


def main():
    """
    Main function
    """
    logger.info("=" * 50)
    logger.info("  XivMind - arXiv Paper Management System")
    logger.info("=" * 50)
    
    _in_docker = is_docker()
    if _in_docker:
        logger.info("Running in Docker mode")
    
    setup_environment()
    
    static_dir = resource_path("static")
    if not os.path.exists(static_dir):
        logger.warning(f"Static directory not found: {static_dir}")
        logger.warning("Frontend files may not be available.")
    else:
        logger.info(f"Static directory: {static_dir}")
    
    try:
        import scipy.stats._distn_infrastructure
        if not hasattr(scipy.stats._distn_infrastructure, 'obj'):
            scipy.stats._distn_infrastructure.obj = _DummyObj
    except Exception as e:
        logger.warning(f"Could not pre-import scipy: {e}")
    
    from fastapi.staticfiles import StaticFiles
    from app.main import app
    
    if os.path.exists(static_dir):
        assets_dir = os.path.join(static_dir, "assets")
        if os.path.exists(assets_dir):
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
            logger.info(f"Static assets mounted from: {assets_dir}")
        
        index_html = os.path.join(static_dir, "index.html")
        if os.path.exists(index_html):
            app.add_middleware(SPAMiddleware, static_dir=static_dir, index_file=index_html)
            logger.info("SPA middleware configured")
    
    import uvicorn
    
    host = "0.0.0.0" if _in_docker else "127.0.0.1"
    port = int(os.environ.get("XIVMIND_PORT", "8000"))
    url = f"http://{'localhost' if _in_docker else host}:{port}"
    
    if not _in_docker:
        browser_thread = threading.Thread(
            target=open_browser,
            args=(url,),
            daemon=True
        )
        browser_thread.start()
    
    logger.info(f"Starting server at {url}")
    logger.info("Press Ctrl+C to stop the server")
    
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=False,
    )


if __name__ == "__main__":
    main()
