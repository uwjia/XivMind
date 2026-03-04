import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.db.factory import get_memory_repository
from app.services.memory.types import (
    CoreMemory,
    MemorySearchResult,
    MemoryType,
    MemoryCategory,
)
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class MemoryRetriever:
    """Retrieves relevant memories based on query."""
    
    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        self.embedding_service = embedding_service or EmbeddingService()
    
    async def get_core_memory(self, user_id: str = "default") -> Optional[CoreMemory]:
        return await get_memory_repository().get_core_memory(user_id)
    
    async def retrieve_relevant_memories(
        self,
        query: str,
        user_id: str = "default",
        top_k: int = 5,
        min_score: float = 0.0,
        include_recall: bool = True,
        include_archival: bool = True,
    ) -> List[MemorySearchResult]:
        results = []
        
        try:
            query_embedding, _ = self.embedding_service.encode(query)
            
            if include_recall:
                recall_results = await get_memory_repository().search_recall_memories(
                    query_embedding=query_embedding,
                    user_id=user_id,
                    top_k=top_k,
                )
                
                for r in recall_results:
                    similarity = r.get("similarity_score", 0.5)
                    if similarity < min_score:
                        continue
                    
                    timestamp_raw = r.get("timestamp")
                    if isinstance(timestamp_raw, datetime):
                        timestamp = timestamp_raw
                    elif isinstance(timestamp_raw, str):
                        timestamp = datetime.fromisoformat(timestamp_raw)
                    else:
                        timestamp = datetime.utcnow()
                    
                    category_str = r.get("category", "context")
                    try:
                        category = MemoryCategory(category_str)
                    except ValueError:
                        category = MemoryCategory.CONTEXT
                    
                    results.append(MemorySearchResult(
                        memory_id=r.get("memory_id", ""),
                        content=r.get("content", ""),
                        similarity_score=similarity,
                        memory_type=MemoryType.RECALL,
                        timestamp=timestamp,
                        metadata={
                            "importance_score": r.get("importance_score", 0.5),
                            "session_id": r.get("session_id", ""),
                            "auto_created": r.get("auto_created", False),
                        },
                        category=category,
                        importance_score=r.get("importance_score", 0.5),
                    ))
            
            if include_archival:
                archival_results = await get_memory_repository().search_archival_memories(
                    query_embedding=query_embedding,
                    user_id=user_id,
                    top_k=top_k,
                )
                
                for r in archival_results:
                    similarity = r.get("similarity_score", 0.5)
                    if similarity < min_score:
                        continue
                    
                    created_at_raw = r.get("created_at")
                    if isinstance(created_at_raw, datetime):
                        timestamp = created_at_raw
                    elif isinstance(created_at_raw, str):
                        timestamp = datetime.fromisoformat(created_at_raw)
                    else:
                        timestamp = datetime.utcnow()
                    
                    content = r.get("content", "")
                    title = r.get("title", "")
                    
                    results.append(MemorySearchResult(
                        memory_id=r.get("memory_id", ""),
                        content=content or title,
                        similarity_score=similarity,
                        memory_type=MemoryType.ARCHIVAL,
                        timestamp=timestamp,
                        metadata={
                            "title": title,
                            "content_type": r.get("content_type", "note"),
                            "tags": r.get("tags", []),
                        },
                        category=MemoryCategory.INSIGHT,
                        importance_score=0.7,
                    ))
            
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            return results[:top_k]
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            return []
    
    async def build_memory_context(
        self,
        query: str,
        user_id: str = "default",
        max_memories: int = 5,
        max_tokens: int = 1000,
    ) -> str:
        core_memory = await self.get_core_memory(user_id)
        relevant_memories = await self.retrieve_relevant_memories(
            query=query,
            user_id=user_id,
            top_k=max_memories,
        )
        
        context_parts = []
        
        if core_memory:
            core_context = core_memory.to_context_string()
            if core_context:
                context_parts.append(f"[User Profile]\n{core_context}")
        
        if relevant_memories:
            recall_memories = [m for m in relevant_memories if m.memory_type == MemoryType.RECALL]
            archival_memories = [m for m in relevant_memories if m.memory_type == MemoryType.ARCHIVAL]
            
            if recall_memories:
                recall_context = "\n".join([
                    f"- {m.content[:200]}" for m in recall_memories[:3]
                ])
                context_parts.append(f"[Related Conversation History]\n{recall_context}")
            
            if archival_memories:
                archival_context = "\n".join([
                    f"- {m.metadata.get('title', m.content[:50])}: {m.content[:150]}"
                    for m in archival_memories[:3]
                ])
                context_parts.append(f"[Related Knowledge Base]\n{archival_context}")
        
        full_context = "\n\n".join(context_parts)
        
        if len(full_context) > max_tokens * 4:
            full_context = full_context[:max_tokens * 4]
        
        return full_context
    
    async def get_recent_memories(
        self,
        user_id: str = "default",
        days: int = 7,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        recall_memories = await get_memory_repository().get_recall_memories(
            user_id=user_id,
            limit=limit,
        )
        
        recent = []
        for m in recall_memories:
            try:
                timestamp_raw = getattr(m, 'timestamp', None) if hasattr(m, 'timestamp') else m.get("timestamp", "")
                if isinstance(timestamp_raw, datetime):
                    timestamp = timestamp_raw
                elif isinstance(timestamp_raw, str):
                    timestamp = datetime.fromisoformat(timestamp_raw)
                else:
                    timestamp = None
                
                if timestamp and timestamp >= cutoff_date:
                    recent.append(m)
            except (ValueError, TypeError):
                continue
        
        return recent
    
    async def get_memories_by_importance(
        self,
        user_id: str = "default",
        min_importance: float = 0.7,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        recall_memories = await get_memory_repository().get_recall_memories(
            user_id=user_id,
            limit=100,
        )
        
        important = []
        for m in recall_memories:
            importance = getattr(m, 'importance_score', 0) if hasattr(m, 'importance_score') else m.get("importance_score", 0)
            if importance >= min_importance:
                important.append(m)
        
        return important[:limit]
