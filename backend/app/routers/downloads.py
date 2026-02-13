from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from app.models import (
    DownloadTaskCreate,
    DownloadTaskResponse,
    DownloadTaskListResponse,
    MessageResponse,
    DownloadStatus,
)
from app.services import download_service
from app.download_manager import download_manager
import json
import subprocess
import platform
import os

router = APIRouter(prefix="/downloads", tags=["downloads"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


ws_manager = ConnectionManager()


async def progress_callback(task_id: str, progress: int, status: str):
    await ws_manager.broadcast({
        "type": "progress",
        "task_id": task_id,
        "progress": progress,
        "status": status,
    })


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "subscribe":
                    task_id = message.get("task_id")
                    if task_id:
                        download_manager.add_progress_callback(task_id, progress_callback)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


@router.post("", response_model=DownloadTaskResponse)
async def create_download_task(task: DownloadTaskCreate):
    try:
        existing_tasks, _ = download_service.get_all_tasks(limit=1000)
        for existing in existing_tasks:
            if existing["paper_id"] == task.paper_id and existing["status"] in [
                DownloadStatus.PENDING.value,
                DownloadStatus.DOWNLOADING.value,
            ]:
                return existing

        result = download_service.create_task(task.model_dump())
        
        await download_manager.start_download(
            result["id"],
            task.pdf_url,
            task.paper_id,
        )
        download_manager.add_progress_callback(result["id"], progress_callback)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=DownloadTaskListResponse)
async def get_download_tasks(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    try:
        items, total = download_service.get_all_tasks(limit=limit, offset=offset)
        return DownloadTaskListResponse(total=total, items=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=DownloadTaskResponse)
async def get_download_task(task_id: str):
    try:
        result = download_service.get_task(task_id)
        if not result:
            raise HTTPException(status_code=404, detail="Task not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{task_id}", response_model=MessageResponse)
async def delete_download_task(task_id: str):
    try:
        if download_manager.is_task_running(task_id):
            await download_manager.cancel_download(task_id)
        download_service.delete_task(task_id)
        return MessageResponse(message="Download task deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/retry", response_model=DownloadTaskResponse)
async def retry_download_task(task_id: str):
    try:
        task = download_service.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        success = await download_manager.retry_download(task_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to retry download")
        
        download_manager.add_progress_callback(task_id, progress_callback)
        
        return download_service.get_task(task_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/cancel", response_model=DownloadTaskResponse)
async def cancel_download_task(task_id: str):
    try:
        success = await download_manager.cancel_download(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found or not running")
        
        return download_service.get_task(task_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/running")
async def get_running_status():
    return {
        "running_count": download_manager.get_running_count(),
        "running_tasks": [
            {
                "task_id": task_id,
                "paper_id": download_manager.get_task(task_id).paper_id if download_manager.get_task(task_id) else None,
            }
            for task_id in download_manager._running_tasks.keys()
        ]
    }


@router.post("/{task_id}/open", response_model=MessageResponse)
async def open_download_file(task_id: str):
    try:
        task = download_service.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        file_path = task.get("file_path")
        if not file_path:
            raise HTTPException(status_code=404, detail="File path not found")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File does not exist")
        
        system = platform.system()
        if system == "Windows":
            os.startfile(file_path)
        elif system == "Darwin":
            subprocess.run(["open", file_path])
        else:
            subprocess.run(["xdg-open", file_path])
        
        return MessageResponse(message="File opened successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
