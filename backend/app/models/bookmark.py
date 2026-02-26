from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


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


class BookmarkListResponse(BaseModel):
    total: int
    items: List[BookmarkResponse]
