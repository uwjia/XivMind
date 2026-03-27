import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query

from app.services.author_analysis_service import (
    get_author_rank_service,
    run_pagerank_analysis,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/author-analysis", tags=["author-analysis"])

_analysis_status = {
    "running": False,
    "progress": 0,
    "total": 0,
    "result": None,
    "error": None,
}


def _progress_callback(processed: int, total: int):
    """Progress callback function"""
    global _analysis_status
    _analysis_status["progress"] = processed
    _analysis_status["total"] = total


def _run_analysis_task(
    min_papers: int = 3, 
    alpha: float = 0.85, 
    use_disambiguation: bool = True,
    similarity_threshold: float = 0.1,
):
    """Background analysis task"""
    global _analysis_status
    _analysis_status["running"] = True
    _analysis_status["progress"] = 0
    _analysis_status["total"] = 0
    _analysis_status["result"] = None
    _analysis_status["error"] = None
    
    try:
        result = run_pagerank_analysis(
            min_papers=min_papers,
            alpha=alpha,
            use_disambiguation=use_disambiguation,
            similarity_threshold=similarity_threshold,
            progress_callback=_progress_callback,
        )
        _analysis_status["result"] = result.to_dict()
    except Exception as e:
        logger.error(f"Analysis task failed: {e}")
        _analysis_status["error"] = str(e)
    finally:
        _analysis_status["running"] = False


@router.get("/top-authors")
async def get_top_authors(
    metric: str = Query(
        "pagerank",
        regex="^(pagerank|degree_centrality|betweenness_centrality|paper_count|clustering_coeff)$",
        description="Sorting metric",
    ),
    category: Optional[str] = Query(None, description="Research field filter"),
    name_search: Optional[str] = Query(None, description="Author name search"),
    limit: int = Query(100, ge=1, le=500, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
) -> Dict[str, Any]:
    """
    Get top-ranked authors
    
    - **metric**: Sorting metric (pagerank, degree_centrality, betweenness_centrality, paper_count, clustering_coeff)
    - **category**: Research field filter (optional)
    - **name_search**: Author name search filter (optional)
    - **limit**: Number of results (1-500)
    - **offset**: Offset for pagination (default 0)
    """
    service = get_author_rank_service()
    return service.get_top_authors(
        metric=metric,
        category=category,
        name_search=name_search,
        limit=limit,
        offset=offset,
    )


@router.get("/author/{author_id}")
async def get_author_detail(author_id: str) -> Dict[str, Any]:
    """
    Get author details
    
    - **author_id**: Author ID (normalized name)
    """
    service = get_author_rank_service()
    author = service.get_author_by_id(author_id)
    
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    
    return author


@router.post("/rebuild")
async def rebuild_analysis(
    background_tasks: BackgroundTasks,
    min_papers: int = Query(3, ge=1, description="Minimum paper count threshold"),
    alpha: float = Query(0.85, ge=0.1, le=0.99, description="PageRank damping factor"),
    use_disambiguation: bool = Query(True, description="Enable author disambiguation"),
    similarity_threshold: float = Query(0.1, ge=0.0, le=1.0, description="Collaborator similarity threshold for disambiguation"),
) -> Dict[str, Any]:
    """
    Rebuild analysis data in background
    
    This operation runs in the background and may take several minutes to hours.
    Check progress via the /status endpoint.
    
    - **min_papers**: Minimum paper count threshold to filter low-activity authors
    - **alpha**: PageRank damping factor (0.1-0.99)
    - **use_disambiguation**: Enable author name disambiguation to separate different authors with the same name
    - **similarity_threshold**: Jaccard similarity threshold for clustering papers (0.0-1.0)
    """
    global _analysis_status
    
    if _analysis_status["running"]:
        return {
            "status": "already_running",
            "message": "Analysis task is already running",
            "progress": _analysis_status["progress"],
            "total": _analysis_status["total"],
        }
    
    background_tasks.add_task(
        _run_analysis_task, 
        min_papers=min_papers, 
        alpha=alpha,
        use_disambiguation=use_disambiguation,
        similarity_threshold=similarity_threshold,
    )
    
    return {
        "status": "started",
        "message": "Analysis task started",
        "disambiguation_enabled": use_disambiguation,
    }


@router.get("/status")
async def get_analysis_status() -> Dict[str, Any]:
    """
    Get analysis task status
    
    Returns the current running status and progress of the analysis task
    """
    global _analysis_status
    
    return {
        "running": _analysis_status["running"],
        "progress": _analysis_status["progress"],
        "total": _analysis_status["total"],
        "result": _analysis_status["result"],
        "error": _analysis_status["error"],
    }


@router.get("/statistics")
async def get_statistics() -> Dict[str, Any]:
    """
    Get statistics
    
    Returns statistics such as total papers and total authors
    """
    service = get_author_rank_service()
    return service.get_statistics()


@router.delete("/clear")
async def clear_analysis_data() -> Dict[str, str]:
    """
    Clear analysis data
    
    Delete all calculated author ranking data
    """
    service = get_author_rank_service()
    service.clear_all()
    
    return {"status": "success", "message": "Analysis data cleared"}
