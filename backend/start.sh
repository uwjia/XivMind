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
            echo ""
            echo "WARNING: This will remove the existing virtual environment!"
            read -p "Are you sure you want to continue? (y/N): " CONFIRM
            if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
                echo "Installation cancelled."
                exit 0
            fi
            echo "Removing old virtual environment..."
            rm -rf venv
        fi
        
        echo "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        
        echo "Upgrading pip..."
        pip install --upgrade pip
        
        echo "Installing requirements..."
        pip install -r requirements.txt
        
        echo ""
        echo "Dependencies installed successfully!"
        ;;
    update)
        echo "Updating dependencies..."
        
        if [ ! -d "venv" ]; then
            echo "Virtual environment not found. Please run 'install' first."
            exit 1
        fi
        
        source venv/bin/activate
        
        # Check if pip is available, if not, install it
        if ! python -c "import pip" > /dev/null 2>&1; then
            echo "pip not found in virtual environment. Repairing..."
            curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
            python get-pip.py
            rm get-pip.py
            if [ $? -ne 0 ]; then
                echo "ERROR: Failed to install pip. Please run 'install' to recreate the virtual environment."
                exit 1
            fi
        fi
        
        echo "Upgrading pip..."
        pip install --upgrade pip
        
        echo "Installing/updating packages from requirements.txt..."
        pip install -r requirements.txt
        
        echo ""
        echo "Dependencies updated successfully!"
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
        echo "Usage: $0 {start|stop|restart|install|update|dev|logs|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start backend service (background)"
        echo "  stop    - Stop backend service"
        echo "  restart - Restart backend service"
        echo "  install - Install dependencies (recreates venv)"
        echo "  update  - Update dependencies (keeps existing venv)"
        echo "  dev     - Start in development mode (foreground with reload)"
        echo "  logs    - View backend logs"
        echo "  status  - Check service status"
        exit 1
        ;;
esac
