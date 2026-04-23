import logging
from fastapi import APIRouter, Query
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict

from app.services.listings_service import ListingsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/listings", tags=["listings"])

_listings_service = ListingsService()


class PaperCodeCheckRequest(BaseModel):
    paper_ids: List[str]


class PaperCodeCheckResponse(BaseModel):
    codes: Dict[str, bool]


class PaperCodeBatchRequest(BaseModel):
    paper_ids: List[str]


@router.post("/fetch")
async def fetch_new_listings():
    """
    Fetch and store arXiv new listings.
    
    Scrapes the arXiv new listings page (https://arxiv.org/list/cs/new),
    extracts paper IDs for new, cross, and replacement submissions,
    fetches paper details from arXiv API, and stores them in the database.
    """
    try:
        result = await _listings_service.fetch_and_store_listings()
        return result
    except Exception as e:
        logger.error(f"Error fetching new listings: {e}")
        return {
            "success": False,
            "error": str(e),
            "new_count": 0,
            "cross_count": 0,
            "replacement_count": 0,
            "total_count": 0,
        }


@router.get("/indexes")
async def get_listings_indexes():
    """
    Get all listings date indexes.
    
    Returns a list of all dates that have listings data stored,
    with counts for each type of submission.
    """
    try:
        indexes = _listings_service.get_listings_indexes()
        return {"indexes": indexes}
    except Exception as e:
        logger.error(f"Error getting listings indexes: {e}")
        return {"indexes": []}


@router.get("/new")
async def get_latest_listings(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format. If not specified, get latest with auto-refresh")
):
    """
    Get the latest day's listings for all three types with auto-refresh.
    
    If date is specified, return papers for that date without auto-refresh.
    If date is not specified, return latest papers with auto-refresh.
    
    Returns:
        {
            "date": "2026-04-13",
            "new": [...],
            "cross": [...],
            "replacement": [...],
            "auto_refreshed": true
        }
    """
    try:
        result = await _listings_service.get_latest_listings(date)
        return result
    except Exception as e:
        logger.error(f"Error getting latest listings: {e}")
        return {
            "date": "",
            "new": [],
            "cross": [],
            "replacement": [],
            "auto_refreshed": False,
            "error": str(e),
        }


@router.get("/{date}")
async def get_listings_by_date(
    date: str,
    listing_type: str = Query("new", description="Type of listings: 'new', 'cross', or 'replacement'"),
    start: int = Query(0, ge=0, description="Start index for pagination"),
    max_results: int = Query(50, ge=1, le=5000, description="Maximum papers to return"),
):
    """
    Get listings by date and type.
    
    - date: Date in YYYY-MM-DD format
    - listing_type: 'new', 'cross', or 'replacement'
    """
    try:
        result = _listings_service.get_listings_by_date(
            date=date,
            listing_type=listing_type,
            start=start,
            max_results=max_results
        )
        return result
    except Exception as e:
        logger.error(f"Error getting listings: {e}")
        return {
            "papers": [],
            "total": 0,
            "date": date,
            "listing_type": listing_type,
            "start": start,
            "max_results": max_results,
            "error": str(e),
        }


@router.post("/codes/check", response_model=PaperCodeCheckResponse)
async def check_papers_with_code(request: PaperCodeCheckRequest):
    """
    Check which papers have code repositories.
    
    Returns a dictionary mapping paper_id to boolean (True if has code).
    """
    try:
        if not request.paper_ids:
            return PaperCodeCheckResponse(codes={})
        result = _listings_service.check_papers_with_code(request.paper_ids)
        return PaperCodeCheckResponse(codes=result)
    except Exception as e:
        logger.error(f"Error checking papers with code: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/codes/batch")
async def get_codes_for_papers(request: PaperCodeBatchRequest):
    """
    Get code repositories for multiple papers.
    
    Returns a dictionary mapping paper_id to code repository info (or null if not found).
    """
    try:
        if not request.paper_ids:
            return {}
        result = _listings_service.get_codes_for_papers(request.paper_ids)
        return result
    except Exception as e:
        logger.error(f"Error getting codes for papers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class PapersWithCodeRequest(BaseModel):
    date: str


@router.post("/codes/papers")
async def get_papers_with_code(request: PapersWithCodeRequest):
    """
    Get papers with code repositories for a specific date.
    
    Returns papers that have code repository links, grouped by submission type.
    
    Returns:
        {
            "date": "2026-04-22",
            "new": [...],
            "cross": [...],
            "replacement": [...]
        }
    """
    try:
        result = _listings_service.get_papers_with_code_by_date(request.date)
        return result
    except Exception as e:
        logger.error(f"Error getting papers with code: {e}")
        raise HTTPException(status_code=500, detail=str(e))
