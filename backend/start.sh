#!/bin/bash

echo "=========================================="
echo "  XivMind Backend Service"
echo "=========================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "$1" in
    start)
        echo "Starting backend service..."
        if [ ! -d "venv" ]; then
            echo "Virtual environment not found. Creating..."
            python3 -m venv venv
            source venv/bin/activate
            pip install -r requirements.txt
        else
            source venv/bin/activate
        fi
        echo "Starting uvicorn server..."
        nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
        echo $! > backend.pid
        echo ""
        echo "Backend service started!"
        echo "  - API Docs: http://localhost:8000/docs"
        echo "  - ReDoc: http://localhost:8000/redoc"
        echo "  - Log file: logs/backend.log"
        ;;
    stop)
        echo "Stopping backend service..."
        if [ -f "backend.pid" ]; then
            kill $(cat backend.pid) 2>/dev/null
            rm backend.pid
            echo "Backend service stopped."
        else
            echo "No PID file found. Trying to kill by port..."
            lsof -ti:8000 | xargs kill -9 2>/dev/null
            echo "Backend service stopped."
        fi
        ;;
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    install)
        echo "Installing dependencies..."
        if [ -d "venv" ]; then
            source venv/bin/activate
        fi
        pip install -r requirements.txt
        echo "Dependencies installed."
        ;;
    dev)
        echo "Starting backend in development mode..."
        if [ -d "venv" ]; then
            source venv/bin/activate
        fi
        uvicorn app.main:app --reload --port 8000
        ;;
    logs)
        if [ -f "logs/backend.log" ]; then
            tail -f logs/backend.log
        else
            echo "Log file not found."
        fi
        ;;
    status)
        if [ -f "backend.pid" ]; then
            PID=$(cat backend.pid)
            if ps -p $PID > /dev/null 2>&1; then
                echo "Backend service is running (PID: $PID)"
            else
                echo "Backend service is not running (stale PID file)"
            fi
        else
            echo "Backend service is not running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|install|dev|logs|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start backend service (background)"
        echo "  stop    - Stop backend service"
        echo "  restart - Restart backend service"
        echo "  install - Install dependencies"
        echo "  dev     - Start in development mode (foreground with reload)"
        echo "  logs    - View backend logs"
        echo "  status  - Check service status"
        exit 1
        ;;
esac
