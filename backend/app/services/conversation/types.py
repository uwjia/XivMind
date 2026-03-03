from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field
import uuid


class ConversationMeta(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(default="default")
    title: str = Field(default="New Conversation")
    mode: str = Field(default="search")
    starred: bool = Field(default=False)
    pinned: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = Field(default=0)


class ConversationCreate(BaseModel):
    title: Optional[str] = None
    mode: Optional[str] = None


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    starred: Optional[bool] = None
    pinned: Optional[bool] = None
    mode: Optional[str] = None


class ConversationMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    papers: Optional[List[Any]] = None
    answer: Optional[Any] = None
    references: Optional[List[Any]] = None


class ConversationMessages(BaseModel):
    session_id: str
    title: str = "New Conversation"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    messages: List[ConversationMessage] = Field(default_factory=list)
