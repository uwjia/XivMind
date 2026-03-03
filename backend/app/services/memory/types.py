from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class MemoryType(str, Enum):
    CORE = "core"
    RECALL = "recall"
    ARCHIVAL = "archival"


class CoreMemory(BaseModel):
    user_id: str = Field(default="default", description="User identifier")
    research_interests: List[str] = Field(default_factory=list, description="User's research interests")
    preferred_domains: List[str] = Field(default_factory=list, description="Preferred arXiv domains")
    frequently_used_skills: List[str] = Field(default_factory=list, description="Frequently used skills")
    language_preference: str = Field(default="en-US", description="Preferred language for responses")
    summary_style: str = Field(default="detailed", description="Preferred summary style: detailed, brief, bullet_points")
    custom_instructions: str = Field(default="", description="Custom instructions for the assistant")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_context_string(self) -> str:
        parts = []
        if self.research_interests:
            parts.append(f"Research Interests: {', '.join(self.research_interests)}")
        if self.preferred_domains:
            parts.append(f"Preferred Domains: {', '.join(self.preferred_domains)}")
        if self.frequently_used_skills:
            parts.append(f"Frequently Used Skills: {', '.join(self.frequently_used_skills)}")
        parts.append(f"Language Preference: {self.language_preference}")
        parts.append(f"Summary Style: {self.summary_style}")
        if self.custom_instructions:
            parts.append(f"Custom Instructions: {self.custom_instructions}")
        return "\n".join(parts)


class RecallMemory(BaseModel):
    memory_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(default="default", description="User identifier")
    session_id: str = Field(default="", description="Session identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    content: str = Field(description="Conversation content")
    embedding: Optional[List[float]] = Field(default=None, description="Vector embedding")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance score")
    access_count: int = Field(default=0, description="Number of times accessed")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ArchivalMemory(BaseModel):
    memory_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(default="default", description="User identifier")
    content_type: str = Field(default="note", description="Type: note, insight, summary")
    title: str = Field(default="", description="Title of the memory")
    content: str = Field(description="Memory content")
    embedding: Optional[List[float]] = Field(default=None, description="Vector embedding")
    source_papers: List[str] = Field(default_factory=list, description="Related paper IDs")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MemoryExtractionResult(BaseModel):
    user_preferences: List[str] = Field(default_factory=list, description="Extracted user preferences")
    research_interests: List[str] = Field(default_factory=list, description="Extracted research interests")
    important_facts: List[str] = Field(default_factory=list, description="Important facts to remember")
    should_update_core: bool = Field(default=False, description="Whether core memory should be updated")
    importance_score: float = Field(default=0.5, description="Overall importance of this conversation")


class ProcessConversationRequest(BaseModel):
    session_id: str = Field(description="Session identifier")
    user_message: str = Field(description="User's message")
    assistant_message: str = Field(description="Assistant's response")
    extract: bool = Field(default=False, description="Whether to extract profile from conversation")


class CoreMemoryUpdate(BaseModel):
    research_interests: Optional[List[str]] = None
    preferred_domains: Optional[List[str]] = None
    frequently_used_skills: Optional[List[str]] = None
    language_preference: Optional[str] = None
    summary_style: Optional[str] = None
    custom_instructions: Optional[str] = None


class RecallMemoryCreate(BaseModel):
    content: str
    session_id: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    importance_score: float = 0.5


class ArchivalMemoryCreate(BaseModel):
    content_type: str = "note"
    title: str = ""
    content: str
    source_papers: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class MemorySearchRequest(BaseModel):
    query: str
    memory_type: MemoryType = MemoryType.RECALL
    top_k: int = 5


class MemorySearchResult(BaseModel):
    memory_id: str
    content: str
    similarity_score: float
    memory_type: MemoryType
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemoryStats(BaseModel):
    core_memory_exists: bool
    recall_memory_count: int
    archival_memory_count: int
    total_memories: int
    oldest_memory: Optional[datetime] = None
    newest_memory: Optional[datetime] = None
