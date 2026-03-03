import aiosqlite
import json
import numpy as np
from datetime import datetime
from typing import Optional, List
from app.db.base import MemoryRepository
from app.services.memory.types import CoreMemory, RecallMemory, ArchivalMemory, MemoryStats
from app.config import get_settings


class SQLiteMemoryRepository(MemoryRepository):
    """SQLite implementation for Memory storage."""
    
    def __init__(self, db_path: str = None):
        self._db_path = db_path
    
    @property
    def db_path(self) -> str:
        if not self._db_path:
            self._db_path = get_settings().SQLITE_DB_PATH
        return self._db_path
    
    async def _ensure_tables(self, db):
        await db.execute("""
            CREATE TABLE IF NOT EXISTS core_memories (
                user_id TEXT PRIMARY KEY,
                research_interests TEXT,
                preferred_domains TEXT,
                frequently_used_skills TEXT,
                language_preference TEXT,
                summary_style TEXT,
                custom_instructions TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS recall_memories (
                memory_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_id TEXT,
                content TEXT,
                embedding BLOB,
                importance_score REAL,
                access_count INTEGER,
                timestamp TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS archival_memories (
                memory_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                content_type TEXT,
                title TEXT,
                content TEXT,
                embedding BLOB,
                source_papers TEXT,
                tags TEXT,
                created_at TEXT,
                last_accessed TEXT
            )
        """)
        await db.commit()
    
    async def get_core_memory(self, user_id: str) -> Optional[CoreMemory]:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_tables(db)
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM core_memories WHERE user_id = ?",
                (user_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                return CoreMemory(
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
        return None
    
    async def save_core_memory(self, memory: CoreMemory) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_tables(db)
            memory.updated_at = datetime.utcnow()
            
            await db.execute("""
                INSERT OR REPLACE INTO core_memories 
                (user_id, research_interests, preferred_domains, frequently_used_skills,
                 language_preference, summary_style, custom_instructions, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.user_id,
                json.dumps(memory.research_interests),
                json.dumps(memory.preferred_domains),
                json.dumps(memory.frequently_used_skills),
                memory.language_preference,
                memory.summary_style,
                memory.custom_instructions,
                memory.created_at.isoformat(),
                memory.updated_at.isoformat(),
            ))
            await db.commit()
        return True
    
    async def insert_recall_memory(self, memory: RecallMemory) -> bool:
        if not memory.embedding or len(memory.embedding) == 0:
            return False
        
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_tables(db)
            
            await db.execute("""
                INSERT INTO recall_memories 
                (memory_id, user_id, session_id, content, embedding, importance_score, access_count, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.memory_id,
                memory.user_id,
                memory.session_id,
                memory.content[:4096] if memory.content else "",
                json.dumps(memory.embedding),
                memory.importance_score,
                memory.access_count,
                memory.timestamp.isoformat(),
            ))
            await db.commit()
        return True
    
    async def get_recall_memories(self, user_id: str, limit: int = 50, offset: int = 0) -> List[RecallMemory]:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_tables(db)
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM recall_memories WHERE user_id = ? ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                (user_id, limit, offset)
            )
            rows = await cursor.fetchall()
            
            return [
                RecallMemory(
                    memory_id=row["memory_id"],
                    user_id=row["user_id"],
                    session_id=row["session_id"] or "",
                    content=row["content"] or "",
                    embedding=json.loads(row["embedding"]) if row["embedding"] else None,
                    importance_score=row["importance_score"] or 0.5,
                    access_count=row["access_count"] or 0,
                    timestamp=datetime.fromisoformat(row["timestamp"]) if row["timestamp"] else datetime.utcnow(),
                )
                for row in rows
            ]
    
    async def delete_recall_memory(self, memory_id: str, flush: bool = True) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_tables(db)
            await db.execute("DELETE FROM recall_memories WHERE memory_id = ?", (memory_id,))
            await db.commit()
        return True
    
    async def delete_recall_memories_batch(self, memory_ids: List[str]) -> int:
        if not memory_ids:
            return 0
        
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_tables(db)
            placeholders = ', '.join(['?' for _ in memory_ids])
            await db.execute(f"DELETE FROM recall_memories WHERE memory_id IN ({placeholders})", memory_ids)
            await db.commit()
        return len(memory_ids)
    
    async def search_recall_memories(self, query_embedding: List[float], user_id: str, top_k: int = 10) -> List[RecallMemory]:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_tables(db)
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM recall_memories WHERE user_id = ?",
                (user_id,)
            )
            rows = await cursor.fetchall()
            
            results = []
            query_vec = np.array(query_embedding)
            
            for row in rows:
                if row["embedding"]:
                    stored_vec = np.array(json.loads(row["embedding"]))
                    similarity = np.dot(query_vec, stored_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(stored_vec))
                    results.append((similarity, row))
            
            results.sort(key=lambda x: x[0], reverse=True)
            
            return [
                RecallMemory(
                    memory_id=row["memory_id"],
                    user_id=row["user_id"],
                    session_id=row["session_id"] or "",
                    content=row["content"] or "",
                    embedding=json.loads(row["embedding"]) if row["embedding"] else None,
                    importance_score=row["importance_score"] or 0.5,
                    access_count=row["access_count"] or 0,
                    timestamp=datetime.fromisoformat(row["timestamp"]) if row["timestamp"] else datetime.utcnow(),
                )
                for _, row in results[:top_k]
            ]
    
    async def insert_archival_memory(self, memory: ArchivalMemory) -> bool:
        if not memory.embedding or len(memory.embedding) == 0:
            return False
        
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_tables(db)
            
            await db.execute("""
                INSERT INTO archival_memories 
                (memory_id, user_id, content_type, title, content, embedding, source_papers, tags, created_at, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.memory_id,
                memory.user_id,
                memory.content_type,
                memory.title[:256] if memory.title else "",
                memory.content[:8192] if memory.content else "",
                json.dumps(memory.embedding),
                json.dumps(memory.source_papers),
                json.dumps(memory.tags),
                memory.created_at.isoformat(),
                memory.last_accessed.isoformat(),
            ))
            await db.commit()
        return True
    
    async def get_archival_memories(self, user_id: str, limit: int = 50, offset: int = 0) -> List[ArchivalMemory]:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_tables(db)
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM archival_memories WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (user_id, limit, offset)
            )
            rows = await cursor.fetchall()
            
            return [
                ArchivalMemory(
                    memory_id=row["memory_id"],
                    user_id=row["user_id"],
                    content_type=row["content_type"] or "note",
                    title=row["title"] or "",
                    content=row["content"] or "",
                    embedding=json.loads(row["embedding"]) if row["embedding"] else None,
                    source_papers=json.loads(row["source_papers"]) if row["source_papers"] else [],
                    tags=json.loads(row["tags"]) if row["tags"] else [],
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                    last_accessed=datetime.fromisoformat(row["last_accessed"]) if row["last_accessed"] else datetime.utcnow(),
                )
                for row in rows
            ]
    
    async def delete_archival_memory(self, memory_id: str, flush: bool = True) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_tables(db)
            await db.execute("DELETE FROM archival_memories WHERE memory_id = ?", (memory_id,))
            await db.commit()
        return True
    
    async def delete_archival_memories_batch(self, memory_ids: List[str]) -> int:
        if not memory_ids:
            return 0
        
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_tables(db)
            placeholders = ', '.join(['?' for _ in memory_ids])
            await db.execute(f"DELETE FROM archival_memories WHERE memory_id IN ({placeholders})", memory_ids)
            await db.commit()
        return len(memory_ids)
    
    async def search_archival_memories(self, query_embedding: List[float], user_id: str, top_k: int = 10) -> List[ArchivalMemory]:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_tables(db)
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM archival_memories WHERE user_id = ?",
                (user_id,)
            )
            rows = await cursor.fetchall()
            
            results = []
            query_vec = np.array(query_embedding)
            
            for row in rows:
                if row["embedding"]:
                    stored_vec = np.array(json.loads(row["embedding"]))
                    similarity = np.dot(query_vec, stored_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(stored_vec))
                    results.append((similarity, row))
            
            results.sort(key=lambda x: x[0], reverse=True)
            
            return [
                ArchivalMemory(
                    memory_id=row["memory_id"],
                    user_id=row["user_id"],
                    content_type=row["content_type"] or "note",
                    title=row["title"] or "",
                    content=row["content"] or "",
                    embedding=json.loads(row["embedding"]) if row["embedding"] else None,
                    source_papers=json.loads(row["source_papers"]) if row["source_papers"] else [],
                    tags=json.loads(row["tags"]) if row["tags"] else [],
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                    last_accessed=datetime.fromisoformat(row["last_accessed"]) if row["last_accessed"] else datetime.utcnow(),
                )
                for _, row in results[:top_k]
            ]
    
    async def get_memory_stats(self, user_id: str) -> MemoryStats:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_tables(db)
            
            cursor = await db.execute(
                "SELECT COUNT(*) FROM recall_memories WHERE user_id = ?",
                (user_id,)
            )
            recall_count = (await cursor.fetchone())[0]
            
            cursor = await db.execute(
                "SELECT COUNT(*) FROM archival_memories WHERE user_id = ?",
                (user_id,)
            )
            archival_count = (await cursor.fetchone())[0]
            
            core = await self.get_core_memory(user_id)
            
            return MemoryStats(
                total_memories=recall_count + archival_count,
                recall_memory_count=recall_count,
                archival_memory_count=archival_count,
                core_memory_exists=core is not None,
            )
    
    async def clear_all_memories(self, user_id: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_tables(db)
            
            await db.execute("DELETE FROM recall_memories WHERE user_id = ?", (user_id,))
            await db.execute("DELETE FROM archival_memories WHERE user_id = ?", (user_id,))
            await db.execute("DELETE FROM core_memories WHERE user_id = ?", (user_id,))
            await db.commit()
        return True
    
    async def clear_core_memory(self, user_id: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_tables(db)
            await db.execute("DELETE FROM core_memories WHERE user_id = ?", (user_id,))
            await db.commit()
        return True
    
    async def clear_recall_memories(self, user_id: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_tables(db)
            await db.execute("DELETE FROM recall_memories WHERE user_id = ?", (user_id,))
            await db.commit()
        return True
    
    async def clear_archival_memories(self, user_id: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_tables(db)
            await db.execute("DELETE FROM archival_memories WHERE user_id = ?", (user_id,))
            await db.commit()
        return True
