import logging
from datetime import datetime
from typing import List, Optional

from app.db.base import ConversationRepository
from app.db.lancedb.client import lancedb_client
from app.services.conversation.types import ConversationMeta

logger = logging.getLogger(__name__)


class LanceDBConversationRepository(ConversationRepository):
    """LanceDB implementation for Conversation storage."""
    
    def __init__(self):
        self._table = None
    
    def _get_table(self):
        if self._table is None:
            self._table = lancedb_client.get_table("conversation_meta")
        return self._table
    
    async def get_conversation(self, conversation_id: str) -> Optional[ConversationMeta]:
        table = self._get_table()
        results = table.search().where(f"session_id = '{conversation_id}'").limit(1).to_pandas()
        
        if len(results) == 0:
            return None
        
        row = results.iloc[0]
        return ConversationMeta(
            session_id=row["session_id"],
            user_id=row["user_id"],
            title=row["title"],
            mode=row["mode"] or "search",
            starred=row["starred"],
            pinned=row.get("pinned", False),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.utcnow(),
            message_count=row["message_count"] or 0,
        )
    
    async def save_conversation(self, conversation: ConversationMeta) -> bool:
        table = self._get_table()
        
        table.delete(f"session_id = '{conversation.session_id}'")
        
        record = {
            "session_id": conversation.session_id,
            "user_id": conversation.user_id,
            "title": conversation.title,
            "mode": conversation.mode,
            "starred": conversation.starred,
            "pinned": conversation.pinned,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "message_count": conversation.message_count,
            "embedding": [0.0] * 8,
        }
        
        table.add([record])
        return True
    
    async def get_conversations(self, user_id: str, limit: int = 50) -> List[ConversationMeta]:
        table = self._get_table()
        results = table.search().where(f"user_id = '{user_id}'").limit(limit).to_pandas()
        
        conversations = []
        for _, row in results.iterrows():
            conversations.append(ConversationMeta(
                session_id=row["session_id"],
                user_id=row["user_id"],
                title=row["title"],
                mode=row["mode"] or "search",
                starred=row["starred"],
                pinned=row.get("pinned", False),
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.utcnow(),
                message_count=row["message_count"] or 0,
            ))
        
        return conversations
    
    async def get_conversations_by_mode(self, user_id: str, mode: str, limit: int = 50) -> List[ConversationMeta]:
        table = self._get_table()
        results = table.search().where(f"user_id = '{user_id}'").to_pandas()
        
        if len(results) == 0:
            return []
        
        filtered = results[results["mode"] == mode].head(limit)
        
        conversations = []
        for _, row in filtered.iterrows():
            conversations.append(ConversationMeta(
                session_id=row["session_id"],
                user_id=row["user_id"],
                title=row["title"],
                mode=row["mode"] or "search",
                starred=row["starred"],
                pinned=row.get("pinned", False),
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.utcnow(),
                message_count=row["message_count"] or 0,
            ))
        
        return conversations
    
    async def get_latest_conversation_by_mode(self, user_id: str, mode: str) -> Optional[ConversationMeta]:
        table = self._get_table()
        results = table.search().where(f"user_id = '{user_id}'").to_pandas()
        
        if len(results) == 0:
            return None
        
        filtered = results[results["mode"] == mode]
        
        if len(filtered) == 0:
            return None
        
        sorted_df = filtered.sort_values(by="updated_at", ascending=False)
        row = sorted_df.iloc[0]
        
        return ConversationMeta(
            session_id=row["session_id"],
            user_id=row["user_id"],
            title=row["title"],
            mode=row["mode"] or "search",
            starred=row["starred"],
            pinned=row.get("pinned", False),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.utcnow(),
            message_count=row["message_count"] or 0,
        )
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        table = self._get_table()
        table.delete(f"session_id = '{conversation_id}'")
        return True
    
    async def search_conversations(self, query: str, user_id: str) -> List[ConversationMeta]:
        table = self._get_table()
        results = table.search().where(f"user_id = '{user_id}'").to_pandas()
        
        if len(results) == 0:
            return []
        
        query_lower = query.lower()
        filtered = results[results["title"].str.lower().str.contains(query_lower, na=False)]
        
        conversations = []
        for _, row in filtered.iterrows():
            conversations.append(ConversationMeta(
                session_id=row["session_id"],
                user_id=row["user_id"],
                title=row["title"],
                mode=row["mode"] or "search",
                starred=row["starred"],
                pinned=row.get("pinned", False),
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.utcnow(),
                message_count=row["message_count"] or 0,
            ))
        
        return conversations
