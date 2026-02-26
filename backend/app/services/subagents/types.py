from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


AGENT_FILE_NAME = "AGENT.md"


class SubAgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SubAgentMessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class SubAgentMessage(BaseModel):
    role: SubAgentMessageRole
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class SubAgentToolCall(BaseModel):
    id: str
    name: str
    arguments: Dict[str, Any]


class SubAgentConfig(BaseModel):
    id: str
    name: str
    description: str = ""
    icon: str = "bot"
    system_prompt: str = ""
    skills: List[str] = []
    tools: List[str] = []
    max_turns: int = 10
    temperature: float = 0.7
    model: Optional[str] = None
    provider: Optional[str] = None
    file_path: Optional[str] = None
    loaded_at: Optional[str] = None
    source: str = "dynamic"
    language: str = "en"  # "en" or "zh"


class SubAgentTask(BaseModel):
    id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S%f"))
    agent_id: str
    instruction: str
    context: Dict[str, Any] = {}
    paper_ids: Optional[List[str]] = None
    max_turns: Optional[int] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class SubAgentResult(BaseModel):
    task_id: str
    agent_id: str
    status: SubAgentStatus
    output: str = ""
    messages: List[SubAgentMessage] = []
    tool_calls: List[SubAgentToolCall] = []
    error: Optional[str] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    turns_used: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class SubAgentExecutionContext(BaseModel):
    agent_id: str
    task_id: str
    messages: List[SubAgentMessage] = []
    variables: Dict[str, Any] = {}
    papers: List[Dict[str, Any]] = []
    current_turn: int = 0
    max_turns: int = 10
    provider: Optional[str] = None
    model: Optional[str] = None
    
    def add_message(self, role: SubAgentMessageRole, content: str, **kwargs):
        self.messages.append(SubAgentMessage(
            role=role,
            content=content,
            **kwargs
        ))
    
    def get_messages_for_llm(self) -> List[Dict[str, str]]:
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in self.messages
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "messages": [msg.model_dump() for msg in self.messages],
            "variables": self.variables,
            "papers": self.papers,
            "current_turn": self.current_turn,
            "max_turns": self.max_turns,
            "provider": self.provider,
            "model": self.model,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SubAgentExecutionContext":
        messages = [
            SubAgentMessage(**msg) for msg in data.get("messages", [])
        ]
        return cls(
            agent_id=data["agent_id"],
            task_id=data["task_id"],
            messages=messages,
            variables=data.get("variables", {}),
            papers=data.get("papers", []),
            current_turn=data.get("current_turn", 0),
            max_turns=data.get("max_turns", 10),
            provider=data.get("provider"),
            model=data.get("model"),
        )
