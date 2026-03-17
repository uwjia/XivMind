import uvicorn
import os
import sys

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

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
