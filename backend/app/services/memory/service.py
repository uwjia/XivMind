import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.db.factory import get_memory_repository
from app.services.memory.types import (
    CoreMemory,
    RecallMemory,
    ArchivalMemory,
    MemoryExtractionResult,
    MemoryStats,
    MemorySearchResult,
    CoreMemoryUpdate,
    RecallMemoryCreate,
    ArchivalMemoryCreate,
)
from app.services.memory.extractor import MemoryExtractor
from app.services.memory.retriever import MemoryRetriever
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class MemoryService:
    """Main service for managing user memories."""
    
    def __init__(self):
        self.extractor = MemoryExtractor()
        self.retriever = MemoryRetriever()
        self.embedding_service = EmbeddingService()
    
    async def get_core_memory(self, user_id: str = "default") -> Optional[CoreMemory]:
        return await get_memory_repository().get_core_memory(user_id)
    
    async def update_core_memory(
        self,
        user_id: str,
        update: CoreMemoryUpdate,
    ) -> CoreMemory:
        current = await self.get_core_memory(user_id)
        
        if not current:
            current = CoreMemory(user_id=user_id)
        
        if update.research_interests is not None:
            current.research_interests = update.research_interests
        if update.preferred_domains is not None:
            current.preferred_domains = update.preferred_domains
        if update.frequently_used_skills is not None:
            current.frequently_used_skills = update.frequently_used_skills
        if update.language_preference is not None:
            current.language_preference = update.language_preference
        if update.summary_style is not None:
            current.summary_style = update.summary_style
        if update.custom_instructions is not None:
            current.custom_instructions = update.custom_instructions
        
        current.updated_at = datetime.utcnow()
        await get_memory_repository().save_core_memory(current)
        
        return current
    
    async def process_conversation(
        self,
        user_id: str,
        session_id: str,
        user_message: str,
        assistant_message: str,
        extract: bool = False,
    ) -> MemoryExtractionResult:
        current_core = await self.get_core_memory(user_id)
        
        extraction = await self.extractor.extract_from_conversation(
            user_message=user_message,
            assistant_message=assistant_message,
            current_core_memory=current_core,
        )
        
        combined_content = f"User: {user_message}\nAssistant: {assistant_message}"
        
        try:
            embedding, _ = self.embedding_service.encode(combined_content)
        except Exception as e:
            logger.warning(f"Failed to get embedding for conversation: {e}")
            embedding = None
        
        recall_memory = self.extractor.create_recall_memory(
            user_id=user_id,
            session_id=session_id,
            content=combined_content,
            embedding=embedding,
            importance_score=extraction.importance_score,
            metadata={
                "user_preferences": extraction.user_preferences,
                "research_interests": extraction.research_interests,
            },
        )
        
        await get_memory_repository().insert_recall_memory(recall_memory)
        
        if extract and extraction.should_update_core and current_core:
            updated_core = self.extractor.update_core_memory(current_core, extraction)
            await get_memory_repository().save_core_memory(updated_core)
        
        return extraction
    
    async def create_recall_memory(
        self,
        user_id: str,
        data: RecallMemoryCreate,
    ) -> RecallMemory:
        try:
            embedding, _ = self.embedding_service.encode(data.content)
        except Exception as e:
            logger.warning(f"Failed to get embedding: {e}")
            embedding = None
        
        memory = RecallMemory(
            user_id=user_id,
            session_id=data.session_id,
            content=data.content,
            embedding=embedding,
            importance_score=data.importance_score,
            metadata=data.metadata,
        )
        
        await get_memory_repository().insert_recall_memory(memory)
        return memory
    
    async def search_memories(
        self,
        query: str,
        user_id: str = "default",
        top_k: int = 5,
    ) -> List[MemorySearchResult]:
        return await self.retriever.retrieve_relevant_memories(
            query=query,
            user_id=user_id,
            top_k=top_k,
        )
    
    async def get_recall_memories(
        self,
        user_id: str = "default",
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        return await get_memory_repository().get_recall_memories(user_id, limit, offset)
    
    async def delete_recall_memory(self, memory_id: str, flush: bool = True) -> bool:
        return await get_memory_repository().delete_recall_memory(memory_id, flush)
    
    async def delete_recall_memories_batch(self, memory_ids: List[str]) -> int:
        return await get_memory_repository().delete_recall_memories_batch(memory_ids)
    
    async def create_archival_memory(
        self,
        user_id: str,
        data: ArchivalMemoryCreate,
    ) -> ArchivalMemory:
        try:
            embedding, _ = self.embedding_service.encode(
                f"{data.title} {data.content}"
            )
        except Exception as e:
            logger.warning(f"Failed to get embedding: {e}")
            embedding = None
        
        memory = ArchivalMemory(
            user_id=user_id,
            content_type=data.content_type,
            title=data.title,
            content=data.content,
            embedding=embedding,
            source_papers=data.source_papers,
            tags=data.tags,
        )
        
        await get_memory_repository().insert_archival_memory(memory)
        return memory
    
    async def get_archival_memories(
        self,
        user_id: str = "default",
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        return await get_memory_repository().get_archival_memories(user_id, limit, offset)
    
    async def delete_archival_memory(self, memory_id: str, flush: bool = True) -> bool:
        return await get_memory_repository().delete_archival_memory(memory_id, flush)
    
    async def delete_archival_memories_batch(self, memory_ids: List[str]) -> int:
        return await get_memory_repository().delete_archival_memories_batch(memory_ids)
    
    async def get_memory_stats(self, user_id: str = "default") -> MemoryStats:
        return await get_memory_repository().get_memory_stats(user_id)
    
    async def clear_all_memories(self, user_id: str = "default") -> bool:
        return await get_memory_repository().clear_all_memories(user_id)
    
    async def clear_core_memory(self, user_id: str = "default") -> bool:
        return await get_memory_repository().clear_core_memory(user_id)
    
    async def clear_recall_memories(self, user_id: str = "default") -> bool:
        return await get_memory_repository().clear_recall_memories(user_id)
    
    async def clear_archival_memories(self, user_id: str = "default") -> bool:
        return await get_memory_repository().clear_archival_memories(user_id)
    
    async def build_context_for_query(
        self,
        query: str,
        user_id: str = "default",
    ) -> str:
        return await self.retriever.build_memory_context(
            query=query,
            user_id=user_id,
        )
    
    async def get_user_profile_summary(self, user_id: str = "default") -> str:
        core = await self.get_core_memory(user_id)
        stats = await self.get_memory_stats(user_id)
        
        parts = []
        
        if core:
            parts.append(f"User Profile: {core.to_context_string()}")
        else:
            parts.append("User Profile: Not available")
        
        parts.append(f"Memory Statistics: {stats.total_memories} total memories")
        parts.append(f"  - Conversation Memories: {stats.recall_memory_count}")
        parts.append(f"  - Knowledge Base Memories: {stats.archival_memory_count}")
        
        return "\n".join(parts)
    
    async def record_skill_usage(
        self,
        user_id: str,
        skill_name: str,
    ) -> None:
        core = await self.get_core_memory(user_id)
        
        if not core:
            core = CoreMemory(user_id=user_id)
        
        if skill_name not in core.frequently_used_skills:
            core.frequently_used_skills.append(skill_name)
            await get_memory_repository().save_core_memory(core)
    
    async def get_recommended_skills(self, user_id: str = "default") -> List[str]:
        core = await self.get_core_memory(user_id)
        
        if core and core.frequently_used_skills:
            return core.frequently_used_skills[:5]
        
        return []


memory_service = MemoryService()
