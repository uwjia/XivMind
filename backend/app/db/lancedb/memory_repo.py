import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.db.base import MemoryRepository as BaseMemoryRepository
from app.db.lancedb.client import lancedb_client
from app.services.memory.types import (
    CoreMemory,
    RecallMemory,
    ArchivalMemory,
    MemoryStats,
    MemoryConfig,
    MemoryCategory,
)

logger = logging.getLogger(__name__)


class LanceDBMemoryRepository(BaseMemoryRepository):
    """LanceDB implementation for Memory storage."""
    
    def __init__(self, db_path: str = None):
        self._core_table = None
        self._recall_table = None
        self._archival_table = None
        self._config_table = None
        self._core_memory_cache: Dict[str, CoreMemory] = {}
    
    def _get_core_table(self):
        if self._core_table is None:
            self._core_table = lancedb_client.get_table("core_memories")
        return self._core_table
    
    def _get_recall_table(self):
        if self._recall_table is None:
            self._recall_table = lancedb_client.get_table("recall_memories")
        return self._recall_table
    
    def _get_archival_table(self):
        if self._archival_table is None:
            self._archival_table = lancedb_client.get_table("archival_memories")
        return self._archival_table
    
    def _get_config_table(self):
        if self._config_table is None:
            self._config_table = lancedb_client.get_table("memory_config")
        return self._config_table
    
    async def get_core_memory(self, user_id: str = "default") -> Optional[CoreMemory]:
        if user_id in self._core_memory_cache:
            return self._core_memory_cache[user_id]
        
        try:
            table = self._get_core_table()
            results = table.search().where(f"user_id = '{user_id}'").limit(1).to_pandas()
            
            if len(results) == 0:
                return None
            
            row = results.iloc[0]
            memory = CoreMemory(
                user_id=row["user_id"],
                research_interests=json.loads(row["research_interests"]) if row["research_interests"] else [],
                preferred_domains=json.loads(row["preferred_domains"]) if row["preferred_domains"] else [],
                frequently_used_skills=json.loads(row["frequently_used_skills"]) if row["frequently_used_skills"] else [],
                language_preference=row["language_preference"] or "en-US",
                summary_style=row["summary_style"] or "detailed",
                custom_instructions=row["custom_instructions"] or "",
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.utcnow(),
            )
            self._core_memory_cache[user_id] = memory
            return memory
        except Exception as e:
            logger.error(f"Failed to get core memory: {e}")
            return None
    
    async def save_core_memory(self, memory: CoreMemory) -> bool:
        try:
            table = self._get_core_table()
            
            memory.updated_at = datetime.utcnow()
            if not memory.created_at:
                memory.created_at = datetime.utcnow()
            
            table.delete(f"user_id = '{memory.user_id}'")
            
            record = {
                "user_id": memory.user_id,
                "research_interests": json.dumps(memory.research_interests),
                "preferred_domains": json.dumps(memory.preferred_domains),
                "frequently_used_skills": json.dumps(memory.frequently_used_skills),
                "language_preference": memory.language_preference,
                "summary_style": memory.summary_style,
                "custom_instructions": memory.custom_instructions,
                "created_at": memory.created_at.isoformat(),
                "updated_at": memory.updated_at.isoformat(),
                "embedding": [0.0] * 8,
            }
            
            table.add([record])
            
            self._core_memory_cache[memory.user_id] = memory
            return True
        except Exception as e:
            logger.error(f"Failed to save core memory: {e}")
            return False
    
    async def insert_recall_memory(self, memory: RecallMemory) -> bool:
        if not memory.embedding or len(memory.embedding) == 0:
            logger.warning(f"Skipping recall memory insert: missing embedding for {memory.memory_id}")
            return False
        
        try:
            table = self._get_recall_table()
            
            record = {
                "memory_id": memory.memory_id,
                "user_id": memory.user_id,
                "session_id": memory.session_id or "",
                "content": memory.content[:4096] if memory.content else "",
                "embedding": memory.embedding,
                "importance_score": memory.importance_score,
                "access_count": memory.access_count,
                "timestamp": memory.timestamp.isoformat(),
                "category": memory.category.value if hasattr(memory.category, 'value') else (memory.category or 'context'),
                "auto_created": memory.auto_created,
                "ttl_days": memory.ttl_days or 0,
                "metadata": json.dumps(memory.metadata) if memory.metadata else "{}",
            }
            
            table.add([record])
            return True
        except Exception as e:
            logger.error(f"Failed to insert recall memory: {e}")
            return False
    
    async def get_recall_memories(self, user_id: str, limit: int = 50, offset: int = 0) -> List[RecallMemory]:
        try:
            table = self._get_recall_table()
            results = table.search().where(f"user_id = '{user_id}'").to_pandas()
            
            memories = []
            for _, row in results.iterrows():
                memories.append(RecallMemory(
                    memory_id=row["memory_id"],
                    user_id=row["user_id"],
                    session_id=row["session_id"] or "",
                    content=row["content"] or "",
                    embedding=None,
                    importance_score=row["importance_score"] or 0.5,
                    access_count=row["access_count"] or 0,
                    timestamp=datetime.fromisoformat(row["timestamp"]) if row["timestamp"] else datetime.utcnow(),
                    category=MemoryCategory(row["category"]) if row.get("category") else MemoryCategory.CONTEXT,
                    auto_created=bool(row.get("auto_created", False)),
                    ttl_days=row.get("ttl_days") if row.get("ttl_days") else None,
                    metadata=json.loads(row["metadata"]) if row.get("metadata") else {},
                ))
            
            memories.sort(key=lambda m: m.timestamp, reverse=True)
            
            return memories[offset:offset + limit]
        except Exception as e:
            logger.error(f"Failed to get recall memories: {e}")
            return []
    
    async def delete_recall_memory(self, memory_id: str, flush: bool = True) -> bool:
        try:
            table = self._get_recall_table()
            table.delete(f"memory_id = '{memory_id}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete recall memory: {e}")
            return False
    
    async def delete_recall_memories_batch(self, memory_ids: list[str]) -> int:
        try:
            if not memory_ids:
                return 0
            
            table = self._get_recall_table()
            
            for mid in memory_ids:
                table.delete(f"memory_id = '{mid}'")
            
            return len(memory_ids)
        except Exception as e:
            logger.error(f"Failed to delete recall memories batch: {e}")
            return 0
    
    async def search_recall_memories(self, query_embedding: List[float], user_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        try:
            table = self._get_recall_table()
            
            results = table.search(
                query_embedding,
                vector_column_name="embedding"
            ).where(f"user_id = '{user_id}'").limit(top_k).to_pandas()
            
            memories = []
            for _, row in results.iterrows():
                memories.append({
                    "memory_id": row.get("memory_id", ""),
                    "user_id": row.get("user_id", ""),
                    "session_id": row.get("session_id", "") or "",
                    "content": row.get("content", "") or "",
                    "importance_score": row.get("importance_score", 0.5) or 0.5,
                    "access_count": row.get("access_count", 0) or 0,
                    "timestamp": row.get("timestamp"),
                    "category": row.get("category", "context") or "context",
                    "auto_created": row.get("auto_created", False) or False,
                    "ttl_days": row.get("ttl_days"),
                    "metadata": json.loads(row.get("metadata", "{}") or "{}"),
                    "similarity_score": 1 - row.get("_distance", 0),
                })
            
            return memories
        except Exception as e:
            logger.error(f"Failed to search recall memories: {e}")
            return []
    
    async def insert_archival_memory(self, memory: ArchivalMemory) -> bool:
        if not memory.embedding or len(memory.embedding) == 0:
            logger.warning(f"Skipping archival memory insert: missing embedding for {memory.memory_id}")
            return False
        
        try:
            table = self._get_archival_table()
            
            record = {
                "memory_id": memory.memory_id,
                "user_id": memory.user_id,
                "content_type": memory.content_type,
                "title": memory.title[:256] if memory.title else "",
                "content": memory.content[:8192] if memory.content else "",
                "embedding": memory.embedding,
                "source_papers": json.dumps(memory.source_papers),
                "tags": json.dumps(memory.tags),
                "created_at": memory.created_at.isoformat(),
                "last_accessed": memory.last_accessed.isoformat(),
            }
            
            table.add([record])
            return True
        except Exception as e:
            logger.error(f"Failed to insert archival memory: {e}")
            return False
    
    async def get_archival_memories(self, user_id: str, limit: int = 50, offset: int = 0) -> List[ArchivalMemory]:
        try:
            table = self._get_archival_table()
            results = table.search().where(f"user_id = '{user_id}'").to_pandas()
            
            memories = []
            for _, row in results.iterrows():
                memories.append(ArchivalMemory(
                    memory_id=row["memory_id"],
                    user_id=row["user_id"],
                    content_type=row["content_type"] or "note",
                    title=row["title"] or "",
                    content=row["content"] or "",
                    embedding=None,
                    source_papers=json.loads(row["source_papers"]) if row["source_papers"] else [],
                    tags=json.loads(row["tags"]) if row["tags"] else [],
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                    last_accessed=datetime.fromisoformat(row["last_accessed"]) if row["last_accessed"] else datetime.utcnow(),
                ))
            
            memories.sort(key=lambda m: m.created_at, reverse=True)
            
            return memories[offset:offset + limit]
        except Exception as e:
            logger.error(f"Failed to get archival memories: {e}")
            return []
    
    async def delete_archival_memory(self, memory_id: str, flush: bool = True) -> bool:
        try:
            table = self._get_archival_table()
            table.delete(f"memory_id = '{memory_id}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete archival memory: {e}")
            return False
    
    async def delete_archival_memories_batch(self, memory_ids: list[str]) -> int:
        try:
            if not memory_ids:
                return 0
            
            table = self._get_archival_table()
            
            for mid in memory_ids:
                table.delete(f"memory_id = '{mid}'")
            
            return len(memory_ids)
        except Exception as e:
            logger.error(f"Failed to delete archival memories batch: {e}")
            return 0
    
    async def search_archival_memories(self, query_embedding: List[float], user_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        try:
            table = self._get_archival_table()
            
            results = table.search(
                query_embedding,
                vector_column_name="embedding"
            ).where(f"user_id = '{user_id}'").limit(top_k).to_pandas()
            
            memories = []
            for _, row in results.iterrows():
                source_papers_raw = row.get("source_papers", "[]")
                tags_raw = row.get("tags", "[]")
                
                memories.append({
                    "memory_id": row.get("memory_id", ""),
                    "user_id": row.get("user_id", ""),
                    "content_type": row.get("content_type", "note") or "note",
                    "title": row.get("title", "") or "",
                    "content": row.get("content", "") or "",
                    "source_papers": json.loads(source_papers_raw) if source_papers_raw else [],
                    "tags": json.loads(tags_raw) if tags_raw else [],
                    "created_at": row.get("created_at"),
                    "last_accessed": row.get("last_accessed"),
                    "similarity_score": 1 - row.get("_distance", 0),
                })
            
            return memories
        except Exception as e:
            logger.error(f"Failed to search archival memories: {e}")
            return []
    
    async def get_memory_stats(self, user_id: str) -> MemoryStats:
        try:
            recall_table = self._get_recall_table()
            recall_results = recall_table.search().where(f"user_id = '{user_id}'").to_pandas()
            recall_count = len(recall_results)
            
            archival_table = self._get_archival_table()
            archival_results = archival_table.search().where(f"user_id = '{user_id}'").to_pandas()
            archival_count = len(archival_results)
            
            core = await self.get_core_memory(user_id)
            
            auto_created_count = 0
            by_category = {}
            
            if recall_count > 0:
                auto_created_count = recall_results["auto_created"].sum()
                
                for cat in recall_results["category"].unique():
                    by_category[cat] = len(recall_results[recall_results["category"] == cat])
            
            oldest = None
            newest = None
            
            if recall_count > 0:
                timestamps = [datetime.fromisoformat(t) for t in recall_results["timestamp"]]
                oldest = min(timestamps)
                newest = max(timestamps)
            
            return MemoryStats(
                core_memory_exists=core is not None,
                recall_memory_count=recall_count,
                archival_memory_count=archival_count,
                total_memories=recall_count + archival_count,
                oldest_memory=oldest,
                newest_memory=newest,
                auto_created_count=auto_created_count,
                by_category=by_category,
            )
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return MemoryStats(
                core_memory_exists=False,
                recall_memory_count=0,
                archival_memory_count=0,
                total_memories=0,
            )
    
    async def clear_all_memories(self, user_id: str) -> bool:
        try:
            recall_table = self._get_recall_table()
            recall_table.delete(f"user_id = '{user_id}'")
            
            archival_table = self._get_archival_table()
            archival_table.delete(f"user_id = '{user_id}'")
            
            core_table = self._get_core_table()
            core_table.delete(f"user_id = '{user_id}'")
            
            if user_id in self._core_memory_cache:
                del self._core_memory_cache[user_id]
            
            return True
        except Exception as e:
            logger.error(f"Failed to clear all memories: {e}")
            return False
    
    async def clear_core_memory(self, user_id: str) -> bool:
        try:
            table = self._get_core_table()
            table.delete(f"user_id = '{user_id}'")
            
            if user_id in self._core_memory_cache:
                del self._core_memory_cache[user_id]
            
            return True
        except Exception as e:
            logger.error(f"Failed to clear core memory: {e}")
            return False
    
    async def clear_recall_memories(self, user_id: str) -> bool:
        try:
            table = self._get_recall_table()
            table.delete(f"user_id = '{user_id}'")
            return True
        except Exception as e:
            logger.error(f"Failed to clear recall memories: {e}")
            return False
    
    async def clear_archival_memories(self, user_id: str) -> bool:
        try:
            table = self._get_archival_table()
            table.delete(f"user_id = '{user_id}'")
            return True
        except Exception as e:
            logger.error(f"Failed to clear archival memories: {e}")
            return False
    
    async def get_memory_config(self, user_id: str) -> MemoryConfig:
        try:
            table = self._get_config_table()
            results = table.search().where(f"user_id = '{user_id}'").limit(1).to_pandas()
            
            if len(results) == 0:
                return MemoryConfig()
            
            row = results.iloc[0]
            return MemoryConfig(
                auto_capture=bool(row.get("auto_capture", True)),
                auto_recall=bool(row.get("auto_recall", True)),
                capture_max_chars=row.get("capture_max_chars", 500),
                recall_top_k=row.get("recall_top_k", 5),
                recall_min_score=round(float(row.get("recall_min_score", 0.7)), 2),
                auto_forget_days=row.get("auto_forget_days", 30),
                importance_threshold=round(float(row.get("importance_threshold", 0.3)), 2),
                extract=bool(row.get("extract", False)),
            )
        except Exception as e:
            logger.error(f"Failed to get memory config: {e}")
            return MemoryConfig()
    
    async def save_memory_config(self, user_id: str, config: MemoryConfig) -> bool:
        try:
            table = self._get_config_table()
            
            table.delete(f"user_id = '{user_id}'")
            
            record = {
                "user_id": user_id,
                "auto_capture": config.auto_capture,
                "auto_recall": config.auto_recall,
                "capture_max_chars": config.capture_max_chars,
                "recall_top_k": config.recall_top_k,
                "recall_min_score": config.recall_min_score,
                "auto_forget_days": config.auto_forget_days,
                "importance_threshold": config.importance_threshold,
                "extract": config.extract,
                "embedding": [0.0] * 8,
            }
            table.add([record])
            
            return True
        except Exception as e:
            logger.error(f"Failed to save memory config: {e}")
            return False
    
    async def delete_recall_memories_by_criteria(
        self,
        user_id: str,
        before_date=None,
        max_importance=None,
        auto_created_only: bool = False,
    ) -> int:
        try:
            table = self._get_recall_table()
            df = table.search().where(f"user_id = '{user_id}'").to_pandas()
            
            if auto_created_only:
                df = df[df["auto_created"] == True]
            
            if before_date:
                df = df[df["timestamp"] < before_date.isoformat()]
            
            if max_importance is not None:
                df = df[df["importance_score"] <= max_importance]
            
            count = len(df)
            
            if count > 0:
                for memory_id in df["memory_id"].tolist():
                    table.delete(f"memory_id = '{memory_id}'")
            
            return count
        except Exception as e:
            logger.error(f"Failed to delete recall memories by criteria: {e}")
            return 0
