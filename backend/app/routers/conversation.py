from fastapi import APIRouter, HTTPException, Query
from app.services.conversation.service import conversation_service
from app.services.conversation.types import ConversationMeta, ConversationCreate, ConversationUpdate, ConversationMessages, ConversationMessage

router = APIRouter(prefix="/conversation", tags=["conversation"])


@router.get("", response_model=list[ConversationMeta])
async def get_conversations(
    user_id: str = Query(default="default"),
    mode: str = Query(default=None),
):
    return await conversation_service.get_conversations(user_id, mode)


@router.get("/latest", response_model=ConversationMeta)
async def get_latest_conversation_by_mode(
    mode: str = Query(...),
    user_id: str = Query(default="default"),
):
    conversation = await conversation_service.get_latest_conversation_by_mode(user_id, mode)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.post("", response_model=ConversationMeta)
async def create_conversation(
    data: ConversationCreate = None,
    user_id: str = Query(default="default"),
):
    return await conversation_service.create_conversation(user_id, data)


@router.get("/search", response_model=list[ConversationMeta])
async def search_conversations(query: str, user_id: str = Query(default="default")):
    return await conversation_service.search_conversations(query, user_id)


@router.get("/{session_id}/messages", response_model=ConversationMessages)
async def get_conversation_messages(session_id: str):
    messages = await conversation_service.get_conversation_messages(session_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Conversation messages not found")
    return messages


@router.post("/{session_id}/messages", response_model=ConversationMessage)
async def add_message(session_id: str, message: ConversationMessage):
    success = await conversation_service.add_message(session_id, message)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add message")
    return message


@router.put("/{session_id}", response_model=ConversationMeta)
async def update_conversation(session_id: str, update: ConversationUpdate):
    result = await conversation_service.update_conversation(session_id, update)
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return result


@router.delete("/{session_id}")
async def delete_conversation(session_id: str):
    success = await conversation_service.delete_conversation(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True}
