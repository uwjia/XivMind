import os
import re
import logging
from app.db.base import DownloadRepository
from app.db.factory import get_download_repository, get_paper_repository
from app.config import get_settings
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

logger = logging.getLogger(__name__)
settings = get_settings()


class DownloadService:
    def __init__(self, repository: Optional[DownloadRepository] = None):
        self._repository = repository or get_download_repository()
        self._paper_repo = None

    def _get_paper_repo(self):
        if self._paper_repo is None:
            self._paper_repo = get_paper_repository()
        return self._paper_repo

    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._repository.add(task_data)

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self._repository.get(task_id)

    def get_all_tasks(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int, int]:
        tasks, total = self._repository.get_all(limit, offset)
        completed_count = self._repository.count_completed()
        return tasks, total, completed_count

    def delete_task(self, task_id: str) -> bool:
        return self._repository.remove(task_id)

    def update_task_status(
        self,
        task_id: str,
        status: str,
        progress: int = 0,
        file_path: Optional[str] = None,
        file_size: int = 0,
        error_message: Optional[str] = None,
    ) -> bool:
        return self._repository.update_status(
            task_id, status, progress, file_path, file_size, error_message
        )

    def get_task_by_paper_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        return self._repository.get_by_paper_id(paper_id)

    def get_all_tasks_by_paper_id(self, paper_id: str) -> List[Dict[str, Any]]:
        return self._repository.get_all_by_paper_id(paper_id)

    def check_batch(self, paper_ids: List[str]) -> Dict[str, bool]:
        return self._repository.check_batch(paper_ids)

    def reset_incomplete_tasks(self) -> int:
        return self._repository.reset_incomplete_tasks()

    def count_completed(self) -> int:
        return self._repository.count_completed()

    def sync_local_files(self) -> Dict[str, Any]:
        """
        Sync local PDF files from DOWNLOAD_DIR to downloads table.
        Returns dict with added, skipped, errors counts and details.
        """
        download_dir = settings.DOWNLOAD_DIR
        if not os.path.exists(download_dir):
            logger.warning(f"Download directory does not exist: {download_dir}")
            return {"added": 0, "skipped": 0, "errors": 0, "details": []}

        paper_id_pattern = re.compile(r'^(\d{4}\.\d{4,5})(v\d+)?\.pdf$', re.IGNORECASE)
        
        added = 0
        updated = 0
        skipped = 0
        errors = 0
        details = []

        paper_repo = self._get_paper_repo()
        
        for filename in os.listdir(download_dir):
            if not filename.lower().endswith('.pdf'):
                continue
            
            match = paper_id_pattern.match(filename)
            if not match:
                logger.debug(f"Skipping file with non-matching name: {filename}")
                continue
            
            paper_id = match.group(1)
            file_path = os.path.join(download_dir, filename)
            
            existing_task = self._repository.get_by_paper_id(paper_id)
            if existing_task:
                if existing_task.get("status") == "completed":
                    skipped += 1
                    details.append({
                        "paper_id": paper_id,
                        "status": "skipped",
                        "reason": "already_completed",
                        "file_path": file_path
                    })
                    continue
                
                file_size = os.path.getsize(file_path)
                self._repository.update_status(
                    existing_task["id"],
                    "completed",
                    100,
                    file_path,
                    file_size,
                )
                updated += 1
                details.append({
                    "paper_id": paper_id,
                    "status": "updated",
                    "file_path": file_path
                })
                continue
            
            paper = paper_repo.get_paper_by_id(paper_id)
            if not paper:
                errors += 1
                details.append({
                    "paper_id": paper_id,
                    "status": "error",
                    "reason": "paper_not_found",
                    "file_path": file_path
                })
                continue
            
            file_size = os.path.getsize(file_path)
            now = datetime.utcnow().isoformat()
            
            task_data = {
                "paper_id": paper_id,
                "arxiv_id": paper.get("arxiv_id", paper_id),
                "title": paper.get("title", ""),
                "pdf_url": paper.get("pdf_url", f"https://arxiv.org/pdf/{paper_id}"),
                "status": "completed",
                "progress": 100,
                "file_path": file_path,
                "file_size": file_size,
                "created_at": now,
                "updated_at": now,
            }
            
            try:
                self._repository.add(task_data)
                added += 1
                details.append({
                    "paper_id": paper_id,
                    "status": "added",
                    "file_path": file_path
                })
            except Exception as e:
                logger.error(f"Failed to add download record for {paper_id}: {e}")
                errors += 1
                details.append({
                    "paper_id": paper_id,
                    "status": "error",
                    "reason": str(e),
                    "file_path": file_path
                })

        return {
            "added": added,
            "updated": skipped,
            "skipped": skipped,
            "errors": errors,
            "details": details
        }

    def get_incomplete(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get incomplete download tasks (status != 'completed') with pagination.
        """
        return self._repository.get_incomplete(limit, offset)

    def get_missing_files(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get completed download tasks where the local file is missing.
        Paginates through all completed tasks to find missing files.
        Returns paginated results of missing files.
        """
        all_missing_files = []
        page_size = 500
        current_offset = 0
        
        while True:
            completed_tasks, _ = self._repository.get_completed_paginated(page_size, current_offset)
            if not completed_tasks:
                break
            
            for task in completed_tasks:
                file_path = task.get("file_path")
                if file_path and not os.path.exists(file_path):
                    all_missing_files.append(task)
            
            current_offset += page_size
            if len(completed_tasks) < page_size:
                break
        
        total_missing = len(all_missing_files)
        paginated_missing = all_missing_files[offset:offset + limit]
        
        return paginated_missing, total_missing


download_service = DownloadService()