import logging
from typing import Optional, Tuple
from datetime import datetime

from .types import (
    RecallMemory,
    MemoryConfig,
    MemoryExtractionResult,
    ShouldSaveResult,
    MemoryCategory,
)
from .extractor import MemoryExtractor
from app.services.embedding_service import embedding_service
from app.db.factory import get_memory_repository

logger = logging.getLogger(__name__)


class AutoCaptureService:
    def __init__(self):
        self.extractor = MemoryExtractor()
        self.embedding_service = embedding_service

    async def capture_conversation(
        self,
        user_id: str,
        session_id: str,
        user_message: str,
        assistant_message: str,
        config: MemoryConfig,
    ) -> Tuple[Optional[RecallMemory], Optional[MemoryExtractionResult]]:
        if not config.auto_capture:
            return None, None

        combined = f"User: {user_message}\nAssistant: {assistant_message}"
        if len(combined) > config.capture_max_chars:
            combined = combined[:config.capture_max_chars] + "..."

        try:
            should_save_result = await self.extractor.should_save(combined)
            if not should_save_result.should_save:
                logger.debug(f"Conversation not worth saving: {should_save_result.reason}")
                return None, None

            current_core = None
            if config.extract:
                current_core = await get_memory_repository().get_core_memory(user_id)

            extraction = await self.extractor.extract_from_conversation(
                user_message=user_message,
                assistant_message=assistant_message,
                current_core_memory=current_core,
            )

            embedding, _ = self.embedding_service.encode(combined)

            memory = RecallMemory(
                user_id=user_id,
                session_id=session_id,
                content=combined,
                embedding=embedding,
                importance_score=extraction.importance_score,
                category=should_save_result.category,
                auto_created=True,
                metadata={
                    "extraction": {
                        "user_preferences": extraction.user_preferences,
                        "research_interests": extraction.research_interests,
                        "important_facts": extraction.important_facts,
                    },
                    "capture_reason": should_save_result.reason,
                },
                timestamp=datetime.utcnow(),
            )

            await get_memory_repository().insert_recall_memory(memory)
            logger.info(f"Auto-captured memory: {memory.memory_id}")

            if config.extract and extraction.should_update_core and current_core:
                updated_core = self.extractor.update_core_memory(current_core, extraction)
                await get_memory_repository().save_core_memory(updated_core)
                logger.info(f"Updated core memory for user: {user_id}")

            return memory, extraction

        except Exception as e:
            logger.error(f"Failed to auto-capture conversation: {e}")
            return None, None

    async def manual_store(
        self,
        user_id: str,
        text: str,
        category: Optional[MemoryCategory] = None,
        importance: Optional[float] = None,
    ) -> Optional[RecallMemory]:
        try:
            embedding, _ = self.embedding_service.encode(text)

            memory = RecallMemory(
                user_id=user_id,
                content=text,
                embedding=embedding,
                importance_score=importance or 0.5,
                category=category or MemoryCategory.FACT,
                auto_created=False,
            )

            await get_memory_repository().insert_recall_memory(memory)
            logger.info(f"Manually stored memory: {memory.memory_id}")
            return memory

        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return None
