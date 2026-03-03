from typing import Optional, List
from datetime import datetime
from pymilvus import Collection

from app.db.base import ConversationRepository
from app.db.milvus.client import milvus_client
from app.services.conversation.types import ConversationMeta


class MilvusConversationRepository(ConversationRepository):
    """Milvus implementation for Conversation storage."""
    
    def __init__(self):
        self._collection: Optional[Collection] = None
    
    def _get_collection(self) -> Collection:
        if not self._collection:
            self._collection = milvus_client.get_collection("conversation_meta")
        return self._collection
    
    async def get_conversation(self, conversation_id: str) -> Optional[ConversationMeta]:
        collection = self._get_collection()
        collection.load()
        
        results = collection.query(
            expr=f'session_id == "{conversation_id}"',
            output_fields=["session_id", "user_id", "title", "mode", "starred", "pinned", "created_at", "updated_at", "message_count"]
        )
        
        if results:
            r = results[0]
            return ConversationMeta(
                session_id=r["session_id"],
                user_id=r["user_id"],
                title=r["title"],
                mode=r["mode"] or "search",
                starred=r["starred"],
                pinned=r.get("pinned", False),
                created_at=datetime.fromisoformat(r["created_at"]) if r["created_at"] else datetime.utcnow(),
                updated_at=datetime.fromisoformat(r["updated_at"]) if r["updated_at"] else datetime.utcnow(),
                message_count=r["message_count"] or 0,
            )
        return None
    
    async def save_conversation(self, conversation: ConversationMeta) -> bool:
        collection = self._get_collection()
        
        data = [
            [conversation.session_id],
            [conversation.user_id],
            [conversation.title],
            [conversation.mode],
            [conversation.starred],
            [conversation.pinned],
            [conversation.created_at.isoformat()],
            [conversation.updated_at.isoformat()],
            [conversation.message_count],
            [[0.0] * 8],
        ]
        
        collection.upsert(data)
        # collection.flush()
        return True
    
    async def get_conversations(self, user_id: str, limit: int = 50) -> List[ConversationMeta]:
        collection = self._get_collection()
        collection.load()
        
        results = collection.query(
            expr=f'user_id == "{user_id}"',
            output_fields=["session_id", "user_id", "title", "mode", "starred", "pinned", "created_at", "updated_at", "message_count"],
            limit=limit
        )
        
        return [
            ConversationMeta(
                session_id=r["session_id"],
                user_id=r["user_id"],
                title=r["title"],
                mode=r["mode"] or "search",
                starred=r["starred"],
                pinned=r.get("pinned", False),
                created_at=datetime.fromisoformat(r["created_at"]) if r["created_at"] else datetime.utcnow(),
                updated_at=datetime.fromisoformat(r["updated_at"]) if r["updated_at"] else datetime.utcnow(),
                message_count=r["message_count"] or 0,
            )
            for r in results
        ]
    
    async def get_conversations_by_mode(self, user_id: str, mode: str, limit: int = 50) -> List[ConversationMeta]:
        collection = self._get_collection()
        collection.load()
        
        results = collection.query(
            expr=f'user_id == "{user_id}" && mode == "{mode}"',
            output_fields=["session_id", "user_id", "title", "mode", "starred", "pinned", "created_at", "updated_at", "message_count"],
            limit=limit
        )
        
        return [
            ConversationMeta(
                session_id=r["session_id"],
                user_id=r["user_id"],
                title=r["title"],
                mode=r["mode"] or "search",
                starred=r["starred"],
                pinned=r.get("pinned", False),
                created_at=datetime.fromisoformat(r["created_at"]) if r["created_at"] else datetime.utcnow(),
                updated_at=datetime.fromisoformat(r["updated_at"]) if r["updated_at"] else datetime.utcnow(),
                message_count=r["message_count"] or 0,
            )
            for r in results
        ]
    
    async def get_latest_conversation_by_mode(self, user_id: str, mode: str) -> Optional[ConversationMeta]:
        collection = self._get_collection()
        collection.load()
        
        results = collection.query(
            expr=f'user_id == "{user_id}" && mode == "{mode}"',
            output_fields=["session_id", "user_id", "title", "mode", "starred", "pinned", "created_at", "updated_at", "message_count"],
            limit=100,
        )
        
        if results:
            results.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
            r = results[0]
            return ConversationMeta(
                session_id=r["session_id"],
                user_id=r["user_id"],
                title=r["title"],
                mode=r["mode"] or "search",
                starred=r["starred"],
                pinned=r.get("pinned", False),
                created_at=datetime.fromisoformat(r["created_at"]) if r["created_at"] else datetime.utcnow(),
                updated_at=datetime.fromisoformat(r["updated_at"]) if r["updated_at"] else datetime.utcnow(),
                message_count=r["message_count"] or 0,
            )
        return None
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        collection = self._get_collection()
        collection.delete(f'session_id == "{conversation_id}"')
        # collection.flush()
        return True
    
    async def search_conversations(self, query: str, user_id: str) -> List[ConversationMeta]:
        collection = self._get_collection()
        collection.load()
        
        results = collection.query(
            expr=f'user_id == "{user_id}"',
            output_fields=["session_id", "user_id", "title", "mode", "starred", "pinned", "created_at", "updated_at", "message_count"],
        )
        
        filtered = [r for r in results if query.lower() in r["title"].lower()]
        
        return [
            ConversationMeta(
                session_id=r["session_id"],
                user_id=r["user_id"],
                title=r["title"],
                mode=r["mode"] or "search",
                starred=r["starred"],
                pinned=r.get("pinned", False),
                created_at=datetime.fromisoformat(r["created_at"]) if r["created_at"] else datetime.utcnow(),
                updated_at=datetime.fromisoformat(r["updated_at"]) if r["updated_at"] else datetime.utcnow(),
                message_count=r["message_count"] or 0,
            )
            for r in filtered
        ]
