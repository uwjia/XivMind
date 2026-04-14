from fastapi import APIRouter, Query, HTTPException, Body, BackgroundTasks
from typing import Optional
from urllib.parse import unquote
import logging

from app.services.paper_service import PaperService
from app.services.author_profile_service import AuthorProfileService
from app.services.llm_service import llm_service
from app.services.memory.service import memory_service
from app.services.memory.auto_capture import AutoCaptureService
from app.services.memory.auto_recall import AutoRecallService
from app.services.memory.types import MemoryConfig
from app.models import (
    SemanticSearchRequest,
    SemanticSearchResponse,
    SimilarPapersResponse,
    GenerateEmbeddingsRequest,
    GenerateEmbeddingsResponse,
    AskRequest,
    AskResponse,
    AskWithMemoryRequest,
    AskWithMemoryResponse,
    PaperReference,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/arxiv", tags=["arxiv"])

_paper_service = PaperService()
_author_profile_service = AuthorProfileService(_paper_service)
auto_capture_service = AutoCaptureService()
auto_recall_service = AutoRecallService()


@router.get("/query")
async def query_papers(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    category: Optional[str] = Query(None, description="arXiv category filter (e.g., 'cs.LG')"),
    start: int = Query(0, ge=0, description="Start index for pagination"),
    max_results: int = Query(50, ge=1, le=5000, description="Maximum papers to return"),
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


@router.get("/author/{author_name:path}/profile")
async def get_author_profile(author_name: str):
    """
    Get author profile with statistics and visualization data.
    
    Returns:
    - Total papers count
    - Active years range
    - Category distribution
    - Yearly paper counts
    - Top collaborators
    - Top keywords
    """
    try:
        author = unquote(author_name)
        profile = _author_profile_service.get_author_profile(author)
        return profile
    except Exception as e:
        logger.error(f"Error getting author profile: {e}")
        return {
            "name": author_name,
            "total_papers": 0,
            "first_paper_year": None,
            "latest_paper_year": None,
            "active_years": 0,
            "categories": [],
            "yearly_papers": [],
            "collaborators": [],
            "keywords": [],
            "error": str(e),
        }


@router.get("/author/{author_name:path}")
async def get_papers_by_author(
    author_name: str,
    start: int = Query(0, ge=0, description="Start index for pagination"),
    max_results: int = Query(50, ge=1, le=500, description="Maximum papers to return"),
):
    """
    Get papers by author name, sorted by published date (newest first).
    
    The author name should be URL-encoded. For example:
    - "John Smith" -> "/author/John%20Smith"
    - "Hans Raj Tiwary" -> "/author/Hans%20Raj%20Tiwary"
    """
    try:
        author = unquote(author_name)
        result = _paper_service.query_papers_by_author(
            author=author,
            start=start,
            max_results=max_results,
        )
        return result
    except Exception as e:
        logger.error(f"Error querying papers by author: {e}")
        return {
            "papers": [],
            "total": 0,
            "start": start,
            "max_results": max_results,
            "author": author_name,
        }


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
        
        if search_result.get("error"):
            return AskResponse(
                answer="",
                references=[],
                error=search_result["error"],
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


@router.post("/ask-with-memory", response_model=AskWithMemoryResponse)
async def ask_question_with_memory(
    request: AskWithMemoryRequest = Body(...),
    background_tasks: BackgroundTasks = None,
):
    """
    Ask a question with memory-based personalization.
    
    This endpoint enhances the basic ask functionality with:
    - User profile context (research interests, preferences)
    - Relevant conversation history
    - Personalized response style (language, summary format)
    - Auto-capture of important conversations
    
    Features:
    1. Uses semantic search to find relevant papers
    2. Retrieves user's core memory (profile)
    3. Searches for relevant conversation memories (auto-recall)
    4. Builds personalized system prompt
    5. Calls LLM with enhanced context
    6. Auto-captures conversation if enabled (background task)
    7. Returns answer with memory usage info
    """
    try:
        search_result = await _paper_service.search_papers_semantic(
            query=request.question,
            top_k=request.top_k,
        )
        
        if search_result.get("error"):
            return AskWithMemoryResponse(
                answer="",
                references=[],
                error=search_result["error"],
            )
        
        papers = search_result.get("papers", [])
        
        memory_context = None
        core_memory = None
        relevant_memories_count = 0
        memory_config = MemoryConfig()
        
        if request.use_memory:
            try:
                from app.db.factory import get_memory_repository
                repo = get_memory_repository()
                memory_config = await repo.get_memory_config(request.user_id)
                
                core_memory = await memory_service.get_core_memory(request.user_id)
                
                if memory_config.auto_recall:
                    recall_result = await auto_recall_service.recall_for_query(
                        query=request.question,
                        user_id=request.user_id,
                        config=memory_config,
                    )
                    memory_context = recall_result.context_string
                    relevant_memories_count = len(recall_result.memories)
                else:
                    memory_context = await memory_service.build_context_for_query(
                        query=request.question,
                        user_id=request.user_id,
                    )
                    relevant_memories_count = memory_context.count('\n- ') if memory_context else 0
                
                logger.info(f"Memory context loaded: core_memory={core_memory is not None}, context_length={len(memory_context) if memory_context else 0}")
            except Exception as mem_error:
                logger.warning(f"Failed to load memory context: {mem_error}")
        
        if not papers:
            return AskWithMemoryResponse(
                answer="I couldn't find any relevant papers in the database to answer your question. "
                       "Try searching for papers first or rephrase your question.",
                references=[],
                model=None,
                memory_used=request.use_memory,
                relevant_memories_count=relevant_memories_count,
            )
        
        answer = await llm_service.ask_question_with_memory(
            question=request.question,
            papers=papers,
            memory_context=memory_context,
            core_memory=core_memory,
            provider=request.provider,
            model=request.model,
        )
        
        if request.use_memory and memory_config.auto_capture and background_tasks:
            background_tasks.add_task(
                auto_capture_service.capture_conversation,
                user_id=request.user_id,
                session_id=request.session_id or "default",
                user_message=request.question,
                assistant_message=answer,
                config=memory_config,
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
        
        return AskWithMemoryResponse(
            answer=answer,
            references=references,
            model=llm_service.get_model_name(provider=request.provider, model=request.model),
            memory_used=request.use_memory,
            relevant_memories_count=relevant_memories_count,
        )
        
    except Exception as e:
        logger.error(f"Error in ask-with-memory endpoint: {e}")
        return AskWithMemoryResponse(
            answer="",
            references=[],
            error=str(e),
            memory_used=False,
            relevant_memories_count=0,
        )


@router.get("/embedding-indexes")
async def get_embedding_indexes():
    """
    Get all embedding indexes.
    
    Returns a list of all dates that have embedding indexes generated.
    """
    try:
        indexes = _paper_service.get_embedding_indexes()
        return {"indexes": indexes}
    except Exception as e:
        logger.error(f"Error getting embedding indexes: {e}")
        return {"indexes": []}


@router.get("/embedding-indexes/{date}")
async def get_embedding_index(date: str):
    """
    Get embedding index for a specific date.
    
    Returns the embedding index information for the given date.
    """
    index = _paper_service.get_embedding_index(date)
    if not index:
        raise HTTPException(status_code=404, detail="Embedding index not found")
    return index
