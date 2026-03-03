from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional, List

from app.services.memory import (
    CoreMemory,
    MemoryService,
    MemoryExtractor,
    MemoryRetriever,
)
from app.services.memory.types import (
    CoreMemoryUpdate,
    RecallMemoryCreate,
    ArchivalMemoryCreate,
    MemorySearchResult,
    MemoryStats,
    ProcessConversationRequest,
    MemoryExtractionResult,
)
from app.services.memory.service import memory_service

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/core", response_model=CoreMemory)
async def get_core_memory(user_id: str = Query(default="default")):
    """Get user's core memory (profile)."""
    memory = await memory_service.get_core_memory(user_id)
    if not memory:
        return CoreMemory(user_id=user_id)
    return memory


@router.put("/core", response_model=CoreMemory)
async def update_core_memory(
    update: CoreMemoryUpdate,
    user_id: str = Query(default="default"),
):
    """Update user's core memory (profile)."""
    return await memory_service.update_core_memory(user_id, update)


@router.get("/recall")
async def get_recall_memories(
    user_id: str = Query(default="default"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """Get user's recall memories (conversation history)."""
    memories = await memory_service.get_recall_memories(user_id, limit, offset)
    return [
        {
            "memory_id": m.memory_id,
            "user_id": m.user_id,
            "session_id": m.session_id,
            "timestamp": m.timestamp.isoformat() if hasattr(m.timestamp, 'isoformat') else m.timestamp,
            "content": m.content,
            "importance_score": m.importance_score,
            "access_count": m.access_count,
        }
        for m in memories
    ]


@router.post("/recall", response_model=dict)
async def create_recall_memory(
    data: RecallMemoryCreate,
    user_id: str = Query(default="default"),
):
    """Create a new recall memory."""
    memory = await memory_service.create_recall_memory(user_id, data)
    return {
        "memory_id": memory.memory_id,
        "timestamp": memory.timestamp.isoformat(),
        "importance_score": memory.importance_score,
    }


@router.delete("/recall/{memory_id}")
async def delete_recall_memory(memory_id: str):
    """Delete a specific recall memory."""
    success = await memory_service.delete_recall_memory(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"success": True}


@router.get("/archival")
async def get_archival_memories(
    user_id: str = Query(default="default"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """Get user's archival memories (knowledge base)."""
    memories = await memory_service.get_archival_memories(user_id, limit, offset)
    return [
        {
            "memory_id": m.memory_id,
            "user_id": m.user_id,
            "content_type": m.content_type,
            "title": m.title,
            "content": m.content,
            "source_papers": m.source_papers,
            "tags": m.tags,
            "created_at": m.created_at.isoformat() if hasattr(m.created_at, 'isoformat') else m.created_at,
            "last_accessed": m.last_accessed.isoformat() if hasattr(m.last_accessed, 'isoformat') else m.last_accessed,
        }
        for m in memories
    ]


@router.post("/archival", response_model=dict)
async def create_archival_memory(
    data: ArchivalMemoryCreate,
    user_id: str = Query(default="default"),
):
    """Create a new archival memory (note/insight/summary)."""
    memory = await memory_service.create_archival_memory(user_id, data)
    return {
        "memory_id": memory.memory_id,
        "created_at": memory.created_at.isoformat(),
        "content_type": memory.content_type,
    }


@router.delete("/archival/{memory_id}")
async def delete_archival_memory(memory_id: str):
    """Delete a specific archival memory."""
    success = await memory_service.delete_archival_memory(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"success": True}


@router.post("/search", response_model=List[MemorySearchResult])
async def search_memories(
    query: str,
    user_id: str = Query(default="default"),
    top_k: int = Query(default=5, ge=1, le=20),
):
    """Search memories by semantic similarity."""
    return await memory_service.search_memories(query, user_id, top_k)


@router.get("/stats", response_model=MemoryStats)
async def get_memory_stats(user_id: str = Query(default="default")):
    """Get memory statistics for a user."""
    return await memory_service.get_memory_stats(user_id)


@router.delete("/clear")
async def clear_all_memories(user_id: str = Query(default="default")):
    """Clear all memories for a user."""
    success = await memory_service.clear_all_memories(user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to clear memories")
    return {"success": True}


@router.delete("/clear/core")
async def clear_core_memory(user_id: str = Query(default="default")):
    """Clear core memory (profile) for a user."""
    success = await memory_service.clear_core_memory(user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to clear core memory")
    return {"success": True}


@router.delete("/clear/recall")
async def clear_recall_memories(user_id: str = Query(default="default")):
    """Clear all recall memories for a user."""
    success = await memory_service.clear_recall_memories(user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to clear recall memories")
    return {"success": True}


@router.delete("/clear/archival")
async def clear_archival_memories(user_id: str = Query(default="default")):
    """Clear all archival memories for a user."""
    success = await memory_service.clear_archival_memories(user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to clear archival memories")
    return {"success": True}


@router.get("/context")
async def get_memory_context(
    query: str,
    user_id: str = Query(default="default"),
):
    """Get relevant memory context for a query."""
    context = await memory_service.build_context_for_query(query, user_id)
    return {"context": context}


@router.get("/profile")
async def get_user_profile(user_id: str = Query(default="default")):
    """Get user profile summary."""
    summary = await memory_service.get_user_profile_summary(user_id)
    return {"profile": summary}


@router.get("/recommended-skills")
async def get_recommended_skills(user_id: str = Query(default="default")):
    """Get recommended skills based on user's frequently used skills."""
    skills = await memory_service.get_recommended_skills(user_id)
    return {"skills": skills}


@router.post("/process-conversation")
async def process_conversation(
    data: ProcessConversationRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Query(default="default"),
):
    """Process a conversation and extract memories in the background.
    
    This endpoint immediately returns a task ID and processes the memory
    extraction asynchronously to avoid blocking the main thread.
    
    Args:
        extract: If True, extract profile data from conversation and update CoreMemory.
                 If False, only store as RecallMemory without profile extraction.
    """
    import uuid
    task_id = str(uuid.uuid4())
    
    background_tasks.add_task(
        memory_service.process_conversation,
        user_id=user_id,
        session_id=data.session_id,
        user_message=data.user_message,
        assistant_message=data.assistant_message,
        extract=data.extract,
    )
    
    return {
        "status": "processing",
        "task_id": task_id,
        "message": "Conversation queued for memory processing",
    }
