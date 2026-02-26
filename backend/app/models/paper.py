from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


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
