import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.models.daily_analysis import (
    DailyAnalysisRequest,
    DailyAnalysisResponse,
)
from app.services.daily_analysis.service import daily_analysis_service

router = APIRouter(prefix="/daily-analysis", tags=["daily-analysis"])


class PaperCountResponse(BaseModel):
    date: str
    total_papers: int


@router.get("/papers/count/{date}", response_model=PaperCountResponse)
async def get_paper_count(date: str):
    """
    Get the total number of papers for a specific date.
    
    - **date**: Date in YYYY-MM-DD format
    """
    count = daily_analysis_service.get_paper_count(date)
    return PaperCountResponse(date=date, total_papers=count)


@router.post("/analyze", response_model=DailyAnalysisResponse)
async def analyze_daily_papers(request: DailyAnalysisRequest):
    """
    Analyze daily papers using LLM.
    
    - **date**: Date in YYYY-MM-DD format
    - **mode**: Analysis mode (summary, trends, high_value, recommend, full)
    - **user_interests**: User's research interests for matching
    - **provider**: LLM provider to use
    - **model**: Specific model to use
    """
    try:
        result = await daily_analysis_service.analyze(request)
        return DailyAnalysisResponse(success=True, result=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        return DailyAnalysisResponse(success=False, error=str(e))


@router.post("/analyze/stream")
async def analyze_daily_papers_stream(request: DailyAnalysisRequest):
    """
    Stream analysis results for daily papers.
    
    Returns Server-Sent Events (SSE) with analysis progress and results.
    """
    async def event_generator():
        try:
            async for event in daily_analysis_service.analyze_stream(request):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
