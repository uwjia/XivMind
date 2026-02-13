import asyncio
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
import httpx
import aiofiles
from pathlib import Path
import logging

from app.services import download_service
from app.config import get_settings
from app.models import DownloadStatus

logger = logging.getLogger(__name__)


@dataclass
class DownloadTask:
    task_id: str
    pdf_url: str
    paper_id: str
    status: str = DownloadStatus.PENDING.value
    progress: int = 0
    file_path: str = ""
    file_size: int = 0
    error_message: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    cancel_flag: bool = False


class DownloadManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._tasks: Dict[str, DownloadTask] = {}
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()
        self._progress_callbacks: Dict[str, list] = {}
    
    def get_task(self, task_id: str) -> Optional[DownloadTask]:
        return self._tasks.get(task_id)
    
    def get_all_tasks(self) -> list:
        return list(self._tasks.values())
    
    def add_progress_callback(self, task_id: str, callback: Callable):
        if task_id not in self._progress_callbacks:
            self._progress_callbacks[task_id] = []
        self._progress_callbacks[task_id].append(callback)
    
    def remove_progress_callback(self, task_id: str, callback: Callable):
        if task_id in self._progress_callbacks:
            try:
                self._progress_callbacks[task_id].remove(callback)
            except ValueError:
                pass
    
    async def _notify_progress(self, task_id: str, progress: int, status: str):
        if task_id in self._progress_callbacks:
            for callback in self._progress_callbacks[task_id]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(task_id, progress, status)
                    else:
                        callback(task_id, progress, status)
                except Exception as e:
                    logger.error(f"Error in progress callback: {e}")
    
    async def start_download(self, task_id: str, pdf_url: str, paper_id: str) -> bool:
        async with self._lock:
            if task_id in self._running_tasks:
                return False
            
            task = DownloadTask(
                task_id=task_id,
                pdf_url=pdf_url,
                paper_id=paper_id,
                status=DownloadStatus.PENDING.value,
            )
            self._tasks[task_id] = task
            
            async_task = asyncio.create_task(self._download_worker(task))
            self._running_tasks[task_id] = async_task
            
            return True
    
    async def _download_worker(self, task: DownloadTask):
        settings = get_settings()
        download_dir = Path(settings.DOWNLOAD_DIR)
        download_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            task.status = DownloadStatus.DOWNLOADING.value
            task.updated_at = datetime.utcnow().isoformat()
            download_service.update_task_status(task.task_id, status=task.status, progress=0)
            await self._notify_progress(task.task_id, 0, task.status)
            
            async with httpx.AsyncClient(timeout=300.0, follow_redirects=True) as client:
                async with client.stream("GET", task.pdf_url) as response:
                    if response.status_code != 200:
                        raise Exception(f"HTTP {response.status_code}")
                    
                    content_disp = response.headers.get("content-disposition", "")
                    if "filename=" in content_disp:
                        import re
                        match = re.search(r'filename="?([^";\n]+)"?', content_disp)
                        if match:
                            filename = match.group(1)
                        else:
                            filename = f"{task.paper_id}.pdf"
                    else:
                        filename = f"{task.paper_id}.pdf"
                    
                    file_path = download_dir / filename
                    total_size = int(response.headers.get("content-length", 0))
                    downloaded = 0
                    last_progress = 0
                    
                    async with aiofiles.open(file_path, "wb") as f:
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            if task.cancel_flag:
                                raise Exception("Download cancelled")
                            
                            await f.write(chunk)
                            downloaded += len(chunk)
                            
                            if total_size > 0:
                                progress = int((downloaded / total_size) * 100)
                                if progress != last_progress:
                                    last_progress = progress
                                    task.progress = progress
                                    task.updated_at = datetime.utcnow().isoformat()
                                    
                                    if progress % 5 == 0 or progress == 100:
                                        download_service.update_task_status(task.task_id, status=task.status, progress=progress)
                                    
                                    await self._notify_progress(task.task_id, progress, task.status)
            
            task.status = DownloadStatus.COMPLETED.value
            task.progress = 100
            task.file_path = str(file_path)
            task.file_size = downloaded
            task.updated_at = datetime.utcnow().isoformat()
            download_service.update_task_status(
                task.task_id, 
                status=task.status, 
                progress=100,
                file_path=task.file_path,
                file_size=task.file_size
            )
            await self._notify_progress(task.task_id, 100, task.status)
            logger.info(f"Download completed: {task.paper_id} ({task.file_size} bytes)")
            
        except Exception as e:
            task.status = DownloadStatus.FAILED.value
            task.error_message = str(e)
            task.updated_at = datetime.utcnow().isoformat()
            download_service.update_task_status(
                task.task_id, 
                status=task.status, 
                error_message=task.error_message
            )
            await self._notify_progress(task.task_id, task.progress, task.status)
            logger.error(f"Download failed: {task.paper_id} - {e}")
        
        finally:
            async with self._lock:
                if task.task_id in self._running_tasks:
                    del self._running_tasks[task.task_id]
    
    async def cancel_download(self, task_id: str) -> bool:
        async with self._lock:
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            task.cancel_flag = True
            task.status = DownloadStatus.FAILED.value
            task.error_message = "Download cancelled by user"
            task.updated_at = datetime.utcnow().isoformat()
            
            download_service.update_task_status(
                task_id, 
                status=task.status, 
                error_message=task.error_message
            )
            
            return True
    
    async def retry_download(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task:
            db_task = download_service.get_task(task_id)
            if not db_task:
                return False
            task = DownloadTask(
                task_id=task_id,
                pdf_url=db_task["pdf_url"],
                paper_id=db_task["paper_id"],
            )
            self._tasks[task_id] = task
        
        task.status = DownloadStatus.PENDING.value
        task.progress = 0
        task.error_message = ""
        task.cancel_flag = False
        task.updated_at = datetime.utcnow().isoformat()
        
        download_service.update_task_status(
            task_id, 
            status=task.status, 
            progress=0,
            error_message=""
        )
        
        return await self.start_download(task_id, task.pdf_url, task.paper_id)
    
    def is_task_running(self, task_id: str) -> bool:
        return task_id in self._running_tasks
    
    def get_running_count(self) -> int:
        return len(self._running_tasks)
    
    async def load_pending_tasks(self):
        tasks, _ = download_service.get_all_tasks(limit=1000)
        for task_data in tasks:
            if task_data["status"] in [DownloadStatus.PENDING.value, DownloadStatus.DOWNLOADING.value]:
                task = DownloadTask(
                    task_id=task_data["id"],
                    pdf_url=task_data["pdf_url"],
                    paper_id=task_data["paper_id"],
                    status=DownloadStatus.PENDING.value,
                )
                self._tasks[task_data["id"]] = task
                await self.start_download(task_data["id"], task_data["pdf_url"], task_data["paper_id"])


download_manager = DownloadManager()
