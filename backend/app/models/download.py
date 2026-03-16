from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DownloadStatus(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"


class DownloadTaskCreate(BaseModel):
    paper_id: str
    arxiv_id: Optional[str] = None
    title: str
    pdf_url: str


class DownloadTaskResponse(BaseModel):
    id: str
    paper_id: str
    arxiv_id: Optional[str] = None
    title: str
    pdf_url: str
    status: DownloadStatus
    progress: int = 0
    file_path: Optional[str] = None
    file_size: int = 0
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DownloadTaskListResponse(BaseModel):
    total: int
    completed_count: int
    items: List[DownloadTaskResponse]


class DownloadCheckBatchRequest(BaseModel):
    paper_ids: list[str]


class DownloadCheckBatchResponse(BaseModel):
    downloads: dict[str, bool]


class DownloadCheckResponse(BaseModel):
    is_downloaded: bool


class SyncResultDetail(BaseModel):
    paper_id: str
    status: str
    file_path: str
    reason: str | None = None


class SyncLocalFilesResponse(BaseModel):
    added: int
    skipped: int
    errors: int
    details: list[SyncResultDetail]

