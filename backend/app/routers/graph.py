from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import logging

from app.services.graph_service import graph_service
from app.models import (
    KnowledgeGraphData,
    SimilarityMatrixResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/{date}", response_model=KnowledgeGraphData, response_model_by_alias=True)
async def get_graph_data(
    date: str,
    threshold: float = Query(0.5, ge=0.0, le=1.0, description="Similarity threshold for edges"),
    category: Optional[str] = Query(None, description="Filter by category (e.g., 'cs.LG')"),
    max_papers: int = Query(200, ge=10, le=2000, description="Maximum papers to include in graph"),
):
    """
    Get knowledge graph data for a specific date.
    
    Returns nodes (papers) and edges (similarities) for visualization.
    - Nodes are colored by category
    - Node size reflects citation count
    - Edge width reflects similarity score
    """
    try:
        graph_data = await graph_service.get_graph_data(
            date=date,
            threshold=threshold,
            category=category,
            max_papers=max_papers
        )
        return graph_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error building graph for {date}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to build graph: {str(e)}")


@router.get("/similarity/{date}", response_model=SimilarityMatrixResponse)
async def get_similarity_matrix(
    date: str,
    threshold: float = Query(0.3, ge=0.0, le=1.0, description="Minimum similarity threshold"),
    category: Optional[str] = Query(None, description="Filter by category"),
    max_papers: int = Query(200, ge=10, le=2000, description="Maximum papers to analyze"),
):
    """
    Get similarity matrix for papers on a specific date.
    
    Returns pairs of similar papers with their similarity scores.
    Useful for building custom visualizations or analysis.
    """
    try:
        similarities, total_papers = await graph_service.get_similarity_matrix(
            date=date,
            threshold=threshold,
            category=category,
            max_papers=max_papers
        )
        
        return SimilarityMatrixResponse(
            date=date,
            similarities=similarities,
            total_papers=total_papers,
            threshold=threshold
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating similarity matrix for {date}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate similarity: {str(e)}")
