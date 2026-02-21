from fastapi import APIRouter, Query, HTTPException, Body
from typing import Optional
import logging

from app.services.paper_service import PaperService
from app.services.llm_service import llm_service
from app.models import (
    SemanticSearchRequest,
    SemanticSearchResponse,
    SimilarPapersResponse,
    GenerateEmbeddingsRequest,
    GenerateEmbeddingsResponse,
    AskRequest,
    AskResponse,
    PaperReference,
    LLMProvidersResponse,
    LLMProviderInfo,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/arxiv", tags=["arxiv"])

_paper_service = PaperService()


@router.get("/query")
async def query_papers(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    category: Optional[str] = Query(None, description="arXiv category filter (e.g., 'cs.LG')"),
    start: int = Query(0, ge=0, description="Start index for pagination"),
    max_results: int = Query(50, ge=1, le=500, description="Maximum papers to return"),
    fetch_category: str = Query("cs*", description="Category to fetch from arXiv (e.g., 'cs*', 'physics*', or empty for all)"),
):
    """
    Query papers for a specific date.
    
    - If local data exists for the date, returns from local storage
    - If no local data, fetches papers for that date from arXiv with fetch_category filter, stores them, then returns filtered results
    """
    try:
        result = await _paper_service.query_papers(
            date=date,
            category=category,
            start=start,
            max_results=max_results,
            fetch_category=fetch_category
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
async def fetch_papers_for_date(
    date: str,
    category: str = Query("cs*", description="Category to fetch from arXiv (e.g., 'cs*', 'physics*', or empty string for all)")
):
    """
    Manually fetch and store papers for a specific date.
    Date format: YYYY-MM-DD
    Category: arXiv category pattern (e.g., 'cs*' for all CS, 'cs.LG' for ML, '' for all)
    """
    result = await _paper_service.fetch_papers_for_date(date, category)
    return result


@router.post("/search", response_model=SemanticSearchResponse)
async def search_papers_semantic(request: SemanticSearchRequest = Body(...)):
    """
    Search papers using semantic similarity.
    
    Uses embedding-based semantic search to find papers that match the query
    in meaning, not just keywords.
    """
    result = await _paper_service.search_papers_semantic(
        query=request.query,
        top_k=request.top_k,
        category=request.category,
        date_from=request.date_from,
        date_to=request.date_to,
    )
    return result


@router.get("/paper/{paper_id}/similar", response_model=SimilarPapersResponse)
async def get_similar_papers(
    paper_id: str,
    top_k: int = Query(5, ge=1, le=20, description="Number of similar papers to return"),
):
    """
    Get papers similar to a given paper.
    
    Finds papers with similar content based on embedding similarity.
    """
    result = await _paper_service.get_similar_papers(
        paper_id=paper_id,
        top_k=top_k,
    )
    return result


@router.post("/embeddings/generate", response_model=GenerateEmbeddingsResponse)
async def generate_embeddings(request: GenerateEmbeddingsRequest = Body(...)):
    """
    Generate embeddings for papers.
    
    Generates vector embeddings for papers that don't have them yet.
    Can optionally filter by date or date range.
    """
    result = await _paper_service.generate_embeddings(
        date=request.date,
        date_from=request.date_from,
        date_to=request.date_to,
        force=request.force,
        batch_size=request.batch_size,
    )
    return result


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest = Body(...)):
    """
    Ask a question and get AI-powered answer with paper references.
    
    1. Uses semantic search to find relevant papers
    2. Builds context from paper abstracts
    3. Calls LLM to generate answer
    4. Returns answer with paper references
    
    Optional: Specify provider and model to use a specific LLM.
    """
    try:
        search_result = await _paper_service.search_papers_semantic(
            query=request.question,
            top_k=request.top_k,
        )
        
        papers = search_result.get("papers", [])
        
        if not papers:
            return AskResponse(
                answer="I couldn't find any relevant papers in the database to answer your question. "
                       "Try searching for papers first or rephrase your question.",
                references=[],
                model=None,
            )
        
        answer = await llm_service.ask_question(
            question=request.question,
            papers=papers,
            provider=request.provider,
            model=request.model,
        )
        
        references = []
        if request.include_references:
            for paper in papers[:request.top_k]:
                references.append(PaperReference(
                    id=paper.get("id", ""),
                    title=paper.get("title", ""),
                    authors=paper.get("authors", []),
                    published=paper.get("published"),
                    relevance_score=paper.get("similarity_score", 0.0),
                ))
        
        return AskResponse(
            answer=answer,
            references=references,
            model=llm_service.get_model_name(provider=request.provider, model=request.model),
        )
        
    except Exception as e:
        logger.error(f"Error in ask endpoint: {e}")
        return AskResponse(
            answer="",
            references=[],
            error=str(e),
        )


@router.get("/llm/providers", response_model=LLMProvidersResponse)
async def get_llm_providers():
    """
    Get available LLM providers.
    
    Returns list of supported LLM providers with their availability status,
    supported models, and descriptions.
    """
    providers = llm_service.get_providers()
    
    default_provider = None
    if llm_service.is_available(llm_service.settings.LLM_PROVIDER):
        default_provider = llm_service.settings.LLM_PROVIDER
    else:
        for p in providers:
            if p.get("available"):
                default_provider = p.get("id")
                break
    
    return LLMProvidersResponse(
        providers=[LLMProviderInfo(**p) for p in providers],
        default_provider=default_provider,
    )


@router.get("/llm/ollama/status")
async def get_ollama_status(
    model: Optional[str] = Query(None, description="Model to check availability for")
):
    """
    Check Ollama service status and available models.
    
    Returns detailed status information about the Ollama service.
    If model is provided, checks if that specific model is available.
    """
    from app.services.llm_service import OllamaProvider
    
    check_model = model or llm_service.settings.OLLAMA_MODEL or "llama3"
    
    provider = OllamaProvider(
        base_url=llm_service.settings.OLLAMA_BASE_URL,
        model=check_model,
    )
    
    available, error = await provider.check_available()
    
    try:
        models = await provider._get_available_models()
    except Exception:
        models = []
    
    return {
        "available": available,
        "error": error if not available else None,
        "base_url": llm_service.settings.OLLAMA_BASE_URL,
        "default_model": llm_service.settings.OLLAMA_MODEL or "llama3",
        "checked_model": check_model,
        "available_models": models,
    }
