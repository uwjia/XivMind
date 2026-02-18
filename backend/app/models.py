from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DownloadStatus(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"


class PaperBase(BaseModel):
    id: str
    arxiv_id: Optional[str] = None
    title: str
    authors: List[str] = []
    abstract: str = ""
    comment: Optional[str] = None
    journal_ref: Optional[str] = None
    doi: Optional[str] = None
    primary_category: str = ""
    categories: List[str] = []
    pdf_url: str = ""
    abs_url: str = ""
    published: Optional[datetime] = None
    updated: Optional[datetime] = None


class Paper(PaperBase):
    pass


class BookmarkCreate(BaseModel):
    paper_id: str
    arxiv_id: Optional[str] = None
    title: str
    authors: List[str] = []
    abstract: str = ""
    comment: Optional[str] = None
    journal_ref: Optional[str] = None
    doi: Optional[str] = None
    primary_category: str = ""
    categories: List[str] = []
    pdf_url: str = ""
    abs_url: str = ""
    published: Optional[str] = None
    updated: Optional[str] = None


class BookmarkResponse(BaseModel):
    id: str
    paper_id: str
    arxiv_id: Optional[str] = None
    title: str
    authors: List[str] = []
    abstract: str = ""
    comment: Optional[str] = None
    journal_ref: Optional[str] = None
    doi: Optional[str] = None
    primary_category: str = ""
    categories: List[str] = []
    pdf_url: str = ""
    abs_url: str = ""
    published: Optional[str] = None
    updated: Optional[str] = None
    created_at: datetime
    embedding: Optional[List[float]] = None


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


class BookmarkListResponse(BaseModel):
    total: int
    items: List[BookmarkResponse]


class DownloadTaskListResponse(BaseModel):
    total: int
    items: List[DownloadTaskResponse]


class SearchResult(BaseModel):
    papers: List[BookmarkResponse]
    query: str
    total: int


class MessageResponse(BaseModel):
    message: str
    success: bool = True
