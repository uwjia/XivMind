from pydantic import BaseModel, Field
from typing import Optional, List


class AskRequest(BaseModel):
    question: str = Field(..., description="Question to ask about papers")
    top_k: int = Field(5, ge=1, le=20, description="Number of relevant papers to use as context")
    include_references: bool = Field(True, description="Include paper references in response")
    provider: Optional[str] = Field(None, description="LLM provider to use (openai, anthropic, glm, ollama)")
    model: Optional[str] = Field(None, description="Specific model to use")


class PaperReference(BaseModel):
    id: str
    title: str
    authors: List[str] = []
    published: Optional[str] = None
    relevance_score: float = 0.0


class AskResponse(BaseModel):
    answer: str
    references: List[PaperReference] = []
    model: Optional[str] = None
    error: Optional[str] = None


class LLMProviderInfo(BaseModel):
    id: str
    name: str
    models: List[str]
    available: bool
    description: str


class LLMProvidersResponse(BaseModel):
    providers: List[LLMProviderInfo]
    default_provider: Optional[str] = None
