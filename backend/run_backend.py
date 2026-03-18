import uvicorn
import os
import sys

print(f"[run_backend.py] APPDATA env at startup: {os.environ.get('APPDATA')}")
print(f"[run_backend.py] DOWNLOAD_DIR env at startup: {os.environ.get('DOWNLOAD_DIR')}")
print(f"[run_backend.py] Current working directory: {os.getcwd()}")

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

print(f"[run_backend.py] application_path: {application_path}")
os.chdir(application_path)

from app.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "localhost")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
