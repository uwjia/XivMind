import json
import os
from datetime import datetime
from typing import Optional
from app.services.conversation.types import ConversationMessages, ConversationMessage
from app.config import get_settings


class ConversationFileStorage:
    """Local file storage service for storing complete conversation messages"""
    
    def __init__(self):
        self._conversations_dir = None
    
    @property
    def conversations_dir(self) -> str:
        if not self._conversations_dir:
            settings = get_settings()
            self._conversations_dir = os.path.join(
                os.path.dirname(settings.SQLITE_DB_PATH),
                "conversations"
            )
            os.makedirs(self._conversations_dir, exist_ok=True)
        return self._conversations_dir
    
    def _get_file_path(self, session_id: str) -> str:
        return os.path.join(self.conversations_dir, f"{session_id}.json")
    
    async def save_messages(self, data: ConversationMessages) -> bool:
        file_path = self._get_file_path(data.session_id)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data.model_dump(), f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Failed to save conversation messages: {e}")
            return False
    
    async def load_messages(self, session_id: str) -> Optional[ConversationMessages]:
        file_path = self._get_file_path(session_id)
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ConversationMessages(**data)
        except Exception as e:
            print(f"Failed to load conversation messages: {e}")
            return None
    
    async def delete_messages(self, session_id: str) -> bool:
        file_path = self._get_file_path(session_id)
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    
    async def add_message(self, session_id: str, message: ConversationMessage) -> bool:
        data = await self.load_messages(session_id)
        if not data:
            return False
        data.messages.append(message)
        data.updated_at = datetime.utcnow()
        return await self.save_messages(data)
    
    async def update_title(self, session_id: str, title: str) -> bool:
        data = await self.load_messages(session_id)
        if not data:
            return False
        data.title = title
        data.updated_at = datetime.utcnow()
        return await self.save_messages(data)


conversation_file_storage = ConversationFileStorage()
