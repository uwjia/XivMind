#!/bin/bash

echo "=========================================="
echo "  XivMind - Milvus Docker Deployment"
echo "=========================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MODE="${2:-standard}"
COMPOSE_FILE="docker-compose.yml"

if [ "$MODE" = "lite" ]; then
    COMPOSE_FILE="docker-compose.lite.yml"
fi

case "$1" in
    start)
        echo "Starting Milvus services ($COMPOSE_FILE)..."
        docker-compose -f "$COMPOSE_FILE" up -d
        echo ""
        echo "Milvus is starting..."
        echo "  - Milvus: http://localhost:19530"
        echo "  - Attu (GUI): http://localhost:3000"
        if [ "$MODE" != "lite" ]; then
            echo "  - MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"
        fi
        echo ""
        echo "Waiting for Milvus to be ready..."
        sleep 10
        until curl -s http://localhost:9091/healthz > /dev/null 2>&1; do
            echo "Still waiting..."
            sleep 5
        done
        echo "Milvus is ready!"
        ;;
    stop)
        echo "Stopping Milvus services..."
        docker-compose -f docker-compose.yml down 2>/dev/null
        docker-compose -f docker-compose.lite.yml down 2>/dev/null
        echo "Milvus services stopped."
        ;;
    restart)
        echo "Restarting Milvus services..."
        docker-compose -f docker-compose.yml down 2>/dev/null
        docker-compose -f docker-compose.lite.yml down 2>/dev/null
        docker-compose -f "$COMPOSE_FILE" up -d
        echo "Milvus services restarted."
        ;;
    status)
        docker-compose -f docker-compose.yml ps 2>/dev/null
        docker-compose -f docker-compose.lite.yml ps 2>/dev/null
        ;;
    logs)
        if [ -d "volumes/milvus-lite" ]; then
            docker-compose -f docker-compose.lite.yml logs -f "${2:-standalone}"
        else
            docker-compose -f docker-compose.yml logs -f "${2:-standalone}"
        fi
        ;;
    clean)
        echo "WARNING: This will delete all data!"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose -f docker-compose.yml down -v 2>/dev/null
            docker-compose -f docker-compose.lite.yml down -v 2>/dev/null
            rm -rf volumes
            echo "All data cleaned."
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|clean} [lite]"
        echo ""
        echo "Commands:"
        echo "  start [lite]   - Start Milvus services (lite = embedded mode)"
        echo "  stop           - Stop Milvus services"
        echo "  restart [lite] - Restart Milvus services"
        echo "  status         - Show service status"
        echo "  logs [service] - Show logs"
        echo "  clean          - Remove all data (WARNING: destructive)"
        echo ""
        echo "Modes:"
        echo "  (default)      - Standard mode with separate etcd, MinIO containers"
        echo "  lite           - Embedded mode (etcd/MinIO embedded in Milvus)"
        exit 1
        ;;
esac
