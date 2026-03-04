import logging
from datetime import datetime, timedelta
from typing import List, Tuple

from .types import MemoryConfig, RecallMemory
from app.db.factory import get_memory_repository

logger = logging.getLogger(__name__)


class AutoForgetService:
    async def cleanup_expired_memories(
        self,
        user_id: str,
        config: MemoryConfig,
    ) -> int:
        cutoff_date = datetime.utcnow() - timedelta(days=config.auto_forget_days)

        try:
            deleted = await get_memory_repository().delete_recall_memories_by_criteria(
                user_id=user_id,
                before_date=cutoff_date,
                max_importance=config.importance_threshold,
                auto_created_only=True,
            )

            logger.info(f"Auto-forgot {deleted} expired memories for user {user_id}")
            return deleted

        except Exception as e:
            logger.error(f"Failed to cleanup expired memories: {e}")
            return 0

    async def cleanup_by_ttl(
        self,
        user_id: str,
    ) -> int:
        try:
            deleted = await get_memory_repository().delete_expired_ttl_memories(
                user_id=user_id,
            )

            logger.info(f"Cleaned up {deleted} TTL-expired memories for user {user_id}")
            return deleted

        except Exception as e:
            logger.error(f"Failed to cleanup TTL memories: {e}")
            return 0

    async def get_memories_for_cleanup(
        self,
        user_id: str,
        config: MemoryConfig,
    ) -> List[Tuple[str, str, float]]:
        cutoff_date = datetime.utcnow() - timedelta(days=config.auto_forget_days)

        try:
            memories = await get_memory_repository().get_recall_memories_for_cleanup(
                user_id=user_id,
                before_date=cutoff_date,
                max_importance=config.importance_threshold,
            )

            return [(m.memory_id, m.content[:100], m.importance_score) for m in memories]

        except Exception as e:
            logger.error(f"Failed to get memories for cleanup: {e}")
            return []

    async def forget_memory(
        self,
        memory_id: str,
        user_id: str,
    ) -> bool:
        try:
            success = await get_memory_repository().delete_recall_memory(
                memory_id=memory_id,
                user_id=user_id,
            )

            if success:
                logger.info(f"Forgot memory: {memory_id}")
            return success

        except Exception as e:
            logger.error(f"Failed to forget memory {memory_id}: {e}")
            return False

    async def forget_all_auto_created(
        self,
        user_id: str,
    ) -> int:
        try:
            deleted = await get_memory_repository().delete_recall_memories_by_criteria(
                user_id=user_id,
                auto_created_only=True,
            )

            logger.info(f"Forgot all {deleted} auto-created memories for user {user_id}")
            return deleted

        except Exception as e:
            logger.error(f"Failed to forget all auto-created memories: {e}")
            return 0
