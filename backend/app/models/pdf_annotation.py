from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AnnotationType(str, Enum):
    HIGHLIGHT = "highlight"
    UNDERLINE = "underline"
    STRIKEOUT = "strikeout"
    DRAWING = "drawing"
    COMMENT = "comment"


class AnnotationPosition(BaseModel):
    x: float
    y: float
    width: float
    height: float


class PdfAnnotationCreate(BaseModel):
    paper_id: str
    type: AnnotationType
    page_number: int
    position: AnnotationPosition
    content: Optional[str] = None
    color: str
    stroke_width: Optional[int] = None


class PdfAnnotationUpdate(BaseModel):
    position: Optional[AnnotationPosition] = None
    content: Optional[str] = None
    color: Optional[str] = None
    stroke_width: Optional[int] = None


class PdfAnnotationResponse(BaseModel):
    id: str
    paper_id: str
    type: AnnotationType
    page_number: int
    position: AnnotationPosition
    content: Optional[str] = None
    color: str
    stroke_width: Optional[int] = None
    created_at: str
    updated_at: str


class PdfReadingProgressCreate(BaseModel):
    current_page: int
    total_pages: int
    zoom_level: float
    view_mode: str = "continuous"


class PdfReadingProgressResponse(BaseModel):
    paper_id: str
    current_page: int
    total_pages: int
    zoom_level: float
    view_mode: str
    last_read_at: str


class PdfOutlineItemResponse(BaseModel):
    title: str
    dest: Optional[int] = None
    items: List["PdfOutlineItemResponse"] = []


PdfOutlineItemResponse.model_rebuild()
