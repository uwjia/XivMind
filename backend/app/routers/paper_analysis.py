import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json

from app.services.paper_analysis import (
    paper_analysis_service,
    AnalysisRequest,
    AnalysisResponse,
    AnalysisResult,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/papers", tags=["paper-analysis"])


@router.post("/{paper_id}/analyze", response_model=AnalysisResponse)
async def analyze_paper(paper_id: str, request: AnalysisRequest = AnalysisRequest()):
    """
    Analyze a paper using AI.
    
    This endpoint performs a complete analysis and returns the result.
    For streaming analysis, use the /analyze/stream endpoint.
    """
    try:
        result = await paper_analysis_service.analyze_paper(paper_id, request)
        return AnalysisResponse(success=True, result=result)
    except ValueError as e:
        logger.error(f"Paper not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return AnalysisResponse(success=False, error=str(e))


@router.post("/{paper_id}/analyze/stream")
async def analyze_paper_stream(paper_id: str, request: AnalysisRequest = AnalysisRequest()):
    """
    Analyze a paper using AI with streaming response.
    
    Returns Server-Sent Events (SSE) with analysis progress and results.
    """
    logger.info(f"Stream analysis request for paper {paper_id}: language={request.language}, type={request.analysis_type}")
    
    async def event_generator():
        try:
            async for event in paper_analysis_service.analyze_paper_stream(paper_id, request):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            logger.error(f"Streaming analysis failed: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/{paper_id}/analysis", response_model=AnalysisResult)
async def get_analysis(paper_id: str):
    """
    Get cached analysis result for a paper.
    
    This endpoint returns the previously cached analysis if available.
    """
    raise HTTPException(
        status_code=501, 
        detail="Analysis caching not yet implemented. Use /analyze endpoint."
    )
