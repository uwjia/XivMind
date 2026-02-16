from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import logging

from app.config import get_settings
from app.services.paper_service import PaperService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/arxiv", tags=["arxiv"])

_settings = get_settings()
_paper_service = PaperService(_settings.SQLITE_DB_PATH)


@router.get("/query")
async def query_papers(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    category: Optional[str] = Query(None, description="arXiv category filter (e.g., 'cs.LG')"),
    start: int = Query(0, ge=0, description="Start index for pagination"),
    max_results: int = Query(50, ge=1, le=500, description="Maximum papers to return"),
):
    """
    Query papers for a specific date.
    
    - If local data exists for the date, returns from local storage
    - If no local data, fetches ALL papers for that date from arXiv, stores them, then returns filtered results
    """
    try:
        result = await _paper_service.query_papers(
            date=date,
            category=category,
            start=start,
            max_results=max_results
        )
        return result
    except Exception as e:
        logger.error(f"Error querying papers: {e}")
        return {
            "papers": [],
            "total": 0,
            "start": start,
            "max_results": max_results,
        }


@router.get("/paper/{paper_id}")
async def get_paper(paper_id: str):
    """Get a single paper by ID."""
    paper = _paper_service.get_paper_by_id(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.delete("/cache/date/{date}")
async def clear_date_cache(date: str):
    """Clear cache for a specific date."""
    _paper_service.clear_date_index(date)
    return {"message": f"Cache cleared for {date}"}


@router.delete("/cache/date")
async def clear_all_date_cache():
    """Clear all date index cache."""
    _paper_service.clear_all_date_index()
    return {"message": "All date index cache cleared"}


@router.get("/date-indexes")
async def get_date_indexes():
    """Get all date index records."""
    return {"indexes": _paper_service.get_all_date_indexes()}


@router.get("/statistics")
async def get_statistics():
    """Get statistics about stored papers."""
    return _paper_service.get_statistics()


@router.post("/fetch/{date}")
async def fetch_papers_for_date(date: str):
    """
    Manually fetch and store papers for a specific date.
    Date format: YYYY-MM-DD
    """
    result = await _paper_service.fetch_papers_for_date(date)
    return result
