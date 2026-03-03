import aiosqlite
from datetime import datetime
from typing import Optional, List
from app.db.base import ConversationRepository
from app.services.conversation.types import ConversationMeta
from app.config import get_settings


class SQLiteConversationRepository(ConversationRepository):
    """SQLite implementation for Conversation storage."""
    
    def __init__(self, db_path: str = None):
        self._db_path = db_path
    
    @property
    def db_path(self) -> str:
        if not self._db_path:
            self._db_path = get_settings().SQLITE_DB_PATH
        return self._db_path
    
    async def _ensure_table(self, db):
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversation_meta (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                mode TEXT DEFAULT 'search',
                starred INTEGER DEFAULT 0,
                pinned INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                message_count INTEGER DEFAULT 0
            )
        """)
        await db.commit()
    
    async def get_conversation(self, conversation_id: str) -> Optional[ConversationMeta]:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_table(db)
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM conversation_meta WHERE session_id = ?",
                (conversation_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                return ConversationMeta(
                    session_id=row["session_id"],
                    user_id=row["user_id"],
                    title=row["title"],
                    mode=row["mode"] or "search",
                    starred=bool(row["starred"]),
                    pinned=bool(row["pinned"]) if "pinned" in row.keys() else False,
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.utcnow(),
                    message_count=row["message_count"] or 0,
                )
        return None
    
    async def save_conversation(self, conversation: ConversationMeta) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_table(db)
            conversation.updated_at = datetime.utcnow()
            
            await db.execute("""
                INSERT OR REPLACE INTO conversation_meta 
                (session_id, user_id, title, mode, starred, pinned, created_at, updated_at, message_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conversation.session_id,
                conversation.user_id,
                conversation.title,
                conversation.mode,
                1 if conversation.starred else 0,
                1 if conversation.pinned else 0,
                conversation.created_at.isoformat(),
                conversation.updated_at.isoformat(),
                conversation.message_count,
            ))
            await db.commit()
        return True
    
    async def get_conversations(self, user_id: str, limit: int = 50) -> List[ConversationMeta]:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_table(db)
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM conversation_meta WHERE user_id = ? ORDER BY updated_at DESC LIMIT ?",
                (user_id, limit)
            )
            rows = await cursor.fetchall()
            
            return [
                ConversationMeta(
                    session_id=row["session_id"],
                    user_id=row["user_id"],
                    title=row["title"],
                    mode=row["mode"] or "search",
                    starred=bool(row["starred"]),
                    pinned=bool(row["pinned"]) if "pinned" in row.keys() else False,
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.utcnow(),
                    message_count=row["message_count"] or 0,
                )
                for row in rows
            ]
    
    async def get_conversations_by_mode(self, user_id: str, mode: str, limit: int = 50) -> List[ConversationMeta]:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_table(db)
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM conversation_meta WHERE user_id = ? AND mode = ? ORDER BY updated_at DESC LIMIT ?",
                (user_id, mode, limit)
            )
            rows = await cursor.fetchall()
            
            return [
                ConversationMeta(
                    session_id=row["session_id"],
                    user_id=row["user_id"],
                    title=row["title"],
                    mode=row["mode"] or "search",
                    starred=bool(row["starred"]),
                    pinned=bool(row["pinned"]) if "pinned" in row.keys() else False,
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.utcnow(),
                    message_count=row["message_count"] or 0,
                )
                for row in rows
            ]
    
    async def get_latest_conversation_by_mode(self, user_id: str, mode: str) -> Optional[ConversationMeta]:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_table(db)
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM conversation_meta WHERE user_id = ? AND mode = ? ORDER BY updated_at DESC LIMIT 1",
                (user_id, mode)
            )
            row = await cursor.fetchone()
            
            if row:
                return ConversationMeta(
                    session_id=row["session_id"],
                    user_id=row["user_id"],
                    title=row["title"],
                    mode=row["mode"] or "search",
                    starred=bool(row["starred"]),
                    pinned=bool(row["pinned"]) if "pinned" in row.keys() else False,
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.utcnow(),
                    message_count=row["message_count"] or 0,
                )
        return None
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_table(db)
            await db.execute(
                "DELETE FROM conversation_meta WHERE session_id = ?",
                (conversation_id,)
            )
            await db.commit()
        return True
    
    async def search_conversations(self, query: str, user_id: str) -> List[ConversationMeta]:
        async with aiosqlite.connect(self.db_path) as db:
            await self._ensure_table(db)
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM conversation_meta WHERE user_id = ? AND title LIKE ? ORDER BY updated_at DESC",
                (user_id, f"%{query}%")
            )
            rows = await cursor.fetchall()
            
            return [
                ConversationMeta(
                    session_id=row["session_id"],
                    user_id=row["user_id"],
                    title=row["title"],
                    mode=row["mode"] or "search",
                    starred=bool(row["starred"]),
                    pinned=bool(row["pinned"]) if "pinned" in row.keys() else False,
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.utcnow(),
                    message_count=row["message_count"] or 0,
                )
                for row in rows
            ]
