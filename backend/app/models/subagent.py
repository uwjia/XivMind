from pydantic import BaseModel, Field
from typing import Optional, List


class SubAgentInfo(BaseModel):
    id: str
    name: str
    description: str = ""
    icon: str = "bot"
    skills: List[str] = []
    tools: List[str] = []
    max_turns: int = 10
    temperature: float = 0.7
    model: Optional[str] = None
    provider: Optional[str] = None
    available: bool = True
    source: str = "dynamic"
    file_path: Optional[str] = None
    loaded_at: Optional[str] = None
    language: str = "en"


class SubAgentListResponse(BaseModel):
    agents: List[SubAgentInfo]
    total: int


class SubAgentExecuteRequest(BaseModel):
    instruction: str = Field(..., description="Task instruction for the SubAgent")
    paper_ids: Optional[List[str]] = Field(None, description="List of paper IDs to use as context")
    context: Optional[dict] = Field(None, description="Additional context for the task")
    provider: Optional[str] = Field(None, description="LLM provider to use")
    model: Optional[str] = Field(None, description="Specific model to use")
    max_turns: Optional[int] = Field(None, description="Maximum number of turns")


class SubAgentExecuteResponse(BaseModel):
    task_id: str
    agent_id: str
    status: str
    output: str = ""
    messages: List[dict] = []
    error: Optional[str] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    turns_used: int = 0


class SubAgentCreateRequest(BaseModel):
    id: str = Field(..., description="Unique identifier for the SubAgent")
    name: str = Field(..., description="Display name for the SubAgent")
    description: Optional[str] = Field("", description="Description of the SubAgent")
    skills: Optional[List[str]] = Field(None, description="List of skill IDs the agent can use")
    tools: Optional[List[str]] = Field(None, description="List of tools the agent can use")
    system_prompt: Optional[str] = Field("", description="System prompt for the agent")


class SubAgentSaveRequest(BaseModel):
    content: str = Field(..., description="Raw AGENT.md content")


class SubAgentReloadResponse(BaseModel):
    success: bool = True
    unloaded: int = 0
    loaded: int = 0
    message: Optional[str] = None
