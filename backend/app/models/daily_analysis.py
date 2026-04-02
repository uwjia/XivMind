from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class AnalysisMode(str, Enum):
    SUMMARY = "summary"
    TRENDS = "trends"
    HIGH_VALUE = "high_value"
    RECOMMEND = "recommend"
    FULL = "full"


class Trend(BaseModel):
    name: str
    description: str
    paper_count: int
    paper_ids: List[str] = []


class HighValuePaper(BaseModel):
    paper_id: str
    title: str
    innovation_type: str
    innovation_description: str
    confidence: float


class RecommendedPaper(BaseModel):
    paper_id: str
    title: str
    relevance_score: int
    matched_interests: List[str]
    reason: str


class DailyAnalysisRequest(BaseModel):
    date: str
    mode: AnalysisMode = AnalysisMode.FULL
    user_interests: Optional[List[str]] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    language: str = "en"
    max_papers: int = 50


class DailyAnalysisResult(BaseModel):
    date: str
    total_papers: int
    summary: Optional[str] = None
    main_themes: Optional[List[str]] = None
    trends: Optional[List[Trend]] = None
    high_value_papers: Optional[List[HighValuePaper]] = None
    recommendations: Optional[List[RecommendedPaper]] = None
    analyzed_at: str
    model_used: str


class DailyAnalysisResponse(BaseModel):
    success: bool
    result: Optional[DailyAnalysisResult] = None
    error: Optional[str] = None
