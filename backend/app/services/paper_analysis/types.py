from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AnalysisType(str, Enum):
    FULL = "full"
    SUMMARY = "summary"
    KEYPOINTS = "keypoints"
    METHODOLOGY = "methodology"
    QUESTIONS = "questions"


class KeyPoint(BaseModel):
    title: str = Field(..., description="Key point title")
    description: str = Field(..., description="Detailed description of the key point")
    importance: str = Field(default="medium", description="Importance level: high, medium, low")


class QuestionAndConclusion(BaseModel):
    question: str = Field(..., description="Research question addressed")
    conclusion: str = Field(..., description="Main conclusion related to the question")


class AnalysisResult(BaseModel):
    paper_id: str = Field(..., description="Paper ID")
    summary: Optional[str] = Field(None, description="Generated summary")
    key_points: Optional[List[KeyPoint]] = Field(None, description="Extracted key points")
    methodology: Optional[str] = Field(None, description="Methodology analysis")
    questions_and_conclusions: Optional[List[QuestionAndConclusion]] = Field(None, description="Questions and conclusions")
    analyzed_at: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    service_used: str = Field(..., description="AI service used for analysis")
    model_used: str = Field(..., description="Model used for analysis")


class AnalysisRequest(BaseModel):
    service: Optional[str] = Field(None, description="AI service to use (openai, anthropic, ollama, etc.)")
    model: Optional[str] = Field(None, description="Model to use")
    analysis_type: AnalysisType = Field(default=AnalysisType.FULL, description="Type of analysis")
    language: str = Field(default="en", description="Output language (en or zh)")


class AnalysisResponse(BaseModel):
    success: bool = Field(..., description="Whether the analysis was successful")
    result: Optional[AnalysisResult] = Field(None, description="Analysis result")
    error: Optional[str] = Field(None, description="Error message if failed")
