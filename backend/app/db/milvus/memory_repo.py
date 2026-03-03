import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pymilvus import Collection

from app.db.base import MemoryRepository as BaseMemoryRepository
from app.db.milvus.client import milvus_client
from app.services.memory.types import (
    CoreMemory,
    RecallMemory,
    ArchivalMemory,
    MemoryStats,
)

logger = logging.getLogger(__name__)


class MilvusMemoryRepository(BaseMemoryRepository):
    """Repository for memory storage in Milvus."""
    
    def __init__(self):
        self._core_collection: Optional[Collection] = None
        self._recall_collection: Optional[Collection] = None
        self._archival_collection: Optional[Collection] = None
        self._core_memory_cache: Dict[str, CoreMemory] = {}
    
    def _get_core_collection(self) -> Collection:
        if not self._core_collection:
            self._core_collection = milvus_client.get_collection("core_memories")
        return self._core_collection
    
    def _get_recall_collection(self) -> Collection:
        if not self._recall_collection:
            self._recall_collection = milvus_client.get_collection("recall_memories")
        return self._recall_collection
    
    def _get_archival_collection(self) -> Collection:
        if not self._archival_collection:
            self._archival_collection = milvus_client.get_collection("archival_memories")
        return self._archival_collection
    
    async def get_core_memory(self, user_id: str = "default") -> Optional[CoreMemory]:
        if user_id in self._core_memory_cache:
            return self._core_memory_cache[user_id]
        
        try:
            collection = self._get_core_collection()
            collection.load()
            
            results = collection.query(
                expr=f'user_id == "{user_id}"',
                output_fields=["user_id", "research_interests", "preferred_domains", 
                              "frequently_used_skills", "language_preference", 
                              "summary_style", "custom_instructions", "created_at", "updated_at"],
            )
            
            if results:
                r = results[0]
                memory = CoreMemory(
                    user_id=r["user_id"],
                    research_interests=json.loads(r["research_interests"] or "[]"),
                    preferred_domains=json.loads(r["preferred_domains"] or "[]"),
                    frequently_used_skills=json.loads(r["frequently_used_skills"] or "[]"),
                    language_preference=r["language_preference"] or "en-US",
                    summary_style=r["summary_style"] or "detailed",
                    custom_instructions=r["custom_instructions"] or "",
                    created_at=datetime.fromisoformat(r["created_at"]) if r["created_at"] else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(r["updated_at"]) if r["updated_at"] else datetime.utcnow(),
                )
                self._core_memory_cache[user_id] = memory
                return memory
        except Exception as e:
            logger.error(f"Failed to get core memory: {e}")
        
        return None
    
    async def save_core_memory(self, memory: CoreMemory) -> bool:
        try:
            collection = self._get_core_collection()
            
            memory.updated_at = datetime.utcnow()
            if not memory.created_at:
                memory.created_at = datetime.utcnow()
            
            data = [
                [memory.user_id],
                [json.dumps(memory.research_interests)],
                [json.dumps(memory.preferred_domains)],
                [json.dumps(memory.frequently_used_skills)],
                [memory.language_preference],
                [memory.summary_style],
                [memory.custom_instructions],
                [memory.created_at.isoformat()],
                [memory.updated_at.isoformat()],
                [[0.0] * 8],
            ]
            
            collection.upsert(data)
            collection.flush()
            
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
            collection = self._get_recall_collection()
            
            insert_data = [
                [memory.memory_id],
                [memory.user_id],
                [memory.session_id],
                [memory.content[:4096] if memory.content else ""],
                [memory.embedding],
                [memory.importance_score],
                [memory.access_count],
                [memory.timestamp.isoformat()],
            ]
            
            collection.insert(insert_data)
            collection.flush()
            return True
        except Exception as e:
            logger.error(f"Failed to insert recall memory: {e}")
            return False
    
    async def get_recall_memories(self, user_id: str, limit: int = 50, offset: int = 0) -> List[RecallMemory]:
        try:
            collection = self._get_recall_collection()
            collection.load()
            
            results = collection.query(
                expr=f'user_id == "{user_id}"',
                output_fields=["memory_id", "user_id", "session_id", "content", 
                              "importance_score", "access_count", "timestamp"],
                limit=1000,
            )
            
            memories = [
                RecallMemory(
                    memory_id=r["memory_id"],
                    user_id=r["user_id"],
                    session_id=r["session_id"] or "",
                    content=r["content"] or "",
                    embedding=None,
                    importance_score=r["importance_score"] or 0.5,
                    access_count=r["access_count"] or 0,
                    timestamp=datetime.fromisoformat(r["timestamp"]) if r["timestamp"] else datetime.utcnow(),
                )
                for r in results
            ]
            
            memories.sort(key=lambda m: m.timestamp, reverse=True)
            
            return memories[offset:offset + limit]
        except Exception as e:
            logger.error(f"Failed to get recall memories: {e}")
            return []
    
    async def delete_recall_memory(self, memory_id: str, flush: bool = True) -> bool:
        try:
            collection = self._get_recall_collection()
            collection.delete(f'memory_id == "{memory_id}"')
            if flush:
                collection.flush()
            return True
        except Exception as e:
            logger.error(f"Failed to delete recall memory: {e}")
            return False
    
    async def delete_recall_memories_batch(self, memory_ids: list[str]) -> int:
        try:
            if not memory_ids:
                return 0
            
            collection = self._get_recall_collection()
            
            ids_str = ', '.join([f'"{mid}"' for mid in memory_ids])
            collection.delete(f'memory_id in [{ids_str}]')
            collection.flush()
            
            return len(memory_ids)
        except Exception as e:
            logger.error(f"Failed to delete recall memories batch: {e}")
            return 0
    
    async def search_recall_memories(self, query_embedding: List[float], user_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        try:
            collection = self._get_recall_collection()
            collection.load()
            
            results = collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param={"metric_type": "COSINE", "params": {"nprobe": 10}},
                limit=top_k,
                expr=f'user_id == "{user_id}"',
                output_fields=["memory_id", "user_id", "session_id", "content", 
                              "importance_score", "access_count", "timestamp"],
            )
            
            memories = []
            for hits in results:
                for hit in hits:
                    # hit.entity is a dict with 'entity' key containing the actual fields
                    entity_data = hit.entity
                    if isinstance(entity_data, dict) and 'entity' in entity_data:
                        fields = entity_data['entity']
                    else:
                        fields = entity_data
                    
                    memories.append({
                        "memory_id": fields.get("memory_id", ""),
                        "user_id": fields.get("user_id", ""),
                        "session_id": fields.get("session_id", "") or "",
                        "content": fields.get("content", "") or "",
                        "importance_score": fields.get("importance_score", 0.5) or 0.5,
                        "access_count": fields.get("access_count", 0) or 0,
                        "timestamp": fields.get("timestamp"),
                        "similarity_score": hit.score,
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
            collection = self._get_archival_collection()
            
            insert_data = [
                [memory.memory_id],
                [memory.user_id],
                [memory.content_type],
                [memory.title[:256] if memory.title else ""],
                [memory.content[:8192] if memory.content else ""],
                [memory.embedding],
                [json.dumps(memory.source_papers)],
                [json.dumps(memory.tags)],
                [memory.created_at.isoformat()],
                [memory.last_accessed.isoformat()],
            ]
            
            collection.insert(insert_data)
            collection.flush()
            return True
        except Exception as e:
            logger.error(f"Failed to insert archival memory: {e}")
            return False
    
    async def get_archival_memories(self, user_id: str, limit: int = 50, offset: int = 0) -> List[ArchivalMemory]:
        try:
            collection = self._get_archival_collection()
            collection.load()
            
            results = collection.query(
                expr=f'user_id == "{user_id}"',
                output_fields=["memory_id", "user_id", "content_type", "title", 
                              "content", "source_papers", "tags", "created_at", "last_accessed"],
                limit=1000,
            )
            
            memories = [
                ArchivalMemory(
                    memory_id=r["memory_id"],
                    user_id=r["user_id"],
                    content_type=r["content_type"] or "note",
                    title=r["title"] or "",
                    content=r["content"] or "",
                    embedding=None,
                    source_papers=json.loads(r["source_papers"]) if r["source_papers"] else [],
                    tags=json.loads(r["tags"]) if r["tags"] else [],
                    created_at=datetime.fromisoformat(r["created_at"]) if r["created_at"] else datetime.utcnow(),
                    last_accessed=datetime.fromisoformat(r["last_accessed"]) if r["last_accessed"] else datetime.utcnow(),
                )
                for r in results
            ]
            
            memories.sort(key=lambda m: m.created_at, reverse=True)
            
            return memories[offset:offset + limit]
        except Exception as e:
            logger.error(f"Failed to get archival memories: {e}")
            return []
    
    async def delete_archival_memory(self, memory_id: str, flush: bool = True) -> bool:
        try:
            collection = self._get_archival_collection()
            collection.delete(f'memory_id == "{memory_id}"')
            if flush:
                collection.flush()
            return True
        except Exception as e:
            logger.error(f"Failed to delete archival memory: {e}")
            return False
    
    async def delete_archival_memories_batch(self, memory_ids: list[str]) -> int:
        try:
            if not memory_ids:
                return 0
            
            collection = self._get_archival_collection()
            
            ids_str = ', '.join([f'"{mid}"' for mid in memory_ids])
            collection.delete(f'memory_id in [{ids_str}]')
            collection.flush()
            
            return len(memory_ids)
        except Exception as e:
            logger.error(f"Failed to delete archival memories batch: {e}")
            return 0
    
    async def search_archival_memories(self, query_embedding: List[float], user_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        try:
            collection = self._get_archival_collection()
            collection.load()
            
            results = collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param={"metric_type": "COSINE", "params": {"nprobe": 10}},
                limit=top_k,
                expr=f'user_id == "{user_id}"',
                output_fields=["memory_id", "user_id", "content_type", "title", 
                              "content", "source_papers", "tags", "created_at", "last_accessed"],
            )
            
            memories = []
            for hits in results:
                for hit in hits:
                    # hit.entity is a dict with 'entity' key containing the actual fields
                    entity_data = hit.entity
                    if isinstance(entity_data, dict) and 'entity' in entity_data:
                        fields = entity_data['entity']
                    else:
                        fields = entity_data
                    
                    source_papers_raw = fields.get("source_papers", "[]")
                    tags_raw = fields.get("tags", "[]")
                    
                    memories.append({
                        "memory_id": fields.get("memory_id", ""),
                        "user_id": fields.get("user_id", ""),
                        "content_type": fields.get("content_type", "note") or "note",
                        "title": fields.get("title", "") or "",
                        "content": fields.get("content", "") or "",
                        "source_papers": json.loads(source_papers_raw) if source_papers_raw else [],
                        "tags": json.loads(tags_raw) if tags_raw else [],
                        "created_at": fields.get("created_at"),
                        "last_accessed": fields.get("last_accessed"),
                        "similarity_score": hit.score,
                    })
            return memories
        except Exception as e:
            logger.error(f"Failed to search archival memories: {e}")
            return []
    
    async def get_memory_stats(self, user_id: str) -> MemoryStats:
        try:
            recall_collection = self._get_recall_collection()
            recall_collection.load()
            recall_results = recall_collection.query(
                expr=f'user_id == "{user_id}"',
                output_fields=["memory_id"],
            )
            recall_count = len(recall_results)
            
            archival_collection = self._get_archival_collection()
            archival_collection.load()
            archival_results = archival_collection.query(
                expr=f'user_id == "{user_id}"',
                output_fields=["memory_id"],
            )
            archival_count = len(archival_results)
            
            core = await self.get_core_memory(user_id)
            
            return MemoryStats(
                total_memories=recall_count + archival_count,
                recall_memory_count=recall_count,
                archival_memory_count=archival_count,
                core_memory_exists=core is not None,
            )
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return MemoryStats(
                total_memories=0,
                recall_memory_count=0,
                archival_memory_count=0,
                core_memory_exists=False,
            )
    
    async def clear_all_memories(self, user_id: str) -> bool:
        try:
            recall_collection = self._get_recall_collection()
            recall_collection.delete(f'user_id == "{user_id}"')
            recall_collection.flush()
            
            archival_collection = self._get_archival_collection()
            archival_collection.delete(f'user_id == "{user_id}"')
            archival_collection.flush()
            
            core_collection = self._get_core_collection()
            core_collection.delete(f'user_id == "{user_id}"')
            core_collection.flush()
            
            if user_id in self._core_memory_cache:
                del self._core_memory_cache[user_id]
            
            return True
        except Exception as e:
            logger.error(f"Failed to clear all memories: {e}")
            return False
    
    async def clear_core_memory(self, user_id: str) -> bool:
        try:
            core_collection = self._get_core_collection()
            core_collection.delete(f'user_id == "{user_id}"')
            core_collection.flush()
            
            if user_id in self._core_memory_cache:
                del self._core_memory_cache[user_id]
            
            return True
        except Exception as e:
            logger.error(f"Failed to clear core memory: {e}")
            return False
    
    async def clear_recall_memories(self, user_id: str) -> bool:
        try:
            recall_collection = self._get_recall_collection()
            recall_collection.delete(f'user_id == "{user_id}"')
            recall_collection.flush()
            
            return True
        except Exception as e:
            logger.error(f"Failed to clear recall memories: {e}")
            return False
    
    async def clear_archival_memories(self, user_id: str) -> bool:
        try:
            archival_collection = self._get_archival_collection()
            archival_collection.delete(f'user_id == "{user_id}"')
            archival_collection.flush()
            
            return True
        except Exception as e:
            logger.error(f"Failed to clear archival memories: {e}")
            return False
