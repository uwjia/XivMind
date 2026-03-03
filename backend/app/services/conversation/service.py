from typing import List, Optional
from app.db.factory import get_conversation_repository
from app.services.conversation.types import ConversationMeta, ConversationCreate, ConversationUpdate, ConversationMessages, ConversationMessage
from app.services.conversation.file_storage import conversation_file_storage


class ConversationService:
    async def create_conversation(self, user_id: str, data: ConversationCreate = None) -> ConversationMeta:
        conversation = ConversationMeta(
            user_id=user_id,
            title=data.title if data and data.title else "New Conversation",
            mode=data.mode if data and data.mode else "search"
        )
        await get_conversation_repository().save_conversation(conversation)
        
        conversation_messages = ConversationMessages(
            session_id=conversation.session_id,
            title=conversation.title
        )
        await conversation_file_storage.save_messages(conversation_messages)
        
        return conversation
    
    async def get_conversations(self, user_id: str = "default", mode: str = None) -> List[ConversationMeta]:
        if mode:
            return await get_conversation_repository().get_conversations_by_mode(user_id, mode)
        return await get_conversation_repository().get_conversations(user_id)
    
    async def get_latest_conversation_by_mode(self, user_id: str, mode: str) -> Optional[ConversationMeta]:
        return await get_conversation_repository().get_latest_conversation_by_mode(user_id, mode)
    
    async def get_conversation_messages(self, session_id: str) -> Optional[ConversationMessages]:
        return await conversation_file_storage.load_messages(session_id)
    
    async def save_conversation_messages(self, data: ConversationMessages) -> bool:
        return await conversation_file_storage.save_messages(data)
    
    async def add_message(self, session_id: str, message: ConversationMessage) -> bool:
        success = await conversation_file_storage.add_message(session_id, message)
        if success:
            conversation = await get_conversation_repository().get_conversation(session_id)
            if conversation:
                conversation.message_count += 1
                
                if conversation.message_count == 1 and message.role == "user":
                    title = message.content[:50] + ("..." if len(message.content) > 50 else "")
                    conversation.title = title
                    await conversation_file_storage.update_title(session_id, title)
                
                await get_conversation_repository().save_conversation(conversation)
        return success
    
    async def update_conversation(self, session_id: str, update: ConversationUpdate) -> Optional[ConversationMeta]:
        conversation = await get_conversation_repository().get_conversation(session_id)
        if not conversation:
            return None
        
        if update.title is not None:
            conversation.title = update.title
            await conversation_file_storage.update_title(session_id, update.title)
        if update.starred is not None:
            conversation.starred = update.starred
        if update.pinned is not None:
            conversation.pinned = update.pinned
        
        await get_conversation_repository().save_conversation(conversation)
        return conversation
    
    async def delete_conversation(self, session_id: str) -> bool:
        success = await get_conversation_repository().delete_conversation(session_id)
        if success:
            await conversation_file_storage.delete_messages(session_id)
        return success
    
    async def search_conversations(self, query: str, user_id: str) -> List[ConversationMeta]:
        return await get_conversation_repository().search_conversations(query, user_id)


conversation_service = ConversationService()
