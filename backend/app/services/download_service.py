from app.db.base import DownloadRepository
from app.db.factory import get_download_repository
from typing import Dict, List, Optional, Tuple, Any


class DownloadService:
    def __init__(self, repository: Optional[DownloadRepository] = None):
        self._repository = repository or get_download_repository()

    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._repository.add(task_data)

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self._repository.get(task_id)

    def get_all_tasks(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        return self._repository.get_all(limit, offset)

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

    def reset_incomplete_tasks(self) -> int:
        return self._repository.reset_incomplete_tasks()


download_service = DownloadService()
