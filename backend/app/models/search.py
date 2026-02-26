from pydantic import BaseModel, Field
from typing import Optional, List

from .bookmark import BookmarkResponse


class SearchResult(BaseModel):
    papers: List[BookmarkResponse]
    query: str
    total: int


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., description="Natural language query for semantic search")
    top_k: int = Field(10, ge=1, le=100, description="Number of results to return")
    category: Optional[str] = Field(None, description="Filter by category (e.g., 'cs.LG')")
    date_from: Optional[str] = Field(None, description="Filter papers from this date (YYYY-MM-DD)")
    date_to: Optional[str] = Field(None, description="Filter papers to this date (YYYY-MM-DD)")


class SemanticSearchResult(BaseModel):
    id: str
    title: str
    abstract: str
    authors: List[str] = []
    primary_category: str = ""
    categories: List[str] = []
    pdf_url: str = ""
    abs_url: str = ""
    published: Optional[str] = None
    similarity_score: float = 0.0


class SemanticSearchResponse(BaseModel):
    papers: List[SemanticSearchResult]
    total: int
    query: str
    model: Optional[str] = None
    error: Optional[str] = None


class SimilarPapersResponse(BaseModel):
    papers: List[SemanticSearchResult]
    source_paper_id: str
    error: Optional[str] = None
